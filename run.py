from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os 
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
from src.communicator import *


def main(args) -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()


    command_map = [
        {"func": command_list, "name": "list", "num": "1"},
        {"func": command_env, "name": "env", "num": "2"},
        {"func": command_etext, "name": "etext", "num": "3"},
        {"func": command_aframe, "name": "aframe", "num": "4"},
        {"func": command_rframe, "name": "rframe", "num": "5"},
        {"func": command_preview, "name": "preview", "num": "6"},
        {"func": command_see, "name": "see", "num": "7"},
        {"func": command_push, "name": "push", "num": "8"},
        {"func": command_pushAll, "name": "pushAll", "num": None},
        {"func": command_deleteEnv, "name": "deleteEnv", "num": "9"},
        {"func": command_view, "name": "view", "num": "10"},
        {"func": command_delete, "name": "delete", "num": "11"},
        {"func": command_skip, "name": "skip", "num": "12"},
        {"func": command_clear, "name": "clear", "num": "13"},
        {"func": command_start, "name": "start", "num": "14"},
        {"func": command_check, "name": "check", "num": "15"},
        {"func": command_help, "name": "help", "num": None},
        {"func": command_q, "name": "q", "num": None},
        {"func": command_eframe, "name": "eframe", "num": None},
        {"func": command_end, "name": "end", "num": None},
        {"func": command_topics, "name": "topics", "num": "16"},
    ]

    # --- Dynamically add all handlers ---
    for cmd in command_map:
        application.add_handler(CommandHandler(cmd["name"], cmd["func"]))
        if cmd["num"]:
            application.add_handler(CommandHandler(cmd["num"], cmd["func"]))


    # --- Message Handler (FIX: This handles image replies) ---
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.Document.IMAGE) & filters.REPLY,
        handle_image_reply
    ))


    # Startup / shutdown hooks
    if args.start == "True":
        application.post_init = on_startup
    else:
        application.post_init = on_startup_no_start
    application.post_shutdown = on_shutdown

    print("Bot started!")
    sendUpdate("Bot started successfully")
    setup_signal_handlers(application)  
    application.run_polling()

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, default="True", help="start program on startup")
    args = parser.parse_args()
    main(args)
