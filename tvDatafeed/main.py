import datetime
import enum
import json
import logging
import os
import pickle
import random
import re
import shutil
import string
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # Update Baru
from websocket import create_connection
import sys

logger = logging.getLogger(__name__)

class Interval(enum.Enum):
    in_1_minute = "1"
    in_3_minute = "3"
    in_5_minute = "5"
    in_15_minute = "15"
    in_30_minute = "30"
    in_45_minute = "45"
    in_1_hour = "1H"
    in_2_hour = "2H"
    in_3_hour = "3H"
    in_4_hour = "4H"
    in_6_hour = "6H"
    in_8_hour = "8H"
    in_12_hour = "12H"
    in_daily = "1D"
    in_weekly = "1W"
    in_monthly = "1M"

class TvDatafeed:
    path = os.path.join(os.path.expanduser("~"), ".tv_datafeed/")
    headers = json.dumps({"Origin": "https://data.tradingview.com"})

    def __save_token(self, token):
        tokenfile = os.path.join(self.path, "token")
        contents = dict(
            token=token,
            date=self.token_date,
            chromedriver_path=self.chromedriver_path,
        )
        with open(tokenfile, "wb") as f:
            pickle.dump(contents, f)
        logger.debug("auth saved")

    def __load_token(self):
        tokenfile = os.path.join(self.path, "token")
        token = None
        if os.path.exists(tokenfile):
            with open(tokenfile, "rb") as f:
                contents = pickle.load(f)
            if contents["token"] not in ["unauthorized_user_token", None]:
                token = contents["token"]
                self.token_date = contents["date"]
                logger.debug("auth loaded")
            self.chromedriver_path = contents.get("chromedriver_path")
        return token

    def __assert_dir(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            if self.chromedriver_path is None:
                print("\n\nFirst time setup: Installing necessary components...")
                self.__install_chromedriver()
        if not os.path.exists(self.profile_dir):
            os.mkdir(self.profile_dir)

    def __install_chromedriver(self):
        try:
            os.system("pip install chromedriver-autoinstaller")
            import chromedriver_autoinstaller
            path = chromedriver_autoinstaller.install(cwd=True)
            if path:
                self.chromedriver_path = os.path.join(self.path, "chromedriver" + (".exe" if os.name == "nt" else ""))
                shutil.copy(path, self.chromedriver_path)
                self.__save_token(token=None)
                time.sleep(1)
                os.remove(path)
        except Exception as e:
            logger.error(f"Chromedriver install failed: {e}")

    def __init__(self, username=None, password=None, chromedriver_path=None, auto_login=True) -> None:
        self.ws_debug = False
        self.__automatic_login = auto_login
        self.chromedriver_path = chromedriver_path
        self.profile_dir = os.path.join(self.path, "chrome")
        self.token_date = datetime.date.today() - datetime.timedelta(days=1)
        self.__assert_dir()
        token = self.auth(username, password)
        if token is None:
            token = "unauthorized_user_token"
            logger.warning("you are using nologin method, data you access may be limited")
        self.token = token
        self.ws = None
        self.session = self.__generate_session()
        self.chart_session = self.__generate_chart_session()

    def __login(self, username, password):
        driver = self.__webdriver_init()
        if not driver: return None
        
        if not self.__automatic_login:
            input("Press Enter after you login manually in the browser...")
        else:
            try:
                # LANGKAH 1: Langsung tembak ke URL Login (Bypass cari tombol menu)
                logger.info("Directing to login page...")
                driver.get("https://www.tradingview.com/#signin")
                time.sleep(5)

                # LANGKAH 2: Klik Pilihan Email (JS Force Click)
                # Kita pakai try-except kecil di sini kalau halaman langsung ke form email
                try:
                    email_btn = driver.find_element(By.CLASS_NAME, "tv-signin-dialog__toggle-email")
                    driver.execute_script("arguments[0].click();", email_btn)
                    time.sleep(2)
                except:
                    pass

                # LANGKAH 3: Input Username & Password
                driver.find_element(By.NAME, "username").send_keys(username)
                driver.find_element(By.NAME, "password").send_keys(password)
                
                # LANGKAH 4: Klik Login Button (JS Force Click)
                submit_btn = driver.find_element(By.CLASS_NAME, "tv-button__loader")
                driver.execute_script("arguments[0].click();", submit_btn)
                
                time.sleep(7)
                logger.info("Login process completed via Direct Link.")
            except Exception as e:
                logger.error(f"Login logic failed: {e}")
        return driver

    def auth(self, username, password):
        token = self.__load_token()
        if token is not None and self.token_date == datetime.date.today():
            return token
        
        driver = None
        if username and password:
            driver = self.__login(username, password)
        else:
            driver = self.__webdriver_init()
            
        if driver:
            token = self.__get_token(driver)
            if token:
                self.token_date = datetime.date.today()
                self.__save_token(token)
        return token

    def __webdriver_init(self):
        options = Options()
        if self.__automatic_login:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(f"user-data-dir={self.profile_dir}")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        try:
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(1920, 1080)
            driver.get("https://www.tradingview.com")
            return driver
        except Exception as e:
            logger.error(f"WebDriver Init Error: {e}")
            return None

    @staticmethod
    def __get_token(driver: webdriver.Chrome):
        try:
            driver.get("https://www.tradingview.com/chart/")
            time.sleep(10)
            token = driver.execute_script("return window.user_auth_token")
            driver.quit()
            return token
        except:
            driver.quit()
            return None

    @staticmethod
    def __filter_raw_message(text):
        try:
            found = re.search(r'"m":"(.+?)",', text).group(1)
            found2 = re.search(r'"p":(.+?"}"])}', text).group(1)
            return found, found2
        except: return None, None

    @staticmethod
    def __generate_session():
        return "qs_" + "".join(random.choice(string.ascii_lowercase) for _ in range(12))

    @staticmethod
    def __generate_chart_session():
        return "cs_" + "".join(random.choice(string.ascii_lowercase) for _ in range(12))

    @staticmethod
    def __prepend_header(st):
        return "~m~" + str(len(st)) + "~m~" + st

    @staticmethod
    def __construct_message(func, param_list):
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def __send_message(self, func, args):
        m = self.__prepend_header(self.__construct_message(func, args))
        self.ws.send(m)

    @staticmethod
    def __create_df(raw_data, symbol):
        try:
            out = re.search(r'"s":\[(.+?)\}\]', raw_data).group(1)
            x = out.split(',{"')
            data = []
            for xi in x:
                xi = re.split(r"\[|:|,|\]", xi)
                ts = datetime.datetime.fromtimestamp(float(xi[4]))
                data.append([ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])
            df = pd.DataFrame(data, columns=["datetime", "open", "high", "low", "close", "volume"]).set_index("datetime")
            df.insert(0, "symbol", value=symbol)
            return df
        except: return pd.DataFrame()

    def get_hist(self, symbol, exchange="NSE", interval=Interval.in_daily, n_bars=10, fut_contract=None, extended_session=False):
        if ":" not in symbol: symbol = f"{exchange}:{symbol}"
        if fut_contract: symbol += f"{fut_contract}!"
        
        interval_val = interval.value
        self.ws = create_connection("wss://data.tradingview.com/socket.io/websocket", headers=self.headers)
        
        self.__send_message("set_auth_token", [self.token])
        self.__send_message("chart_create_session", [self.chart_session, ""])
        self.__send_message("quote_create_session", [self.session])
        self.__send_message("resolve_symbol", [self.chart_session, "symbol_1", '={"symbol":"'+symbol+'","adjustment":"splits","session":"'+('regular' if not extended_session else 'extended')+'"}'])
        self.__send_message("create_series", [self.chart_session, "s1", "s1", "symbol_1", interval_val, n_bars])
        
        raw_data = ""
        while True:
            try:
                result = self.ws.recv()
                raw_data += result + "\n"
                if "series_completed" in result: break
            except: break
        
        self.ws.close()
        return self.__create_df(raw_data, symbol)

if __name__ == "__main__":
    tv = TvDatafeed()
    print(tv.get_hist("XAUUSD", "SAXO", interval=Interval.in_4_hour, n_bars=10))