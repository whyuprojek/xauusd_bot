import pandas as pd
import numpy as np

# SINGLE SOURCE OF TRUTH - Memori SNR Manual
MANUAL_STORAGE = {
    "RES": [],
    "SUP": []
}

def update_manual_snr(res_list, sup_list):
    """Menyimpan level murni dari user dan sorting otomatis."""
    global MANUAL_STORAGE
    try:
        MANUAL_STORAGE["RES"] = sorted([float(r.strip()) for r in res_list if r.strip()])
        MANUAL_STORAGE["SUP"] = sorted([float(s.strip()) for s in sup_list if s.strip()], reverse=True)
        return True
    except:
        return False

def get_strict_manual_zones(price_now, buffer=2.0):
    """Konversi price ke zone (Rule: Full Manual Control)."""
    final_res = []
    final_sup = []
    
    # Filter Proximity: Hanya tampilkan yang dalam jangkauan $30
    for r in MANUAL_STORAGE["RES"]:
        if abs(r - price_now) < 30:
            final_res.append({"level": r, "uz": r + buffer, "lz": r - buffer})
            
    for s in MANUAL_STORAGE["SUP"]:
        if abs(s - price_now) < 30:
            final_sup.append({"level": s, "uz": s + buffer, "lz": s - buffer})
            
    return {"RES": final_res, "SUP": final_sup}

def get_refined_snd(df_m5):
    """M5 SND dengan filter Imbalance Explosive."""
    zones = []
    for i in range(len(df_m5) - 5, 20, -1):
        c1, c2, c3 = df_m5.iloc[i-1], df_m5.iloc[i], df_m5.iloc[i+1]
        body_c3 = abs(c3['close'] - c3['open'])
        avg_body = df_m5['close'].diff().abs().rolling(20).mean().iloc[i]
        
        if body_c3 > (avg_body * 1.5):
            is_buy = (c3['close'] > c2['high'])
            is_sell = (c3['close'] < c2['low'])
            
            if is_buy or is_sell:
                uz, lz = c2['high'], c2['low']
                touch = sum(1 for j in range(i+2, len(df_m5)) if df_m5['high'].iloc[j] >= lz and df_m5['low'].iloc[j] <= uz)
                if touch < 3:
                    zones.append({
                        "type": "BUY" if is_buy else "SELL",
                        "uz": uz, "lz": lz, "touch": touch,
                        "strength": "STRONG" if touch == 0 else "VALID"
                    })
    return zones

def analyze_market(df_h4, df_m30, df_m5):
    price_now = df_m5['close'].iloc[-1]
    manual_zones = get_strict_manual_zones(price_now)
    
    # H4 Parallel Channel Context
    h4_high = df_h4['high'].rolling(50).max().iloc[-1]
    h4_low = df_h4['low'].rolling(50).min().iloc[-1]
    pos_pct = (price_now - h4_low) / (h4_high - h4_low) if (h4_high - h4_low) != 0 else 0.5
    h4_pos = "UPPER" if pos_pct > 0.7 else ("LOWER" if pos_pct < 0.3 else "MIDDLE")
    
    all_snd = get_refined_snd(df_m5)
    valid_setups = []

    for snd in all_snd:
        # Check Manual SNR Confluence (Rule 5)
        con_res = any(snd['lz'] <= r['level'] <= snd['uz'] for r in manual_zones['RES'])
        con_sup = any(snd['lz'] <= s['level'] <= snd['uz'] for s in manual_zones['SUP'])
        
        is_valid = False
        score = 40
        
        if snd['type'] == "SELL" and h4_pos == "UPPER" and con_res:
            is_valid, score = True, 75
        if snd['type'] == "BUY" and h4_pos == "LOWER" and con_sup:
            is_valid, score = True, 75
            
        if is_valid:
            valid_setups.append({**snd, "confidence": score, "confluence": True})

    best = sorted(valid_setups, key=lambda x: x['confidence'], reverse=True)[0] if valid_setups else None
    
    # Logic Status
    if not best:
        status, reason = "WAITING", "Menunggu SND menyentuh SNR Manual Anda."
    elif best['lz'] <= price_now <= best['uz']:
        status, reason = "VALID ENTRY", f"Harga di zona {best['type']} + Konfluensi SNR Manual."
    else:
        status, reason = "WAIT RETEST", f"Menunggu retest ke zona {best['type']} ({best['lz']:.2f})."

    return {
        "price": price_now, "h4_pos": h4_pos, "manual_snr": manual_zones,
        "all_snd": all_snd, "best_setup": best, "status": status,
        "reason": reason, "confidence": best['confidence'] if best else 35,
        "bias": "BULLISH" if pos_pct > 0.5 else "BEARISH",
        "signal": best['type'] if status == "VALID ENTRY" else "NONE"
    }

def get_risk_params(signal, entry_price):
    pips = 2.5 if signal == "BUY" else -2.5
    return entry_price - pips, entry_price + (pips * 2.4)