from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os 
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
from src.communicator import *# ==============================
# Run Bot
# ==============================

def start_bot():
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_queue))
    application.add_handler(CommandHandler("view", view_queue))
    application.add_handler(CommandHandler("delete", delete_queue))
    application.add_handler(CommandHandler("end", end_queue))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Startup / shutdown hooks
    application.post_init = on_startup
    application.post_shutdown = on_shutdown

    print("Bot started!")
    print(sendUpdate("Bot started successfully", main= True))
    setup_signal_handlers(application)  
    application.run_polling()


if __name__ == "__main__":
    start_bot()
