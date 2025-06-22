import os
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7781051082:AAGBThK4JHCUnbU4Ma2T4-hWJMwkW182AUk"
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

YDL_OPTS_VIDEO = {
    'format': 'best[ext=mp4]',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

YDL_OPTS_AUDIO = {
    'format': 'bestaudio[ext=m4a]',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s_audio.%(ext)s'),
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

async def start(update, context):
    await update.message.reply_text("Salom! YouTube, Instagram yoki TikTok havolasini yuboring, men video va MP3 yuboraman.")

async def download_content(update, context):
    url = update.message.text
    chat_id = update.message.chat_id

    try:
        await update.message.reply_text("Yuklanmoqda, biroz kuting...")
        with YoutubeDL(YDL_OPTS_VIDEO) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = os.path.join(DOWNLOAD_DIR, f"{info['id']}.{info['ext']}")
        with YoutubeDL(YDL_OPTS_AUDIO) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = os.path.join(DOWNLOAD_DIR, f"{info['id']}_audio.m4a")
        mp3_file = os.path.join(DOWNLOAD_DIR, f"{info['id']}.mp3")
        video_clip = VideoFileClip(video_file)
        video_clip.audio.write_audiofile(mp3_file)
        video_clip.close()
        with open(video_file, 'rb') as video:
            await context.bot.send_video(chat_id=chat_id, video=video, caption="Mana video!")
        with open(mp3_file, 'rb') as audio:
            await context.bot.send_audio(chat_id=chat_id, audio=audio, caption="Mana MP3!")
        for file in [video_file, audio_file, mp3_file]:
            if os.path.exists(file):
                os.remove(file)
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text(f"Xato yuz berdi: {str(e)}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_content))
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == '__main__':
    main()
