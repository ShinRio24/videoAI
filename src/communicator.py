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
task_queue = asyncio.Queue()
stop_flag = False  # signal to stop worker
current_task: str | None = None  # currently processing task


# ------------------------------
# Persistence
# ------------------------------

import signal
import asyncio

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


async def load_queue_from_file():
    """Load queue from file into task_queue."""
    if not os.path.exists(QUEUE_FILE):
        print(f"[QUEUE] No queue file found at {QUEUE_FILE}")
        return

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]

    for t in topics:
        await add_to_queue(t)

    print(f"[QUEUE] Loaded {len(topics)} topics from {QUEUE_FILE}")


# ------------------------------
# Queue Worker
# ------------------------------
async def run_main(title: str):
    result = await asyncio.to_thread(
        subprocess.run, ["python3","-m", "src.main", title],
        capture_output=True, text=True
    )
    print(f"[QUEUE] Finished: {title}")
    print(f"[OUTPUT]\n{result.stdout}")
    if result.stderr:
        print(f"[ERROR]\n{result.stderr}")


async def queue_worker():
    """Always running queue worker."""
    global stop_flag, current_task
    print("[QUEUE] Worker started.")

    while True:
        if stop_flag:
            print("[QUEUE] Stop flag set, exiting worker.")
            break

        current_task = await task_queue.get()
        print(f"[QUEUE] Processing: {current_task}")
        await run_main(current_task)

        task_queue.task_done()
        current_task = None
        save_queue_to_file()

    print("[QUEUE] Worker stopped.")


# ------------------------------
# Queue Management
# ------------------------------
async def add_to_queue(title: str):
    await task_queue.put(title.strip())
    save_queue_to_file()
    print(f"[QUEUE] Added to queue: {title}")
    global stop_flag
    stop_flag=False


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



def stop_queue():
    """Stop the queue worker after current task."""
    global stop_flag
    stop_flag = True
    print("[QUEUE] Stop signal received.")


def get_queue_list():
    """Return a snapshot of current queue items."""
    return list(task_queue._queue)


# ==============================
# Telegram Bot Handlers
# ==============================
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
    title = " ".join(context.args)
    await add_to_queue(title)
    await update.message.reply_text(f"Added to queue: {title}")


async def view_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    queue_list = get_queue_list()
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
    stop_queue()
    await update.message.reply_text("Queue processing will stop after current task.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = update.message.text
    await update.message.reply_text(f"Your chat ID is {chat_id}")
    print(f"[MESSAGE] Chat ID: {chat_id} | Text: {text}")


# ==============================
# Startup / Shutdown
# ==============================
async def on_startup(app: Application):
    print("[QUEUE] Starting worker...")
    app.create_task(queue_worker())
    await load_queue_from_file()


async def on_shutdown(app: Application):
    print("[QUEUE] Shutting down... saving queue to file.")
    save_queue_to_file()


