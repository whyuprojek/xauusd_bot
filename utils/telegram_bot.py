import os
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

def get_main_menu():
    """Persistent Buttons at the bottom of the screen."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_cek = types.KeyboardButton("🔄 CEK REALTIME")
    btn_set = types.KeyboardButton("⚙️ SET SNR")
    markup.add(btn_cek, btn_set)
    return markup

def send_telegram_msg(text, is_signal=False):
    try:
        bot.send_message(CHAT_ID, text, parse_mode="HTML", reply_markup=get_main_menu())
    except Exception as e:
        print(f"❌ Error Telegram: {e}")