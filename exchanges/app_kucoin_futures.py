import app_futures_currencies as app_futures_currencies
import app_constants
import decimal
from decimal import Decimal

decimal.getcontext().prec = app_constants.FLOATING_PRECISION

from kucoin_futures.client import Market
from kucoin_futures.client import Trade
from kucoin_futures.client import User

import threading
from threading import RLock

from app_telegram import telegram_bot
from app_exception_control import ExceptionC

class KucoinFutures:

    def __init__(self, wallet_name, api_key = '', api_secret = '', api_passphrase = '', is_sandbox = False):

        self.wallet_name = wallet_name
        self.client_market = Market()
        self.client_trade = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)
        self.client_user = User(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)
        self.symbols = app_futures_currencies.data


    def get_server_time(self):

        return ExceptionC.with_send(self.client_market.get_server_timestamp)


    def RSI(self, symbol, type):

        type = int(type)

        EPS = 1e-9

        while True:

            day = 1000*60*60*24

            tnow = self.get_server_time()

            data = ExceptionC.with_send(self.client_market.get_kline_data, symbol = symbol, granularity = 1440, begin_t = tnow - day * (type + 1), end_t = tnow)

            if len(data) == type+1:

                break

        prices = []

        for x in data:

            prices.append(x[4])

        UPA = EPS
        DOWNA = EPS

        for i in range(1, len(prices)):

            if prices[i-1] <= prices[i]:

                UPA += prices[i] - prices[i-1]

            else:

                DOWNA += prices[i-1] - prices[i]

        return 100 - 100 / (1 + UPA / DOWNA)
        
    
    def get_RSIs(self, type):

        thlock = RLock()

        results = {}


        def get_rsi(symbol, type):
        
            data = self.RSI(symbol, type)

            with thlock:

                results[symbol] = data


        mthreads = []

        for symbol in self.symbols:

            mthreads.append(threading.Thread(target=get_rsi, args=(symbol, type,)))

        for i in range(len(mthreads)):

            mthreads[i].start()

        for i in range(len(mthreads)):

            mthreads[i].join()

        data = {}

        for symbol in self.symbols:

            data[symbol] = results[symbol]

        return data