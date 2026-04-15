import time
import os
from core.scanner import scan_xauusd
from core.strategy import analyze_market, get_risk_params, update_manual_snr
from utils.telegram_bot import bot, get_main_menu, send_telegram_msg, send_telegram_photo
from utils.formatter import format_market_output
from utils.visualizer import generate_chart


LAST_ALERT = {
    "snr": None,
    "h4": None,
    "snd": None
}


def check_snr_alert(price, sup, res):
    if sup and abs(price - sup) <= 3:
        return f"⚠️ Harga mendekati SUPPORT {sup}"

    if res and abs(price - res) <= 3:
        return f"⚠️ Harga mendekati RESISTANCE {res}"

    return None


def check_h4_alert(data):
    if data.get("h4_break_up"):
        return f"📊 H4 BREAK VALID ↑ menuju {data.get('next_target')}"

    if data.get("h4_break_down"):
        return f"📊 H4 BREAK VALID ↓ menuju {data.get('next_target')}"

    return None


def check_snd_alert(data):
    setup = data.get("setup")
    if not setup:
        return None

    if setup["type"] == "BUY":
        return f"🔥 SND BUY di Support {data.get('nearest_support')}"
    elif setup["type"] == "SELL":
        return f"🔥 SND SELL di Resistance {data.get('nearest_resistance')}"

    return None


def execute_analysis(chat_id):
    scanner_data = scan_xauusd()

    if scanner_data:
        df_h4, df_m30, df_m5 = scanner_data
        data = analyze_market(df_h4, df_m30, df_m5)
        price = df_m5['close'].iloc[-1]

        output = format_market_output(data, price)

        chart_path = f"chart_{chat_id}.png"

        # 🔥 FIX: kirim TF besar ke visualizer
        generate_chart(df_m5, df_m30, df_h4, data, filename=chart_path)

        if os.path.exists(chart_path):
            send_telegram_photo(chart_path, caption=output)
            os.remove(chart_path)
        else:
            send_telegram_msg(output)

        global LAST_ALERT

        snr_alert = check_snr_alert(price, data.get("nearest_support"), data.get("nearest_resistance"))
        if snr_alert and LAST_ALERT["snr"] != snr_alert:
            send_telegram_msg(snr_alert)
            LAST_ALERT["snr"] = snr_alert

        h4_alert = check_h4_alert(data)
        if h4_alert and LAST_ALERT["h4"] != h4_alert:
            send_telegram_msg(h4_alert)
            LAST_ALERT["h4"] = h4_alert

        snd_alert = check_snd_alert(data)
        if snd_alert and LAST_ALERT["snd"] != snd_alert:
            send_telegram_msg(snd_alert)
            LAST_ALERT["snd"] = snd_alert

    else:
        send_telegram_msg("❌ Gagal mengambil data market.")


@bot.message_handler(func=lambda message: message.text == "🔄 CEK REALTIME")
def btn_cek_market(message):
    send_telegram_msg("🔍 Sedang menganalisa market...")
    execute_analysis(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "⚙️ SET SNR")
def btn_set_snr(message):
    msg = (
        "📥 <b>MODE INPUT SNR MANUAL</b>\n\n"
        "Silakan kirim level dengan format:\n"
        "<code>RES: 2350, 2365 SUP: 2320, 2310</code>"
    )
    send_telegram_msg(msg)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_telegram_msg("🚀 Bot Trading Online. Gunakan tombol di bawah:")


@bot.message_handler(func=lambda message: "RES:" in message.text and "SUP:" in message.text)
def handle_text_snr(message):
    try:
        raw = message.text
        res_part = raw.split('SUP:')[0].replace('RES:', '').strip()
        sup_part = raw.split('SUP:')[1].strip()

        success = update_manual_snr(res_part.split(','), sup_part.split(','))

        if success:
            send_telegram_msg("✅ <b>SNR MANUAL BERHASIL DISIMPAN!</b>")
        else:
            send_telegram_msg("❌ Format salah.")
    except:
        send_telegram_msg("❌ Format salah.")


if __name__ == "__main__":
    print("🤖 Bot Polling Started...")
    bot.infinity_polling()