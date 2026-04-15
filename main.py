import time
import threading
import os
from core.scanner import scan_xauusd
from core.strategy import analyze_market, get_risk_params, update_manual_snr
from utils.telegram_bot import bot, get_main_menu
from utils.formatter import format_market_output
from utils.visualizer import generate_chart

def execute_analysis(chat_id):
    """Fungsi tunggal untuk eksekusi analisis dan kirim chart."""
    scanner_data = scan_xauusd()
    if scanner_data:
        df_h4, df_m30, df_m5 = scanner_data
        data = analyze_market(df_h4, df_m30, df_m5)
        price = df_m5['close'].iloc[-1]
        output = format_market_output(data, price)
        
        chart_path = f"chart_{chat_id}.png"
        generate_chart(df_m5, data, filename=chart_path)
        
        if os.path.exists(chart_path):
            with open(chart_path, 'rb') as photo:
                bot.send_photo(chat_id, photo, caption=output, parse_mode="HTML", reply_markup=get_main_menu())
            os.remove(chart_path)
        else:
            bot.send_message(chat_id, output, parse_mode="HTML", reply_markup=get_main_menu())
    else:
        bot.send_message(chat_id, "❌ Gagal mengambil data market.", reply_markup=get_main_menu())

# Handler Tombol CEK REALTIME
@bot.message_handler(func=lambda message: message.text == "🔄 CEK REALTIME")
def btn_cek_market(message):
    bot.send_message(message.chat.id, "🔍 Sedang menganalisa market...")
    execute_analysis(message.chat.id)

# Handler Tombol SET SNR
@bot.message_handler(func=lambda message: message.text == "⚙️ SET SNR")
def btn_set_snr(message):
    msg = (
        "📥 <b>MODE INPUT SNR MANUAL</b>\n\n"
        "Silakan kirim level dengan format:\n"
        "<code>RES: 2350, 2365 SUP: 2320, 2310</code>"
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

# Handler Command /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🚀 Bot Trading Online. Gunakan tombol di bawah:", reply_markup=get_main_menu())

# Handler untuk menangkap input teks SNR secara cerdas
@bot.message_handler(func=lambda message: "RES:" in message.text and "SUP:" in message.text)
def handle_text_snr(message):
    try:
        raw = message.text
        res_part = raw.split('SUP:')[0].replace('RES:', '').strip()
        sup_part = raw.split('SUP:')[1].strip()
        
        success = update_manual_snr(res_part.split(','), sup_part.split(','))
        if success:
            bot.reply_to(message, "✅ <b>SNR MANUAL BERHASIL DISIMPAN!</b>\nKlik 🔄 CEK REALTIME untuk melihat hasil.", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ Gagal memproses angka. Pastikan hanya angka dan koma.")
    except:
        bot.reply_to(message, "❌ Format salah. Contoh: RES: 2350,2360 SUP: 2310,2300")

# Loop Monitoring Otomatis (Tetap Berjalan di Background)
def main_loop():
    while True:
        # Logika monitoring otomatis untuk Signal Alert bisa ditaruh di sini
        time.sleep(60)

if __name__ == "__main__":
    # Jalankan Bot Polling
    print("🤖 Bot Polling Started with Persistent Buttons...")
    bot.infinity_polling()