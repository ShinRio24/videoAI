# runQueue.py + communicator.py integrated

import asyncio
import subprocess
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
from dotenv import load_dotenv

# ==============================
# Setup
# ==============================
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
CHANNEL_ID = -1003034237870
MAINTHREAD_ID =  3
SUBTHREAD_ID = 4
QUEUE_FILE = "topics.txt"

# ==============================
# Queue
# ==============================

skip_flag = False   # global signal to skip the current task
current_proc: asyncio.subprocess.Process | None = None

stop_flag = False  # signal to stop worker
current_task: str | None = None  # currently processing task
task_queue = asyncio.Queue() 
worker_task: asyncio.Task | None = None

# ------------------------------
# Persistence
# ------------------------------

import signal
import asyncio

async def ensure_worker_running(app: Application):
    global worker_task
    if worker_task is None or worker_task.done():
        print("[QUEUE] Worker not running, starting new one...")
        worker_task = app.create_task(queue_worker())

def setup_signal_handlers(application):
    loop = asyncio.get_event_loop()

    def handle_signal(sig, frame):
        print(f"[SYSTEM] Caught signal {sig}, shutting down gracefully...")
        # schedule shutdown
        loop.create_task(on_shutdown(application))
        loop.stop()

    signal.signal(signal.SIGINT, handle_signal)   # Ctrl+C
    signal.signal(signal.SIGTERM, handle_signal)  # kill

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
        await add_to_queue(t, app)

    print(f"[QUEUE] Loaded {len(topics)} topics from {QUEUE_FILE}")


# ------------------------------
# Queue Worker
# ------------------------------

async def skip_current_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global skip_flag
    if current_task:
        skip_flag = True
        await update.message.reply_text(f"Skipping current task: {current_task}")
    else:
        await update.message.reply_text("No task is currently running.")


async def run_main(title: str):
    global current_proc
    print(f"[QUEUE] Starting: {title}", flush=True)

    current_proc = await asyncio.create_subprocess_exec(
        "python3", "-u", "-m", "src.main", title,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    while True:
        try:
            line = await asyncio.wait_for(current_proc.stdout.readline(), timeout=0.5)
            if line:
                print(line.decode().rstrip(), flush=True)
        except asyncio.TimeoutError:
            pass  # check skip_flag periodically

        if skip_flag:
            print(f"[QUEUE] Skipping task: {title}")
            current_proc.kill()
            await current_proc.wait()
            break

    await current_proc.wait()
    current_proc = None
    print(f"[QUEUE] Finished: {title}", flush=True)



async def queue_worker():
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
            break  # exit immediately


        task_queue.task_done()

        current_task = None
        save_queue_to_file()

    print("[QUEUE] Worker stopped.")



# ------------------------------
# Queue Management
# ------------------------------
async def add_to_queue(title: str, app: Application):
    await task_queue.put(title.strip())
    save_queue_to_file()
    print(f"[QUEUE] Added to queue: {title}")
    await ensure_worker_running(app)  



async def delete_from_queue(identifier) -> str:
    queue_list = list(task_queue._queue)

    # Delete by index
    if isinstance(identifier, int):
        if identifier < 1 or identifier > len(queue_list):
            return f"Invalid index: {identifier}. Queue size is {len(queue_list)}."
        removed = queue_list[identifier - 1]
        del task_queue._queue[identifier - 1]

    # Delete by name
    elif isinstance(identifier, str):
        if identifier not in queue_list:
            return f"Task '{identifier}' not found in queue."
        removed = identifier
        queue_list_index = queue_list.index(identifier)
        del task_queue._queue[queue_list_index]

    else:
        return "Invalid identifier type."

    save_queue_to_file()  # persist change
    print(f"[QUEUE] Deleted from queue: {removed}")
    return f"Deleted from queue: {removed}"



import math

async def update_progress(message_id: int, title: str, current: int, total: int):
    """
    Edit a Telegram message to show a progress bar.
    """
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
# Telegram Bot Handlers
# ==============================

async def postToTelegram(video_path: str, caption: str = ""):
    if not os.path.exists(video_path):
        sendUpdate(f"❌ Video file not found: {video_path}", main=True)
        return None

    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    payload = {
        "chat_id": CHANNEL_ID,
        "caption": caption,
        "message_thread_id": MAINTHREAD_ID
    }

    with open(video_path, "rb") as video_file:
        files = {"video": video_file}
        response = requests.post(url, data=payload, files=files)
    
    if response.status_code == 200:
        sendUpdate(f"✅ Video sent to Telegram: {os.path.basename(video_path)}", main=True)
    else:
        sendUpdate(f"❌ Failed to send video: {response.text}", main=True)

    return response.json()


def sendUpdate(message: str, main = False):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    if main:
        payload = {"chat_id": CHANNEL_ID, "text": message, "message_thread_id":MAINTHREAD_ID}
    else:
        payload = {"chat_id": CHANNEL_ID, "text": message, "message_thread_id":SUBTHREAD_ID}
    response = requests.post(url, json=payload)
    return response.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    await update.message.reply_text(f"Your chat ID is {update.message.chat.id}")
    await update.message.reply_text(f"Your thread ID is {update.message.message_thread_id}")


async def add_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a title to queue")
        return
    raw_input = " ".join(context.args)

    titles = [t.strip() for t in raw_input.split(";") if t.strip()]

    for title in titles:
        await add_to_queue(title, context.application)

    if len(titles) == 1:
        await update.message.reply_text(f"Added to queue: {titles[0]}")
    else:
        formatted = "\n".join([f"- {t}" for t in titles])
        await update.message.reply_text(f"Added {len(titles)} tasks to queue:\n{formatted}")



async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all tasks from the queue."""
    # Clear the asyncio queue
    while not task_queue.empty():
        task_queue.get_nowait()
        task_queue.task_done()

    # Clear current task
    global current_task
    current_task = None

    # Persist empty queue to file
    save_queue_to_file()

    await update.message.reply_text("The queue has been cleared.")
    print("[QUEUE] Queue cleared by user command")

async def view_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    queue_list = list(task_queue._queue)
    if not queue_list:
        await update.message.reply_text("The queue is empty")
    else:
        formatted = "\n".join([f"{i+1}. {title}" for i, title in enumerate(queue_list)])
        await update.message.reply_text(f"Current Queue:\n{formatted}")


async def delete_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide the index number or exact task name to delete.\nExample: /delete 2\nOr: /delete My Task Title")
        return

    arg = " ".join(context.args)

    # Try to interpret as an integer index
    if arg.isdigit():
        identifier = int(arg)
    else:
        identifier = arg.strip()

    result = await delete_from_queue(identifier)
    await update.message.reply_text(result)


async def end_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag
    stop_flag = True
    save_queue_to_file() 
    await update.message.reply_text("Queue processing will stop after current task.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = update.message.text
    await update.message.reply_text(f"Your chat ID is {chat_id}")
    print(f"[MESSAGE] Chat ID: {chat_id} | Text: {text}")


# ==============================
# Startup / Shutdown
# ==============================

def cleanLogFile():
    import os
    log_file_path = "tools/output_log.txt"
    MAX_SIZE = 100 * 1024 * 1024  
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > MAX_SIZE:
        os.remove(log_file_path)
        print(f"{log_file_path} exceeded 100MB and was deleted.")
        with open(log_file_path, "w") as f:
            pass


async def on_startup(app: Application):
    cleanLogFile()
    global stop_flag
    stop_flag = False
    print("[QUEUE] Starting worker...")
    await load_queue_from_file(app)
    await ensure_worker_running(app)


async def on_shutdown(app: Application):
    print("[QUEUE] Shutting down... saving queue to file.")
    save_queue_to_file()


