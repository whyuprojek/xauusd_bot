import os
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)


# ===============================
# 🔘 MAIN MENU
# ===============================
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_cek = types.KeyboardButton("🔄 CEK REALTIME")
    btn_set = types.KeyboardButton("⚙️ SET SNR")
    markup.add(btn_cek, btn_set)
    return markup


# ===============================
# 🔥 SEND MESSAGE (UNIFIED)
# ===============================
def send_telegram_msg(text, use_chat_id=True):
    try:
        target = CHAT_ID if use_chat_id else None

        if target:
            bot.send_message(
                target,
                text,
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )
        else:
            print("⚠️ CHAT_ID tidak ditemukan.")
    except Exception as e:
        print(f"❌ Error Telegram: {e}")


# ===============================
# 🔥 SEND PHOTO (CHART)
# ===============================
def send_telegram_photo(photo_path, caption=None):
    try:
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                bot.send_photo(
                    CHAT_ID,
                    photo,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=get_main_menu()
                )
        else:
            print("❌ File chart tidak ditemukan.")
    except Exception as e:
        print(f"❌ Error Kirim Foto: {e}")