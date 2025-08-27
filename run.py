from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os 
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
from src.communicator import *# ==============================
# Run Bot
# ==============================


from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging
import os
import logging

async def log_all(update, context):
    logging.info(f"Received update: {update}")

def start_bot(args):
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_queue))
    application.add_handler(CommandHandler("view", view_queue))
    application.add_handler(CommandHandler("delete", delete_queue))
    application.add_handler(CommandHandler("end", end_queue))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    #edit env section
    # Accept both photos and image documents


    application.add_handler(CommandHandler("clear", clear_queue))
    application.add_handler(CommandHandler("skip", skip_current_task))
    application.add_handler(CommandHandler("env", edit_env))
    application.add_handler(CommandHandler("list", list_env))
    application.add_handler(CommandHandler("frame", frame))
    application.add_handler(MessageHandler(filters.PHOTO | (filters.Document.IMAGE), handle_frame_image))

    application.add_handler(CommandHandler("text", edit_text))
    application.add_handler(CommandHandler("preview", preview_current))
    application.add_handler(CommandHandler("push", push_video))
    






    # Startup / shutdown hooks
    if args.start == "True":
        application.post_init = on_startup
    else:
        application.post_init = on_startupNoStart
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
    start_bot(args)
