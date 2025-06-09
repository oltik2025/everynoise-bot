import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")  # Токен берётся из переменной окружения

logging.basicConfig(level=logging.INFO)

genre_links = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне число от 1 до 6280, и я пришлю Spotify-плейлист этого жанра 🎵")

def load_genres():
    url = "https://everynoise.com/everynoise1d.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.select("div#scan a")

def get_spotify_link(index):
    if not genre_links:
        return "Список жанров ещё не загружен."
    try:
        link = genre_links[index - 1]['href']
        genre_url = "https://everynoise.com/" + link
        r = requests.get(genre_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        spotify = soup.find('a', href=lambda h: h and "spotify.com/playlist" in h)
        return spotify['href'] if spotify else "Плейлист не найден 😢"
    except IndexError:
        return "Число вне допустимого диапазона (1–6280)."
    except Exception as e:
        return f"Произошла ошибка: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Пожалуйста, отправьте **число** от 1 до 6280.")
        return
    index = int(text)
    if not (1 <= index <= 6280):
        await update.message.reply_text("Число должно быть от 1 до 6280.")
        return
    await update.message.reply_text("⏳ Ищу плейлист...")
    link = get_spotify_link(index)
    await update.message.reply_text(link)

def main():
    global genre_links
    genre_links = load_genres()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()

if __name__ == '__main__':
    main()
