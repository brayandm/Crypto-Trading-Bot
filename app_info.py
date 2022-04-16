import app_constants
import decimal
from decimal import Decimal

decimal.getcontext().prec = app_constants.FLOATING_PRECISION

import threading
from threading import RLock

import matplotlib.pyplot as plt

from kucoin.client import Market
from kucoin_futures.client import Market as MarketFutures

from app_telegram import telegram_bot
from app_exception_control import ExceptionC
from app_database import database


class CumulativeTable:

    def __init__(self):

        self.tacum = []


    def append(self, x):

        if len(self.tacum) == 0:

            self.tacum.append(x)

        else:

            self.tacum.append(self.tacum[-1] + x)


    def sum(self, a, b):

        if a == 0:

            return self.tacum[b] 

        return self.tacum[b] - self.tacum[a-1]


class Info:

    def __init__(self):

        self.client_market = Market()
        self.client_market_futures = MarketFutures()
        self.day_in_minutes = 60*24
        self.maximum_size_per_request = 200


    def get_currency_from_symbol(self, symbol):

        return symbol.split('-')[0]


    def get_symbol_from_currency(self, currency):

        return currency + '-USDT'


    def get_constant_round(self, currency):

        for bucket in ExceptionC.with_send(self.client_market.get_symbol_list):

            if bucket['symbol'] == self.get_symbol_from_currency(currency):

                return (bucket['baseIncrement'], bucket['quoteIncrement'])
    
        telegram_bot.send('Symbol not found in ' + self.wallet_name + '...')

        telegram_bot.send('Bot in ' + self.wallet_name + ' stopped automatically...')

        while True:

            pass


    def round_number(self, number, precision):

        exp10 = Decimal('1') / (Decimal('10') ** Decimal(precision))

        return str(Decimal(number).quantize(exp10, rounding = decimal.ROUND_DOWN))


    def round_number_base(self, currency, number):

        return str(Decimal(number).quantize(Decimal(self.get_constant_round(currency)[0]), rounding = decimal.ROUND_DOWN))


    def round_number_quote(self, currency, number):

        return str(Decimal(number).quantize(Decimal(self.get_constant_round(currency)[1]), rounding = decimal.ROUND_DOWN))


    def get_price_currency(self, currency):

        return ExceptionC.with_send(self.client_market.get_ticker, symbol = self.get_symbol_from_currency(currency))['price']


    def get_currency_taker_fee(self, currency):

        return ExceptionC.with_send(self.client_market.get_24h_stats, symbol = self.get_symbol_from_currency(currency))['takerFeeRate']


    def get_currency_maker_fee(self, currency):

        return ExceptionC.with_send(self.client_market.get_24h_stats, symbol = self.get_symbol_from_currency(currency))['makerFeeRate']


    def get_last_minutes(self, currency, minutes):

        tend = ExceptionC.with_send(self.client_market.get_server_timestamp) // 1000
        tstart = tend - minutes * 60

        arr = []

        for bucket in ExceptionC.with_print(self.client_market.get_kline, symbol = self.get_symbol_from_currency(currency), kline_type = '1min', startAt = str(tstart), endAt = str(tend)):

            arr.append(bucket[2])

        return arr

    
    def get_server_time_minutes(self):

        return ExceptionC.with_send(self.client_market.get_server_timestamp) // 1000 // 60

    
    def get_prices_futures(self, symbol, granularity, start, end):

        granularity = int(granularity)
        start = int(start)
        end = int(end)

        thlock = RLock()

        results = {}


        def get_kline(symbol, granularity, start, end):
        
            while True:

                try:

                    data = self.client_market_futures.get_kline_data(symbol = symbol, granularity = granularity, begin_t = start*60*1000, end_t = end*60*1000+1)

                    with thlock:

                        results[start] = data.reverse()

                    break

                except:

                    pass


        mthreads = []

        for i in reversed(range(start, end+1, granularity * self.maximum_size_per_request)):

            tstart = i
            tend = min(i + granularity * self.maximum_size_per_request - 1, end)

            mthreads.append(threading.Thread(target=get_kline, args=(symbol, granularity, tstart, tend,)))

        for i in range(len(mthreads)):

            mthreads[i].start()

        for i in range(len(mthreads)):

            mthreads[i].join()

        data = []

        for i in reversed(range(start, end+1, granularity * self.maximum_size_per_request)):

            for j in range(len(results[i])):

                data.append(str(results[i][j][4]))

        return data


    def get_all_futures(self, days, granularity, symbols):

        thlock = RLock()

        results = {}


        def get_prices(symbol, granularity, start, end):
        
            data = self.get_prices_futures(symbol, granularity, start, end)

            with thlock:

                results[symbol] = data


        last_day = self.get_server_time_minutes() // self.day_in_minutes

        mthreads = []

        for symbol in symbols:

            mthreads.append(threading.Thread(target=get_prices, args=(symbol, granularity, (last_day-int(days)) * self.day_in_minutes, last_day * self.day_in_minutes,)))

        for i in range(len(mthreads)):

            mthreads[i].start()

        for i in range(len(mthreads)):

            mthreads[i].join()

        data = []

        for symbol in symbols:

            data.append([symbol, results[symbol]])

        return data


    def generate_image_currency_prices(self, currency, filename, days = None):

        if days == None:
        
            data = list(reversed(database.get_currency(currency)))

        else:

            data = list(reversed(database.get_currency_days_before(currency, str(int(days) + 30))))

        MA30 = self.day_in_minutes*30
        MA20 = self.day_in_minutes*20
        MA10 = self.day_in_minutes*10

        cumulative_table = CumulativeTable()

        for i in range(len(data)):

            cumulative_table.append(float(data[i]))
            
        ma30x = []
        ma30y = []
        ma20x = []
        ma20y = []
        ma10x = []
        ma10y = []
        x = []
        y = []

        for i in range(MA30-1, len(data)):

            ma30x.append(i / self.day_in_minutes)
            ma30y.append(cumulative_table.sum(i-MA30+1, i) / MA30)

        for i in range(MA20-1, len(data)):

            ma20x.append(i / self.day_in_minutes)
            ma20y.append(cumulative_table.sum(i-MA20+1, i) / MA20)

        for i in range(MA10-1, len(data)):

            ma10x.append(i / self.day_in_minutes)
            ma10y.append(cumulative_table.sum(i-MA10+1, i) / MA10)

        for i in range(len(data)):

            x.append(i / self.day_in_minutes)
            y.append(float(data[i]))

        if days != None:

            ma30x = ma30x[self.day_in_minutes * 0:]
            ma30y = ma30y[self.day_in_minutes * 0:]
            ma20x = ma20x[self.day_in_minutes * 10:]
            ma20y = ma20y[self.day_in_minutes * 10:]
            ma10x = ma10x[self.day_in_minutes * 20:]
            ma10y = ma10y[self.day_in_minutes * 20:]
            x = x[self.day_in_minutes * 30 - 1:]
            y = y[self.day_in_minutes * 30 - 1:]

            for i in range(len(x)):

                ma30x[i] -= 30
                ma20x[i] -= 30
                ma10x[i] -= 30
                x[i] -= 30

        plt.figure()
        plt.plot(ma30x, ma30y, color = 'red', linestyle = '-', linewidth = 0.8)
        plt.plot(ma20x, ma20y, color = 'orange', linestyle = '-', linewidth = 0.8)
        plt.plot(ma10x, ma10y, color = 'yellow', linestyle = '-', linewidth = 0.8)
        plt.plot(x, y, color = 'blue', linestyle = '-', linewidth = 0.8)
        plt.title(currency + ' Price Chart')
        plt.xlabel('Days')
        plt.ylabel('Price (USDT)')
        plt.legend(labels = ['MA30', 'MA20', 'MA10', 'Price'])
        plt.savefig(filename)
        

info = Info()