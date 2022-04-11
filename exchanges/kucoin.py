from kucoin.client import Market
from kucoin.client import Trade
from kucoin.client import User

from app_telegram import telegram_bot
from app_exception_control import ExceptionC

class Kucoin:

    def __init__(self, wallet_name, api_key = '', api_secret = '', api_passphrase = '', is_sandbox = False):

        self.wallet_name = wallet_name
        self.client_market = Market()
        self.client_trade = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)
        self.client_user = User(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)


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

            return cad
            
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


    def get_balance_currency(self, currency):

        try:

            return ExceptionC.with_send(self.client_user.get_account_list, currency = currency, account_type = 'trade')[0]['balance']

        except:

            return str(0)


    def get_balance_usdt(self):

        try:

            return ExceptionC.with_send(self.client_user.get_account_list, currency = 'USDT', account_type = 'trade')[0]['balance']

        except:

            return str(0)


    def get_balance_total(self):

        data = {}

        for bucket in ExceptionC.with_send(self.client_user.get_account_list, account_type = 'trade'):

            data[bucket['currency']] = bucket['balance']

        return data


    def get_price_currency(self, currency):

        return ExceptionC.with_send(self.client_market.get_24h_stats, symbol = self.get_symbol_from_currency(currency))['last']


    def get_last_minutes(self, currency, minutes):

        tend = ExceptionC.with_send(self.client_market.get_server_timestamp) // 1000
        tstart = tend - minutes * 60

        arr = []

        for bucket in ExceptionC.with_print(self.client_market.get_kline, symbol = self.get_symbol_from_currency(currency), kline_type = '1min', startAt = str(tstart), endAt = str(tend)):

            arr.append(bucket[2])

        return arr


    def buy_currency(self, currency, funds):

        if float(self.get_balance_usdt()) < float(funds):

            telegram_bot.send('Insufficient usdt balance in ' + self.wallet_name + ' to buy...')

            telegram_bot.send('Bot in ' + self.wallet_name + ' stopped automatically...')

            while True:

                pass

        ExceptionC.with_send(self.client_trade.create_market_order, symbol = self.get_symbol_from_currency(currency), side = 'buy', funds = self.round_number_price(currency, funds))
        
        while True:

            if len(ExceptionC.with_send(self.client_trade.get_order_list, status = 'active')['items']) == 0:

                break
            
            telegram_bot.send('Buying currency in ' + self.wallet_name + '...')


    def sell_currency(self, currency, size):

        if float(self.get_balance_currency(currency)) < float(size):

            telegram_bot.send('Insufficient currency balance in ' + self.wallet_name + ' to sell...')

            telegram_bot.send('Bot in ' + self.wallet_name + ' stopped automatically...')

            while True:

                pass

        ExceptionC.with_send(self.client_trade.create_market_order, symbol = self.get_symbol_from_currency(currency), side = 'sell', size = self.round_number_base(currency, size))

        while True:

            if len(ExceptionC.with_send(self.client_trade.get_order_list, status = 'active')['items']) == 0:

                break
            
            telegram_bot.send('Selling currency in ' + self.wallet_name + '...')