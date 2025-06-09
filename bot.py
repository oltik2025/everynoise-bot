import os
import logging
import random
import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")  # Токен из переменной окружения

logging.basicConfig(level=logging.INFO)

genre_links = []

keyboard = [["?? Рандомный жанр"]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне число от 1 до 6280, и я пришлю Spotify-плейлист этого жанра ??\n"
        "Или нажми кнопку ?? для случайного жанра!",
        reply_markup=markup
    )

def load_genres():
    url = "https://everynoise.com/everynoise1d.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.select("div#scan a")
        logging.info(f"Загружено жанров: {len(links)}")
        return links
    except Exception as e:
        logging.error(f"Ошибка загрузки жанров: {e}")
        return []

def get_spotify_link(index):
    if not genre_links:
        return "Список жанров ещё не загружен."
    try:
        link = genre_links[index - 1]['href']
        genre_url = "https://everynoise.com/" + link
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(genre_url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        spotify = soup.find('a', href=lambda h: h and "spotify.com/playlist" in h)
        if spotify:
            return f"?? Плейлист жанра №{index}:\n{spotify['href']}"
        else:
            return "Плейлист не найден ??"
    except IndexError:
        return "Число вне допустимого диапазона (1–6280)."
    except Exception as e:
        logging.error(f"Ошибка получения плейлиста: {e}")
        return "Произошла ошибка при получении плейлиста."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "рандом" in text.lower() or text == "?? Рандомный жанр":
        index = random.randint(1, len(genre_links))
        link = get_spotify_link(index)
        await update.message.reply_text(link)
        return

    if not text.isdigit():
        await update.message.reply_text("Пожалуйста, отправьте число от 1 до 6280 или нажмите ??.")
        return
    index = int(text)
    if not (1 <= index <= 6280):
        await update.message.reply_text("Число должно быть от 1 до 6280.")
        return

    await update.message.reply_text("? Ищу плейлист...")
    link = get_spotify_link(index)
    await update.message.reply_text(link)

def main():
    global genre_links
    genre_links = load_genres()
    if not genre_links:
        print("Не удалось загрузить список жанров. Попробуйте позже.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()
