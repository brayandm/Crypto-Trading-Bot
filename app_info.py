import matplotlib.pyplot as plt

from kucoin.client import Market

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
        self.day_in_minutes = 60*24


    def get_currency_from_symbol(self, symbol):

        return symbol.split('-')[0]


    def get_symbol_from_currency(self, currency):

        return currency + '-USDT'


    def get_constant_round(self, currency):

        for bucket in ExceptionC.with_send(self.client_market.get_symbol_list):

            if bucket['symbol'] == self.get_symbol_from_currency(currency):

                return (len(bucket['baseIncrement']) - 2, len(bucket['priceIncrement']) - 2)
    
        telegram_bot.send('Symbol not found in ' + self.wallet_name + '...')

        telegram_bot.send('Bot in ' + self.wallet_name + ' stopped automatically...')

        while True:

            pass


    def round_number(self, number, precision):

        cad = str(number)

        point_position = -1

        for i in range(len(cad)):

            if cad[i] == '.':

                point_position = i
        
        if point_position == -1:

            point_position = len(cad)

            cad += '.'

        while point_position + precision + 1 < len(cad):

            cad = cad[0:-1]

        while len(cad) < point_position + precision + 1:

            cad += '0'

        if cad[-1] == '.':

            cad = cad[0:-1]
        
        return cad


    def round_number_base(self, currency, number):

        return self.round_number(number, self.get_constant_round(currency)[0])


    def round_number_price(self, currency, number):

        return self.round_number(number, self.get_constant_round(currency)[1])


    def get_price_currency(self, currency):

        return ExceptionC.with_send(self.client_market.get_24h_stats, symbol = self.get_symbol_from_currency(currency))['last']


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
            x = x[self.day_in_minutes * 30:]
            y = y[self.day_in_minutes * 30:]

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