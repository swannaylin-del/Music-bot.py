import os
import yt_dlp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. THE WEB SERVER (Required for Render to stay online)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive! Keeping Render awake."

def run_web_server():
    # Render uses port 8080 by default for free services
    app.run(host='0.0.0.0', port=8080)

# 2. THE BOT LOGIC
# REPLACE THE TOKEN BELOW WITH YOUR ACTUAL TOKEN FROM @BOTFATHER
TOKEN = '8267750642:AAFLbI_EZr4ZaZ32Rt6Z-7Usg4TyXXgkDFA'

def download_music(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch1',
        'outtmpl': 'song.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        filename = ydl.prepare_filename(info).replace(info['ext'], 'mp3')
        return filename, info.get('title', 'Music')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if not query:
        return

    status_msg = await update.message.reply_text(f"🔍 Searching for: {query}...")

    try:
        file_path, title = download_music(query)
        await status_msg.edit_text("📤 Uploading MP3...")
        
        with open(file_path, 'rb') as audio:
            await update.message.reply_audio(audio=audio, title=title)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")

if __name__ == '__main__':
    # Start the web server in a separate thread so it doesn't block the bot
    Thread(target=run_web_server).start()
    
    # Start the Telegram Bot
    print("Bot is starting on Render...")
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    bot_app.run_polling()
