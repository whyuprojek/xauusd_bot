# Jalankan ini di sisi Wine/Windows environment
import rpyc
from mt5linux import MetaTrader5

if __name__ == "__main__":
    # Konfigurasi MT5 di dalam Wine
    mt5 = MetaTrader5()
    # Memulai Server Bridge pada Port 18812
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(mt5, port=18812)
    print("Bridge Server aktif di port 18812...")
    server.start()