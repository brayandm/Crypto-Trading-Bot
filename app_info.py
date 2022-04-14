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

            data = list(reversed(database.get_currency_days_before(currency, days)))

        MA30 = 60*24*30

        cumulative_table = CumulativeTable()

        for i in range(len(data)):

            cumulative_table.append(data[i])
            
        ma30x = []
        ma30y = []
        x = []
        y = []

        for i in range(MA30-1, len(data)):

            ma30x.append(i)
            ma30y.append(cumulative_table.sum(i-MA30+1, i))

        for i in range(len(data)):

            x.append(i)
            y.append(float(data[i]))

        plt.plot(ma30x, ma30y, color = 'orange', linestyle = '-')
        plt.plot(x, y, color = 'blue', linestyle = '-')
        plt.savefig(filename)


info = Info()