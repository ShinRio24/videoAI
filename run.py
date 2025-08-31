from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os 
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
from src.communicator import *


def main(args) -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # --- Command Handlers ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("q", add_queue))
    application.add_handler(CommandHandler("skip", skip_current_task))
    application.add_handler(CommandHandler("view", view_queue))
    application.add_handler(CommandHandler("delete", delete_queue))
    application.add_handler(CommandHandler("clear", clear_queue))
    application.add_handler(CommandHandler("end", end_queue))

    # --- Editing Command Handlers ---

    application.add_handler(CommandHandler("env", edit_env))
    application.add_handler(CommandHandler("list", list_env))
    application.add_handler(CommandHandler("etext", edit_text))
    application.add_handler(CommandHandler("eframe", frame))
    application.add_handler(CommandHandler("rframe", remove_frame))
    application.add_handler(CommandHandler("aframe", add_frame))
    application.add_handler(CommandHandler("preview", preview_current))
    application.add_handler(CommandHandler("see", see_preview))
    application.add_handler(CommandHandler("push", push_video))
    application.add_handler(CommandHandler("deleteEnv", remove_video))


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
    sendUpdate("Bot started successfully", main= True)
    setup_signal_handlers(application)  
    application.run_polling()

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, default="True", help="start program on startup")
    args = parser.parse_args()
    main(args)
