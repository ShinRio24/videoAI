from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM")
CHANNEL_ID = -1003034237870  # replace with your channel ID (must include -100 prefix)





# Function to send a message to the channel
def sendUpdate(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True)
    )
    # Print chat ID and reply with it
    print(f"[START] Chat ID: {update.message.chat.id}")
    await update.message.reply_text(f"Your chat ID is {update.message.chat.id}")

# Handle all text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = update.message.text
    print(f"[MESSAGE] Chat ID: {chat_id} | Text: {text}")
    await update.message.reply_text(f"Your chat ID is {chat_id}")



import threading
def start_bot():
    application = Application.builder().token(TOKEN).build()

        # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("Bot started!")

    # Optional: send a startup message to your channel
    print(sendUpdate("Bot started successfully"))
    # Run the bot
    application.run_polling()

#run actual bot
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()