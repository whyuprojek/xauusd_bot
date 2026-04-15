from core.tv_conn import get_data_tv
import time

def scan_xauusd():
    """
    Mengambil data market dengan window yang cukup besar untuk analisis 
    Struktur (H4), Konteks (M30), dan Eksekusi (M5).
    """
    try:
        # H4: Kita butuh 200 candle untuk deteksi Major Swing & Parallel Channel
        df_h4 = get_data_tv("XAUUSD", "H4", count=200)
        
        # M30: Kita butuh 150 candle untuk melihat struktur market terdekat
        df_m30 = get_data_tv("XAUUSD", "M30", count=150)
        
        # M5: Kita butuh 150 candle untuk mendeteksi SND valid + cek Touch Count
        df_m5 = get_data_tv("XAUUSD", "M5", count=150)
        
        # Validasi Data: Pastikan semua dataframe terisi dan tidak kosong
        if df_h4 is None or df_h4.empty:
            print("⚠️ Scanner Warning: Data H4 kosong.")
            return None
            
        if df_m30 is None or df_m30.empty:
            print("⚠️ Scanner Warning: Data M30 kosong.")
            return None
            
        if df_m5 is None or df_m5.empty:
            print("⚠️ Scanner Warning: Data M5 kosong.")
            return None

        # Berhasil: Kembalikan data untuk diproses strategy.py
        return df_h4, df_m30, df_m5

    except Exception as e:
        print(f"❌ Scanner Critical Error: {e}")
        return None

def wait_for_market_update(interval=60):
    """Fungsi helper untuk cooldown loop."""
    time.sleep(interval)