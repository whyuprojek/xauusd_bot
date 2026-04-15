from core.tv_conn import get_data_tv
import time
import pandas as pd


def remove_unclosed_candle(df, timeframe_minutes):
    """
    Buang candle terakhir kalau belum close (FIX timezone safe)
    """
    if df is None or df.empty:
        return df

    try:
        last_index = df.index[-1]

        # 🔥 FIX TIMEZONE (WAJIB)
        now = pd.Timestamp.now(tz='UTC')

        if last_index.tzinfo is None:
            last_index = last_index.tz_localize('UTC')
        else:
            last_index = last_index.tz_convert('UTC')

        # hitung selisih waktu (menit)
        delta = (now - last_index).total_seconds() / 60

        # kalau candle belum close → buang
        if delta < timeframe_minutes:
            return df.iloc[:-1]

        return df

    except Exception as e:
        print(f"⚠️ Candle validation error: {e}")
        return df


def scan_xauusd():
    """
    Mengambil data market untuk:
    H4 (struktur), M30 (channel), M5 (entry SND)
    """

    try:
        df_h4 = get_data_tv("XAUUSD", "H4", count=200)
        df_m30 = get_data_tv("XAUUSD", "M30", count=150)
        df_m5 = get_data_tv("XAUUSD", "M5", count=150)

        # ===============================
        # VALIDASI DATA
        # ===============================
        if df_h4 is None or df_h4.empty:
            print("⚠️ H4 kosong")
            return None

        if df_m30 is None or df_m30.empty:
            print("⚠️ M30 kosong")
            return None

        if df_m5 is None or df_m5.empty:
            print("⚠️ M5 kosong")
            return None

        # ===============================
        # FIX ORDER DATA
        # ===============================
        df_h4 = df_h4.sort_index()
        df_m30 = df_m30.sort_index()
        df_m5 = df_m5.sort_index()

        # ===============================
        # FIX CANDLE CLOSE (SMART)
        # ===============================
        df_h4 = remove_unclosed_candle(df_h4, 240)  # H4
        df_m30 = remove_unclosed_candle(df_m30, 30)
        df_m5 = remove_unclosed_candle(df_m5, 5)

        return df_h4, df_m30, df_m5

    except Exception as e:
        print(f"❌ Scanner Error: {e}")
        return None


def wait_for_market_update(interval=60):
    time.sleep(interval)