import asyncio
import httpx
import math
import os
import signal
import subprocess
from dotenv import load_dotenv
import requests

from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from .videoEdit import *

# ==============================
# Setup & Constants
# ==============================
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
CHANNEL_ID = -1003034237870
MAINTHREAD_ID = 3
SUBTHREAD_ID = 4
QUEUE_FILE = "topics.txt"
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
    payload = {
        "chat_id": CHANNEL_ID, 
        "text": message, 
        "message_thread_id": thread_id
    }
    
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

    payload = {"chat_id": CHANNEL_ID, "caption": caption, "message_thread_id": MAINTHREAD_ID}
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
    import requests # Local import to highlight synchronous nature
    progress = current / total
    filled_len = math.floor(progress * 20)
    bar = '█' * filled_len + '-' * (20 - filled_len)
    msg_text = f"Processing '{title}':\n[{bar}] {int(progress*100)}% ({current}/{total})"

    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {
        "chat_id": CHANNEL_ID,
        "message_id": message_id,
        "text": msg_text
    }
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
        "python3", "-u", "-m", "src.main", title,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
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
    print(f"[QUEUE] Subprocess for '{title}' exited with code: {return_code}", flush=True)
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

    print("[QUEUE] Worker stopped.")

# ==============================
# Telegram Handlers: Queue Management
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the queue worker."""
    global stop_flag
    stop_flag = False
    print("[QUEUE] Starting worker...")
    await ensure_worker_running(context.application)
    await update.message.reply_text("Queue processing started.")

async def add_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds one or more tasks to the queue."""
    if not context.args:
        await update.message.reply_text("Please provide a title to queue. You can separate multiple titles with a semicolon ';'.")
        return
    raw_input = " ".join(context.args)
    titles = [t.strip() for t in raw_input.split(";") if t.strip()]

    for title in titles:
        await task_queue.put(title.strip())
    
    save_queue_to_file()
    await ensure_worker_running(context.application)

    if len(titles) == 1:
        await update.message.reply_text(f"Added to queue: {titles[0]}")
    else:
        formatted = "\n".join([f"- {t}" for t in titles])
        await update.message.reply_text(f"Added {len(titles)} tasks to queue:\n{formatted}")

async def view_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the current items in the queue."""
    queue_list = list(task_queue._queue)
    if current_task is None and not queue_list:
        await update.message.reply_text("The queue is empty.")
        return
    
    response = ""
    if current_task:
        response += f"**Currently Processing:**\n- {current_task}\n\n"
    
    if queue_list:
        formatted = "\n".join([f"{i+1}. {title}" for i, title in enumerate(queue_list)])
        response += f"**Upcoming Queue:**\n{formatted}"
    
    await update.message.reply_text(response)

async def delete_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes an item from the queue by index or name."""
    if not context.args:
        await update.message.reply_text("Provide an index or name to delete.\nUsage: /delete 2 OR /delete My Task Title")
        return

    arg = " ".join(context.args)
    identifier = int(arg) if arg.isdigit() else arg.strip()
    
    queue_list = list(task_queue._queue)
    removed_item = None

    if isinstance(identifier, int):
        if 1 <= identifier <= len(queue_list):
            removed_item = queue_list.pop(identifier - 1)
        else:
            await update.message.reply_text(f"Invalid index. Queue has {len(queue_list)} items.")
            return
    else: # string
        if identifier in queue_list:
            queue_list.remove(identifier)
            removed_item = identifier
        else:
            await update.message.reply_text(f"Task '{identifier}' not found in queue.")
            return

    # Rebuild the queue
    while not task_queue.empty():
        task_queue.get_nowait()
    for item in queue_list:
        await task_queue.put(item)

    save_queue_to_file()
    await update.message.reply_text(f"Deleted from queue: {removed_item}")

async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clears all tasks from the queue."""
    while not task_queue.empty():
        task_queue.get_nowait()
        task_queue.task_done()
    
    # Do not clear current_task, as it might be running. Use /skip for that.
    save_queue_to_file()
    await update.message.reply_text("The pending queue has been cleared.")
    print("[QUEUE] Queue cleared by user command.")

async def skip_current_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skips the currently processing task."""
    global skip_flag
    if current_task:
        skip_flag = True
        await update.message.reply_text(f"Signaling to skip current task: {current_task}")
    else:
        await update.message.reply_text("No task is currently running.")

async def end_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stops the worker after the current task is finished."""
    global stop_flag
    stop_flag = True
    save_queue_to_file()
    await update.message.reply_text("Queue processing will stop after the current task completes.")

# ==============================
# Telegram Handlers: Video Editing
# ==============================

async def edit_env(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets the active editing environment for the user."""
    if not context.args:
        await update.message.reply_text("Please provide an env code to edit.")
        return
    
    code_str = context.args[0]
    try:
        response_text = editEnv(code_str) # Assuming this is synchronous
        if "Env set to" in response_text:
            context.user_data['editingEnv'] = int(code_str)
        await update.message.reply_text(response_text)
    except ValueError as e:
        await update.message.reply_text(f"Error: {e}")

async def list_env(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists available editing environments."""
    await update.message.reply_text("\n".join(listEnvs()))

async def edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edits the text of a specific frame."""
    editing_env = context.user_data.get('editingEnv')
    if editing_env is None:
        await update.message.reply_text("❌ No editing environment selected. Use /editenv <code> first.")
        return
    
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /etext <index> <new text>")
        return
    
    index = int(context.args[0])
    new_text = " ".join(context.args[1:])
    result = editText(editing_env, index, new_text)
    await update.message.reply_text(result)

async def frame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the process to change a frame's image."""
    editing_env = context.user_data.get('editingEnv')
    if editing_env is None:
        await update.message.reply_text("❌ No editing environment selected. Use /editenv <code> first.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /frame <index>")
        return

    frame_index = int(context.args[0])
    prompt_msg = await update.message.reply_text(f"📌 Reply to this message with the image for frame {frame_index}.")
    context.user_data['frame_prompt'] = {
        "index": frame_index,
        "prompt_message_id": prompt_msg.message_id,
        "env": editing_env
    }

async def remove_frame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Removes a frame by its index."""
    editing_env = context.user_data.get('editingEnv')
    if editing_env is None:
        await update.message.reply_text("❌ No editing environment selected. Use /editenv <code> first.")
        return
        
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /removeframe <index>")
        return

    frame_index = int(context.args[0])
    result_message = removeFrame(editing_env, frame_index)
    await update.message.reply_text(result_message)

async def add_frame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the process to add a new frame."""
    editing_env = context.user_data.get('editingEnv')
    if editing_env is None:
        await update.message.reply_text("❌ No editing environment selected. Use /editenv <code> first.")
        return

    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /addframe <index> <text for new frame>")
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
        "env": editing_env
    }

async def handle_image_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles image replies for frame editing commands."""
    if not update.message.reply_to_message: return

    # Check for /frame reply
    frame_prompt = context.user_data.get('frame_prompt')
    if frame_prompt and update.message.reply_to_message.message_id == frame_prompt['prompt_message_id']:
        await process_frame_edit(update, context, frame_prompt)
        context.user_data.pop('frame_prompt', None)
        return

    # Check for /addframe reply
    add_frame_prompt = context.user_data.get('add_frame_prompt')
    if add_frame_prompt and update.message.reply_to_message.message_id == add_frame_prompt['prompt_message_id']:
        await process_frame_add(update, context, add_frame_prompt)
        context.user_data.pop('add_frame_prompt', None)
        return

async def preview_current(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates a video preview and replies with it to the original message."""
    editing_env = context.user_data.get('editingEnv')
    if not editing_env:
        await update.message.reply_text("❌ No editing environment selected.")
        return
        
    # Inform the user that the process has started
    status_message = await update.message.reply_text("⏳ Generating preview...")
    
    path = await asyncio.to_thread(previewCurrent, editing_env)
    
    if path and os.path.exists(path):
        try:
            # Open the generated file and send it as a video reply
            with open(path, 'rb') as video_file:
                await update.message.reply_video(video=video_file)
                await update.message.reply_video("preview complete on env:" + str(editing_env))
            
            # Delete the "Generating preview..." message for a cleaner chat
            await status_message.delete()
        except Exception as e:
            # In case of an error during sending, update the status message
            await status_message.edit_text(f"❌ Failed to send preview: {e}")
        finally:
            # Clean up the generated file from the server
            os.remove(path)
    else:
        # If the file wasn't created, edit the status message to inform the user
        await status_message.edit_text("❌ Preview generation failed or file not found.")

async def see_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    editing_env = context.user_data.get('editingEnv')
    if not editing_env:
        await update.message.reply_text("❌ No editing environment selected. Use /editenv first.")
        return

    try:

        path = f"media/editEnvs/{editing_env}/preview.mp4"

        if path and os.path.exists(path):
            await update.message.reply_text("👀 Here is the last generated preview...")
            with open(path, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption=f"Last preview for env: {editing_env}")
        else:
            await update.message.reply_text(
                "🤔 No preview found for the current environment.\n"
                "Please generate one first using the /preview command."
            )
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

async def push_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pushes the final video from the current editing env."""
    editing_env = context.user_data.get('editingEnv')
    if editing_env is None:
        await update.message.reply_text("❌ No editing environment selected.")
        return

    await update.message.reply_text("🚀 Pushing video...")
    result = await asyncio.to_thread(editing_env)
    await update.message.reply_text(result)

async def remove_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pushes the final video from the current editing env."""
    editing_env = context.user_data.get('editingEnv')
    if editing_env is None:
        await update.message.reply_text("❌ No editing environment selected.")
        return

    await update.message.reply_text("🚀 Deleting Env "+str(editing_env))
    result = cleanEnv(editing_env)
    await update.message.reply_text(result)

# ==============================
# Telegram Handlers: General & Debug
# ==============================

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Replies with user, chat, and thread IDs for debugging."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    await update.message.reply_text(f"Your User ID is `{update.effective_user.id}`")
    await update.message.reply_text(f"This Chat ID is `{update.message.chat.id}`")
    if update.message.is_topic_message:
        await update.message.reply_text(f"This Thread ID is `{update.message.message_thread_id}`")

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
        file_ext = os.path.splitext(file.file_path)[1] if hasattr(file, 'file_path') else '.jpg'
        saved_path = prefix+f"{file_ext}"
        await file.download_to_drive(saved_path)

        prefix = os.path.splitext(prefix)[0]

        with Image.open(saved_path) as img:
            # Convert to 'RGB' is crucial for saving as JPG and removing transparency
            rgb_img = img.convert('RGB')
            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(prefix+'.jpg'), exist_ok=True)
            rgb_img.save(prefix+'.jpg', 'jpeg', quality=95)
        return prefix+'.jpg'
    except Exception as e:
        print(f"File download error: {e}")
        return None


async def process_frame_edit(update, context, prompt_data):
    """Helper to process the image reply for the /frame command."""
    file_id = get_file_id_from_message(update.message)
    if not file_id:
        await update.message.reply_text("❌ No valid image found in your reply.")
        return
    
    if  context.user_data.get('editingEnv') is None:
        return "No environment selected"
    
    env = openEnv(context.user_data.get('editingEnv'))
    data = env.videoData
    if prompt_data['index'] >= len(data):
        return "Error, index too large"
    if os.path.exists(data[prompt_data['index']]['path']):
        os.remove(data[prompt_data['index']]['path'])

    saved_path = await download_file(context, file_id, data[prompt_data['index']]['path'])
    if not saved_path:
        await update.message.reply_text("❌ Failed to download image.")
        return
    
    await update.message.reply_text(f"🎬 {saved_path}")

async def process_frame_add(update, context, prompt_data):
    """Helper to process the image reply for the /addframe command."""
    file_id = get_file_id_from_message(update.message)
    if not file_id:
        await update.message.reply_text("❌ No valid image found in your reply.")
        return

    saved_path = await download_file(context, file_id, "add")
    if not saved_path:
        await update.message.reply_text("❌ Failed to download image.")
        return

    result = addFrame(prompt_data['env'], prompt_data['index'], prompt_data['text'], saved_path)
    await update.message.reply_text(f"🎬 {result}")

# ==============================
# Application Startup & Shutdown
# ==============================

def cleanLogFile():
    """Cleans the log file if it exceeds a max size."""
    log_file_path = "tools/output_log.txt"
    MAX_SIZE_MB = 10
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > MAX_SIZE_MB * 1024 * 1024:
        try:
            os.remove(log_file_path)
            print(f"Log file '{log_file_path}' exceeded {MAX_SIZE_MB}MB and was cleared.")
            with open(log_file_path, "w") as f:
                pass # Create an empty file
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
    # The worker task is created but will exit immediately if the queue is empty
    # or stop after one task if `stop_flag` is checked at the start.
    # We call ensure_worker_running to prepare it.
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
    signal.signal(signal.SIGTERM, handle_signal) # kill

