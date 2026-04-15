import pandas as pd
import numpy as np
import json
import os

# ===============================
# 📦 FILE SNR
# ===============================
SNR_FILE = "snr_storage.json"

# ===============================
# 📦 STORAGE SNR (MANUAL)
# ===============================
MANUAL_STORAGE = {
    "RES": [],
    "SUP": []
}

# ===============================
# 🔄 LOAD SNR
# ===============================
def load_snr_from_file():
    global MANUAL_STORAGE

    try:
        if os.path.exists(SNR_FILE):
            with open(SNR_FILE, "r") as f:
                data = json.load(f)

                MANUAL_STORAGE["RES"] = data.get("RES", [])
                MANUAL_STORAGE["SUP"] = data.get("SUP", [])

                print(f"✅ SNR Loaded: {MANUAL_STORAGE}")
        else:
            print("⚠️ File SNR tidak ditemukan")

    except Exception as e:
        print(f"❌ Load SNR error: {e}")


# ===============================
# 💾 SAVE SNR
# ===============================
def update_manual_snr(res_list, sup_list):
    global MANUAL_STORAGE
    try:
        MANUAL_STORAGE["RES"] = sorted([float(r.strip()) for r in res_list if r.strip()])
        MANUAL_STORAGE["SUP"] = sorted([float(s.strip()) for s in sup_list if s.strip()], reverse=True)

        with open(SNR_FILE, "w") as f:
            json.dump(MANUAL_STORAGE, f)

        print(f"✅ SNR Saved: {MANUAL_STORAGE}")

        return True
    except Exception as e:
        print(f"❌ Save SNR error: {e}")
        return False


# ===============================
# 📦 SND DETECTION (RAN STYLE)
# ===============================
def get_ran_snd(df_m5):
    zones = []

    for i in range(len(df_m5) - 3, max(len(df_m5) - 50, 2), -1):
        c1 = df_m5.iloc[i-1]
        c2 = df_m5.iloc[i]
        c3 = df_m5.iloc[i+1]

        c1_green = c1['close'] > c1['open']
        c2_red = c2['close'] < c2['open']
        c2_green = c2['close'] > c2['open']
        c3_green = c3['close'] > c3['open']

        # 🟢 BUY (B-R-B)
        if c1_green and c2_red and c3_green:
            if c3['close'] > c2['high']:
                uz, lz = c2['high'], c2['low']

                touch = sum(
                    1 for j in range(i+2, len(df_m5))
                    if df_m5['high'].iloc[j] >= lz and df_m5['low'].iloc[j] <= uz
                )

                if touch <= 3:
                    zones.append({
                        "type": "BUY",
                        "uz": uz,
                        "lz": lz,
                        "touch": touch,
                        "fresh": touch == 0
                    })

        # 🔴 SELL (R-B-R)
        elif not c1_green and c2_green and not c3_green:
            if c3['close'] < c2['low']:
                uz, lz = c2['high'], c2['low']

                touch = sum(
                    1 for j in range(i+2, len(df_m5))
                    if df_m5['high'].iloc[j] >= lz and df_m5['low'].iloc[j] <= uz
                )

                if touch <= 3:
                    zones.append({
                        "type": "SELL",
                        "uz": uz,
                        "lz": lz,
                        "touch": touch,
                        "fresh": touch == 0
                    })

    return zones


# ===============================
# 📊 MAIN ANALYSIS
# ===============================
def analyze_market(df_h4, df_m30, df_m5):

    # 🔥 LOAD SNR SETIAP ANALISA
    load_snr_from_file()

    price_now = float(df_m5['close'].iloc[-1])

    # ===============================
    # 📊 SNR STRUCTURE
    # ===============================
    all_levels = sorted(list(set(MANUAL_STORAGE["RES"] + MANUAL_STORAGE["SUP"])))

    if not all_levels:
        return {
            "price": price_now,
            "nearest_support": None,
            "nearest_resistance": None,
            "next_target": None,
            "status": "WAIT",
            "m30_pos": "MIDDLE",
            "reason": "SNR belum diset.",
            "setup": None,
            "h4_break_up": False,
            "h4_break_down": False
        }

    below = [l for l in all_levels if l < price_now]
    above = [l for l in all_levels if l > price_now]

    nearest_sup = float(max(below)) if below else None
    nearest_res = float(min(above)) if above else None

    # ===============================
    # 📊 H4 CLOSE VALIDATION (FIXED)
    # ===============================
    last_h4_close = float(df_h4['close'].iloc[-1])
    BREAK_BUFFER = 0.5

    h4_break_up = False
    h4_break_down = False

    if nearest_res is not None:
        h4_break_up = last_h4_close > (nearest_res + BREAK_BUFFER)

    if nearest_sup is not None:
        h4_break_down = last_h4_close < (nearest_sup - BREAK_BUFFER)

    # ===============================
    # 🎯 NEXT TARGET
    # ===============================
    next_target = None

    if h4_break_up and nearest_res:
        next_levels = [l for l in all_levels if l > nearest_res]
        next_target = next_levels[0] if next_levels else None

    elif h4_break_down and nearest_sup:
        next_levels = [l for l in all_levels if l < nearest_sup]
        next_target = next_levels[-1] if next_levels else None

    # ===============================
    # 📏 M30 CHANNEL
    # ===============================
    h30_high = df_m30['high'].rolling(30).max().iloc[-1]
    h30_low = df_m30['low'].rolling(30).min().iloc[-1]
    m30_range = h30_high - h30_low

    if m30_range > 0:
        if price_now > (h30_high - (m30_range * 0.3)):
            m30_pos = "UPPER"
        elif price_now < (h30_low + (m30_range * 0.3)):
            m30_pos = "LOWER"
        else:
            m30_pos = "MIDDLE"
    else:
        m30_pos = "MIDDLE"

    # ===============================
    # 📦 SND
    # ===============================
    all_snd = get_ran_snd(df_m5)

    setup = None
    status = "NO TRADE"
    reason = "Menunggu struktur atau SND valid."

    for snd in all_snd:

        if not snd.get('fresh', True) and snd.get('touch', 0) > 1:
            continue

        dist_to_sup = abs(snd['lz'] - nearest_sup) if nearest_sup else 999
        dist_to_res = abs(snd['uz'] - nearest_res) if nearest_res else 999

        # BUY
        if snd['type'] == "BUY":
            if m30_pos == "UPPER":
                continue

            if dist_to_sup < 2.5:
                setup = snd

                if snd['lz'] <= price_now <= snd['uz']:
                    status = "VALID SETUP"
                    reason = f"BUY di Support {nearest_sup}"
                else:
                    status = "WAIT RETEST"
                    reason = f"Menunggu retest BUY di {nearest_sup}"
                break

        # SELL
        elif snd['type'] == "SELL":
            if m30_pos == "LOWER":
                continue

            if dist_to_res < 2.5:
                setup = snd

                if snd['lz'] <= price_now <= snd['uz']:
                    status = "VALID SETUP"
                    reason = f"SELL di Resistance {nearest_res}"
                else:
                    status = "WAIT RETEST"
                    reason = f"Menunggu retest SELL di {nearest_res}"
                break

    if m30_pos == "MIDDLE" and not setup:
        status = "WAIT"
        reason = "Harga di middle"

    return {
        "price": price_now,
        "nearest_support": nearest_sup,
        "nearest_resistance": nearest_res,
        "next_target": next_target,
        "status": status,
        "m30_pos": m30_pos,
        "reason": reason,
        "setup": setup,
        "h4_break_up": h4_break_up,
        "h4_break_down": h4_break_down
    }


# ===============================
# 💰 RISK MANAGEMENT
# ===============================
def get_risk_params(signal, entry_price):
    pips = 2.5 if signal == "BUY" else -2.5
    sl = entry_price - pips
    tp = entry_price + (pips * 2.0)
    return sl, tp