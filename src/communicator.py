import asyncio
import httpx
import math
import os
import signal
import subprocess
from dotenv import load_dotenv
import requests

from telegram import Update, ForceReply
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from .videoEdit import *

# ==============================
# Setup & Constants
# ==============================
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
CHANNEL_ID = -1003034237870
MAINTHREAD_ID = 3
SUBTHREAD_ID = 4
QUEUE_FILE = "tools/topics.txt"
BUFFER_FOLDER = "media/tempFiles/telegramImages/"
os.makedirs(BUFFER_FOLDER, exist_ok=True)

# ==============================
# Global State & Queue
# ==============================
stop_flag = False
skip_flag = False
current_task: str | None = None
current_proc: asyncio.subprocess.Process | None = None
task_queue = asyncio.Queue()
worker_task: asyncio.Task | None = None

# ==============================
# Async Network Helpers
# ==============================


def sendUpdate(message: str, main=False):
    """Sends a text message to the Telegram channel synchronously."""
    thread_id = MAINTHREAD_ID if main else SUBTHREAD_ID
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": message, "message_thread_id": thread_id}

    try:
        response = requests.post(url, json=payload, timeout=30)

        # This will raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to send update: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the request: {e}")
        return None


async def postToTelegram(video_path: str, caption: str = ""):
    """Uploads a video file to the Telegram channel asynchronously."""
    if not os.path.exists(video_path):
        sendUpdate(f"❌ Video file not found: {video_path}", main=True)
        return None

    payload = {
        "chat_id": CHANNEL_ID,
        "caption": caption,
        "message_thread_id": MAINTHREAD_ID,
    }
    try:
        with open(video_path, "rb") as video_file:
            files = {"video": (os.path.basename(video_path), video_file, "video/mp4")}
            async with httpx.AsyncClient(timeout=120.0) as client:
                url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
                response = await client.post(url, data=payload, files=files)
                response.raise_for_status()
                return response.json()
    except httpx.HTTPStatusError as e:
        sendUpdate(f"❌ Failed to send video: {e.response.text}", main=True)
        return None
    except Exception as e:
        sendUpdate(f"❌ An unexpected error occurred during upload: {e}", main=True)
        return None


# NOTE: This function uses synchronous `requests`.
async def update_progress(message_id: int, title: str, current: int, total: int):
    """Edit a Telegram message to show a progress bar."""
    import requests  # Local import to highlight synchronous nature

    progress = current / total
    filled_len = math.floor(progress * 20)
    bar = "█" * filled_len + "-" * (20 - filled_len)
    msg_text = (
        f"Processing '{title}':\n[{bar}] {int(progress*100)}% ({current}/{total})"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {"chat_id": CHANNEL_ID, "message_id": message_id, "text": msg_text}
    requests.post(url, json=payload)


# ==============================
# Queue Persistence
# ==============================


def save_queue_to_file():
    """Save current task + pending queue to file."""
    queue_list = list(task_queue._queue)
    if current_task:
        queue_list.insert(0, current_task)
    try:
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            for item in queue_list:
                f.write(item + "\n")
        print(f"[QUEUE] Saved {len(queue_list)} items to {QUEUE_FILE}")
    except Exception as e:
        print(f"[QUEUE] Failed to save queue: {e}")


async def load_queue_from_file(app: Application):
    """Load queue from file into task_queue."""
    if not os.path.exists(QUEUE_FILE):
        print(f"[QUEUE] No queue file found at {QUEUE_FILE}")
        return

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]

    for t in topics:
        await task_queue.put(t.strip())

    print(f"[QUEUE] Loaded {len(topics)} topics from {QUEUE_FILE}")



# ==============================
# Queue Worker Logic
# ==============================
async def run_main(title: str):
    """Executes the main video generation script as a subprocess."""
    global current_proc
    print(f"[QUEUE] Starting: {title}", flush=True)

    current_proc = await asyncio.create_subprocess_exec(
        "python3",
        "-u",
        "-m",
        "src.main",
        title,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    while True:
        try:
            # Check for the skip flag before waiting for output
            if skip_flag:
                print(f"[QUEUE] Skipping task: {title}")
                # FIXED: Use .terminate() for a graceful shutdown
                current_proc.terminate()
                # FIXED: Wait for the process to terminate gracefully
                await current_proc.wait()
                # FIXED: Exit the function immediately to avoid errors
                return

            line = await asyncio.wait_for(current_proc.stdout.readline(), timeout=0.5)

            if not line:
                print("[QUEUE] Subprocess finished (EOF detected).")
                break

            print(line.decode().rstrip(), flush=True)

        except asyncio.TimeoutError:
            # This allows the loop to check the skip_flag periodically
            pass

    # This part is now only reached on a normal exit
    return_code = await current_proc.wait()
    print(
        f"[QUEUE] Subprocess for '{title}' exited with code: {return_code}", flush=True
    )
    current_proc = None


async def queue_worker():
    """The main worker loop that processes tasks from the queue."""
    global current_task, skip_flag
    print("[QUEUE] Worker started.")

    while True:
        if stop_flag:
            print("[QUEUE] Stopping worker due to stop_flag.")
            sendUpdate("Queue processing stopped.", main=True)
            break

        current_task = await task_queue.get()
        skip_flag = False
        print(f"[QUEUE] Processing: {current_task}")
        try:
            await run_main(current_task)
        except asyncio.CancelledError:
            print(f"[QUEUE] Current task {current_task} cancelled")
            break  # Exit immediately

        task_queue.task_done()
        current_task = None
        save_queue_to_file()

        print("[QUEUE] Task finished, starting 10-second cooldown...")
        await asyncio.sleep(10)

    print("[QUEUE] Worker stopped.")


# ==============================
# Telegram Handlers: Queue Management
# ==============================
import traceback
async def command_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generates a list of 10 influential people based on a user-provided idea.
    """
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Please provide an idea for the topics. \nExample: `/gentopics 日本の歴史`",
            message_thread_id=update.effective_message.message_thread_id,
        )
        return

    idea = " ".join(context.args)

    try:
        topics = await asyncio.to_thread(genTopics, idea)

        if not topics:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Sorry, I couldn't generate any topics for that idea. The response might have been empty.",
                message_thread_id=update.effective_message.message_thread_id,
            )
            return

        formatted_list = [f"{i+1}. {topic}" for i, topic in enumerate(topics)]
        response_text = f"✨ *Here are 10 topic ideas for \"{idea}\":*\n\n" + "\n".join(formatted_list)

        # 5. Send the final list back to the user
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response_text,
            message_thread_id=update.effective_message.message_thread_id,
        )

    except Exception as e:
        print(f"An error occurred in command_topics: {e}")
        error_traceback = traceback.format_exc()
        print(error_traceback)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ An unexpected error occurred. Please check the logs.",
            message_thread_id=update.effective_message.message_thread_id,
        )

async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the queue worker."""
    global stop_flag
    stop_flag = False
    print("[QUEUE] Starting worker...")
    await ensure_worker_running(context.application)
    await context.bot.send_message(
        text="Queue processing started.",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


async def command_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds one or more tasks to the queue."""
    if not context.args:
        await context.bot.send_message(
            text="Please provide a title to queue. You can separate multiple titles with a semicolon ';'.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return
    raw_input = " ".join(context.args)
    titles = [t.strip() for t in raw_input.split(";") if t.strip()]

    for title in titles:
        await task_queue.put(title.strip())

    save_queue_to_file()
    await ensure_worker_running(context.application)

    if len(titles) == 1:
        await context.bot.send_message(
            text=f"Added to queue: {titles[0]}",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
    else:
        formatted = "\n".join([f"- {t}" for t in titles])
        await context.bot.send_message(
            text=f"Added {len(titles)} tasks to queue:\n{formatted}",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )


async def command_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the current items in the queue."""
    queue_list = list(task_queue._queue)
    if current_task is None and not queue_list:
        await context.bot.send_message(
            text="The queue is empty.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    response = ""
    if current_task:
        response += f"**Currently Processing:**\n- {current_task}\n\n"

    if queue_list:
        formatted = "\n".join([f"{i+1}. {title}" for i, title in enumerate(queue_list)])
        response += f"**Upcoming Queue:**\n{formatted}"

    await context.bot.send_message(
        text=response,
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


async def command_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes an item from the queue by index or name."""
    if not context.args:
        await context.bot.send_message(
            text="Provide an index or name to delete.\nUsage: /delete 2 OR /delete My Task Title",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    arg = " ".join(context.args)
    identifier = int(arg) if arg.isdigit() else arg.strip()

    queue_list = list(task_queue._queue)
    removed_item = None

    if isinstance(identifier, int):
        if 1 <= identifier <= len(queue_list):
            removed_item = queue_list.pop(identifier - 1)
        else:
            await context.bot.send_message(
                text=f"Invalid index. Queue has {len(queue_list)} items.",
                chat_id=update.effective_chat.id,
                message_thread_id=update.effective_message.message_thread_id,
                disable_notification=True,
            )
            return
    else:  # string
        if identifier in queue_list:
            queue_list.remove(identifier)
            removed_item = identifier
        else:
            await context.bot.send_message(
                text=f"Task '{identifier}' not found in queue.",
                chat_id=update.effective_chat.id,
                message_thread_id=update.effective_message.message_thread_id,
                disable_notification=True,
            )
            return

    # Rebuild the queue
    while not task_queue.empty():
        task_queue.get_nowait()
    for item in queue_list:
        await task_queue.put(item)

    save_queue_to_file()
    await context.bot.send_message(
        text=f"Deleted from queue: {removed_item}",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


async def command_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clears all tasks from the queue."""
    while not task_queue.empty():
        task_queue.get_nowait()
        task_queue.task_done()

    # Do not clear current_task, as it might be running. Use /skip for that.
    save_queue_to_file()
    await context.bot.send_message(
        text="The pending queue has been cleared.",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
    print("[QUEUE] Queue cleared by user command.")


async def command_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skips the currently processing task."""
    global skip_flag
    if current_task:
        skip_flag = True
        await context.bot.send_message(
            text=f"Signaling to skip current task: {current_task}",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
    else:
        await context.bot.send_message(
            text="No task is currently running.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )


async def command_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stops the worker after the current task is finished."""
    global stop_flag
    stop_flag = True
    save_queue_to_file()
    await context.bot.send_message(
        text="Queue processing will stop after the current task completes.",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


# ==============================
# Telegram Handlers: Video Editing
# ==============================
editingTaskQueue = asyncio.Queue()


async def _task_runner(task, params, update, context):
    print(f"   Running task '{task.__name__}' in a thread...")
    # Run the blocking task in a separate thread
    result = await asyncio.to_thread(task, *params)
    print(f"   Task '{task.__name__}' thread finished. Sending reply...")

    if task == previewCurrent:
        try:
            with open(result, "rb") as video_file:

                await context.bot.send_video(
                    video = open(video_file, 'rb'),
                    chat_id=update.effective_chat.id,
                    message_thread_id=update.effective_message.message_thread_id,
                    disable_notification=True
                )

                await context.bot.send_message(
                    text="Preview complete on env: "
                    + str(context.user_data.get("editingEnv")),
                        chat_id=update.effective_chat.id,
                        message_thread_id=update.effective_message.message_thread_id,
                        disable_notification=True,
                )
                

        except Exception as e:
            await context.bot.send_message(
                text=f"Error sending video: {e}",
                chat_id=update.effective_chat.id,
                message_thread_id=update.effective_message.message_thread_id,
                disable_notification=True,
            )
    else:
        await context.bot.send_message(
            text=result,
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )


async def queue_worker_editing():
    print("Queue worker started (Editing Task). Waiting for tasks...")
    while True:
        # 2. Wait until a task is available in the queue
        task, params, update, context = await editingTaskQueue.get()

        try:
            # 3. Run the task. The worker will wait here until _task_runner is complete
            # before fetching the next item from the queue.
            await _task_runner(task, params, update, context)
        except Exception as e:
            # Basic error handling to prevent the worker from crashing.
            print(
                f"ERROR: An exception occurred while processing task '{task.__name__}': {e}"
            )
            try:
                # Try to notify the user about the failure
                await context.bot.send_message(
                    text=f"An error occurred processing your request: {e}",
                    chat_id=update.effective_chat.id,
                    message_thread_id=update.effective_message.message_thread_id,
                    disable_notification=True,
                )
            except Exception as notify_error:
                print(
                    f"ERROR: Could not notify user about the task failure: {notify_error}"
                )
        finally:
            # Mark the task as done. This is important for queue management.
            editingTaskQueue.task_done()
            print(
                f"--- Task '{task.__name__}' complete. Queue size: {editingTaskQueue.qsize()}. ---"
            )


def createTask(task, params, update, context):
    """
    This function now acts as a producer, quickly adding tasks to the queue.
    It no longer creates an asyncio.Task directly, upholding the "fire and forget" aspect.
    """
    print(f"   Queuing task: {task.__name__}")
    task_details = (task, params, update, context)
    editingTaskQueue.put_nowait(task_details)


async def command_env(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets the active editing environment for the user."""
    if not context.args:
        await context.bot.send_message(
            text="Please provide an env code to edit.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    code_str = context.args[0]
    try:
        response_text = editEnv(code_str)  # Assuming this is synchronous
        if "Env set to" in response_text:
            context.user_data["editingEnv"] = int(code_str)
        await context.bot.send_message(
            text=response_text,
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        await command_see(update, context)
    except ValueError as e:
        await context.bot.send_message(
            text=f"Error: {e}",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )


async def command_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists available editing environments."""
    await context.bot.send_message(
        text="\n".join(listEnvs()),
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


async def command_etext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edits the text of a specific frame."""
    editing_env = context.user_data.get("editingEnv")
    if editing_env is None:
        await context.bot.send_message(
            text="❌ No editing environment selected. Use /editenv <code> first.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    if len(context.args) < 2 or not context.args[0].isdigit():
        await context.bot.send_message(
            text="Usage: /etext <index> <new text>",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    index = int(context.args[0])
    new_text = " ".join(context.args[1:])
    result = editText(editing_env, index, new_text)
    await context.bot.send_message(
        text=result,
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


async def command_eframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the process to change a frame's image."""
    editing_env = context.user_data.get("editingEnv")
    if editing_env is None:
        await context.bot.send_message(
            text="❌ No editing environment selected. Use /editenv <code> first.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    if not context.args or not context.args[0].isdigit():
        await context.bot.send_message(
            text="Usage: /frame <index>",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    frame_index = int(context.args[0])
    prompt_msg = await context.bot.send_message(
        text=f"📌 Reply to this message with the image for frame {frame_index}.",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
    context.user_data["frame_prompt"] = {
        "index": frame_index,
        "prompt_message_id": prompt_msg.message_id,
        "env": editing_env,
    }


async def command_rframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Removes a frame by its index."""
    editing_env = context.user_data.get("editingEnv")
    if editing_env is None:
        await context.bot.send_message(
            text="❌ No editing environment selected. Use /editenv <code> first.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    if not context.args or not context.args[0].isdigit():
        await context.bot.send_message(
            text="Usage: /removeframe <index>",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    frame_index = int(context.args[0])
    result_message = removeFrame(editing_env, frame_index)
    await context.bot.send_message(
        text=result_message,
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


async def command_aframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the process to add a new frame."""
    editing_env = context.user_data.get("editingEnv")
    if editing_env is None:
        await context.bot.send_message(
            text="❌ No editing environment selected. Use /editenv <code> first.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    if len(context.args) < 2 or not context.args[0].isdigit():
        await context.bot.send_message(
            text="Usage: /addframe <index> <text for new frame>",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    frame_index = int(context.args[0])
    new_text = " ".join(context.args[1:])
    prompt_msg = await update.message.reply_text(
        f"✅ Text for new frame {frame_index} is set.\n\n"
        f"**Now, reply to this message with the image.**"
    )
    context.user_data["add_frame_prompt"] = {
        "index": frame_index,
        "text": new_text,
        "prompt_message_id": prompt_msg.message_id,
        "env": editing_env,
    }


async def handle_image_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles image replies for frame editing commands."""
    if not update.message.reply_to_message:
        return

    # Check for /frame reply
    frame_prompt = context.user_data.get("frame_prompt")
    if (
        frame_prompt
        and update.message.reply_to_message.message_id
        == frame_prompt["prompt_message_id"]
    ):
        await process_frame_edit(update, context, frame_prompt)
        context.user_data.pop("frame_prompt", None)
        return

    # Check for /addframe reply
    add_frame_prompt = context.user_data.get("add_frame_prompt")
    if (
        add_frame_prompt
        and update.message.reply_to_message.message_id
        == add_frame_prompt["prompt_message_id"]
    ):
        await process_frame_add(update, context, add_frame_prompt)
        context.user_data.pop("add_frame_prompt", None)
        return


async def command_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates a video preview and replies with it to the original message."""
    editing_env = context.user_data.get("editingEnv")
    if not editing_env:
        await context.bot.send_message(
            text="❌ No editing environment selected.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    await context.bot.send_message(
        text="⏳ Generating preview...",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
    createTask(previewCurrent, [editing_env], update, context)


async def command_see(update: Update, context: ContextTypes.DEFAULT_TYPE):
    editing_env = context.user_data.get("editingEnv")
    if not editing_env:
        await context.bot.send_message(
            text="❌ No editing environment selected. Use /editenv first.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    try:

        path = f"media/editEnvs/{editing_env}/preview.mp4"

        if path and os.path.exists(path):
            await context.bot.send_message(
                text="👀 Here is the last generated preview...",
                chat_id=update.effective_chat.id,
                message_thread_id=update.effective_message.message_thread_id,
                disable_notification=True,
            )
            await context.bot.send_video(
                video = open(path, 'rb'),
                chat_id=update.effective_chat.id,
                message_thread_id=update.effective_message.message_thread_id,
                disable_notification=True,
                )
        else:
            await update.message.reply_text(
                "🤔 No preview found for the current environment.\n"
                "Please generate one first using the /preview command."
            )
    except Exception as e:
        await context.bot.send_message(
            text=f"An error occurred: {e}",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )


async def command_push(update: Update, context: ContextTypes.DEFAULT_TYPE):
    editing_env = context.user_data.get("editingEnv")
    if editing_env is None:
        await context.bot.send_message(
            text="❌ No editing environment selected.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    await context.bot.send_message(
        text="🚀 Pushing video...",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
    context.user_data["editingEnv"] = None
    createTask(pushVideo, [editing_env], update, context)

async def command_pushAll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_env_codes = listEnvsRaw()
    if not all_env_codes:
        await context.bot.send_message(
            text="ℹ️ No environments found to push.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    for env_code in all_env_codes:
        createTask(pushVideo, [env_code], update, context)

    await context.bot.send_message(
        text=f"✅ All environments ({len(all_env_codes)}) have been successfully added to the queue.",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )

async def command_deleteEnv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pushes the final video from the current editing env."""
    if not context.args or not context.args[0].isdigit():
        await context.bot.send_message(
            text="Please provide an env code to edit.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    code_str = int(context.args[0])

    await context.bot.send_message(
        text="🚀 Deleting Env " + str(code_str),
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
    result = removeEnv(code_str)
    await context.bot.send_message(
        text=result,
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


# ==============================
# Telegram Handlers: General & Debug
# ==============================


async def command_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Replies with user, chat, and thread IDs for debugging."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    await context.bot.send_message(
        text=f"Your User ID is `{update.effective_user.id}`",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
    await context.bot.send_message(
        text=f"This Chat ID is `{update.message.chat.id}`",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
    if update.message.is_topic_message:
        await context.bot.send_message(
            text=f"This Thread ID is `{update.message.message_thread_id}`",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generic message handler for debugging."""
    chat_id = update.message.chat.id
    text = update.message.text
    print(f"[MESSAGE] Chat ID: {chat_id} | Text: {text}")


# ==============================
# Helper & Utility Functions
# ==============================


async def ensure_worker_running(app: Application):
    """Starts the queue worker if it's not already running."""
    global worker_task
    if worker_task is None or worker_task.done():
        print("[QUEUE] Worker not running, starting new one...")
        worker_task = app.create_task(queue_worker())
    worker = asyncio.create_task(queue_worker_editing())


def get_file_id_from_message(message):
    """Extracts file_id from a photo or document."""
    if message.photo:
        return message.photo[-1].file_id
    if message.document and message.document.mime_type.startswith("image/"):
        return message.document.file_id
    return None


from PIL import Image


async def download_file(context, file_id, prefix):
    """Downloads a file from Telegram and saves it to the buffer folder."""
    try:
        file = await context.bot.get_file(file_id)
        file_ext = (
            os.path.splitext(file.file_path)[1]
            if hasattr(file, "file_path")
            else ".jpg"
        )
        saved_path = prefix + f"{file_ext}"
        await file.download_to_drive(saved_path)

        prefix = os.path.splitext(prefix)[0]

        with Image.open(saved_path) as img:
            # Convert to 'RGB' is crucial for saving as JPG and removing transparency
            rgb_img = img.convert("RGB")
            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(prefix + ".jpg"), exist_ok=True)
            rgb_img.save(prefix + ".jpg", "jpeg", quality=95)
        return prefix + ".jpg"
    except Exception as e:
        print(f"File download error: {e}")
        return None


async def process_frame_edit(update, context, prompt_data):
    """Helper to process the image reply for the /frame command."""
    file_id = get_file_id_from_message(update.message)
    if not file_id:
        await context.bot.send_message(
            text="❌ No valid image found in your reply.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    if context.user_data.get("editingEnv") is None:
        return "No environment selected"

    env = openEnv(context.user_data.get("editingEnv"))
    data = env.videoData
    if prompt_data["index"] >= len(data):
        return "Error, index too large"
    if os.path.exists(data[prompt_data["index"]]["path"]):
        os.remove(data[prompt_data["index"]]["path"])

    saved_path = await download_file(
        context, file_id, data[prompt_data["index"]]["path"]
    )
    if not saved_path:
        await context.bot.send_message(
            text="❌ Failed to download image.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    await context.bot.send_message(
        text=f"🎬 {saved_path}",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


from datetime import datetime


async def process_frame_add(update, context, prompt_data):
    """Helper to process the image reply for the /addframe command."""
    file_id = get_file_id_from_message(update.message)
    if not file_id or file_id == "":
        await context.bot.send_message(
            text="❌ No valid image found in your reply.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    editing_env = prompt_data["env"]
    env_directory = f"media/editEnvs/{editing_env}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    unique_filename_prefix = f"frame_{timestamp}"
    full_path_prefix = os.path.join(env_directory, unique_filename_prefix)

    saved_path = await download_file(context, file_id, full_path_prefix)
    if not saved_path:
        await context.bot.send_message(
            text="❌ Failed to download image.",
            chat_id=update.effective_chat.id,
            message_thread_id=update.effective_message.message_thread_id,
            disable_notification=True,
        )
        return

    result = addFrame(
        prompt_data["env"], prompt_data["index"], prompt_data["text"], saved_path
    )
    await context.bot.send_message(
        text=f"🎬 {result}",
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )


# ==============================
# Application Startup & Shutdown
# ==============================


def cleanLogFile():
    """Cleans the log file if it exceeds a max size."""
    log_file_path = "tools/output_log.txt"
    MAX_SIZE_MB = 10
    if (
        os.path.exists(log_file_path)
        and os.path.getsize(log_file_path) > MAX_SIZE_MB * 1024 * 1024
    ):
        try:
            os.remove(log_file_path)
            print(
                f"Log file '{log_file_path}' exceeded {MAX_SIZE_MB}MB and was cleared."
            )
            with open(log_file_path, "w") as f:
                pass  # Create an empty file
        except OSError as e:
            print(f"Error cleaning log file: {e}")


async def on_startup(app: Application):
    """Actions to perform on bot startup."""
    cleanLogFile()
    global stop_flag
    stop_flag = False
    print("[SYSTEM] Application starting...")
    await load_queue_from_file(app)
    await ensure_worker_running(app)


async def on_startup_no_start(app: Application):
    """Startup routine that loads the queue but does not start the worker."""
    cleanLogFile()
    global stop_flag
    stop_flag = True
    print("[SYSTEM] Application starting, worker initially paused...")
    await load_queue_from_file(app)
    await ensure_worker_running(app)


async def on_shutdown(app: Application):
    """Actions to perform on bot shutdown."""
    print("[SYSTEM] Shutting down... saving queue to file.")
    save_queue_to_file()
    if worker_task and not worker_task.done():
        worker_task.cancel()


def setup_signal_handlers(application):
    """Sets up graceful shutdown on SIGINT and SIGTERM."""
    loop = asyncio.get_event_loop()

    def handle_signal(sig, frame):
        print(f"[SYSTEM] Caught signal {sig}, shutting down gracefully...")
        loop.create_task(on_shutdown(application))
        loop.stop()

    signal.signal(signal.SIGINT, handle_signal)  # Ctrl+C
    signal.signal(signal.SIGTERM, handle_signal)  # kill


async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a clear, numbered, and copy-paste friendly guide of all commands."""
    help_text = """
*Video Editing Commands* 🎬

1. `/list` (or `/1`)
   ► Lists all saved video projects.

2. `/env <id>` (or `/2 <id>`)
   ► Selects a project to edit by its ID.

3. `/etext <index> <new text>` (or `/3 <index> <new text>`)
   ► Changes the text for a specific frame.

4. `/aframe <index> <text>` (or `/4 <index> <text>`)
   ► Adds a new frame. (Remember to attach an image).

5. `/rframe <index>` (or `/5 <index>`)
   ► Removes a specific frame from the project.

6. `/preview` (or `/6`)
   ► Creates a preview video of the selected project.

7. `/see` (or `/7`)
   ► Shows you the latest preview video.

8. `/push` (or `/8`)
   ► Uploads the final video and deletes the project.

   `/pushAll`
   ► Uploads the final video and deletes the projects.

9. `/deleteEnv <id>` (or `/9 <id>`)
   ► Permanently deletes a video project by its ID.


*Task Queue Commands* ⚙️

10. `/view` (or `/10`)
    ► Shows all tasks waiting in the queue.

11. `/delete <index>` (or `/11 <index>`)
    ► Removes a specific task from the queue.

12. `/skip` (or `/12`)
    ► Skips the task that is currently running.

13. `/clear` (or `/13`)
    ► WARNING: Removes ALL tasks from the queue.

14. `/start` (or `/14`)
    ► Starts the bot.

15. `/check` (or `/15`)
    ► Checks if the bot is running.
"""
    await context.bot.send_message(
        text=help_text,
        chat_id=update.effective_chat.id,
        message_thread_id=update.effective_message.message_thread_id,
        disable_notification=True,
    )
