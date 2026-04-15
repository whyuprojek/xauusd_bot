from tvDatafeed import TvDatafeed, Interval
import pandas as pd

# Inisialisasi global
tv = TvDatafeed()

def get_data_tv(symbol, interval_str, count=100):
    intervals = {
        "M1": Interval.in_1_minute,
        "M5": Interval.in_5_minute,
        "M30": Interval.in_30_minute,
        "H4": Interval.in_4_hour
    }
    
    try:
        # Re-init sesekali jika data macet (Force Refresh)
        df = tv.get_hist(symbol=symbol, exchange='OANDA', interval=intervals[interval_str], n_bars=count)
        
        if df is None or df.empty:
            return pd.DataFrame()
            
        return df
    except Exception as e:
        print(f"❌ Error Fetching {interval_str}: {e}")
        return pd.DataFrame()