import os

from kucoin.client import Market
from kucoin.client import Trade
from kucoin.client import User

from app_telegram import telegram_bot
from app_exception_control import ExceptionControl

class Kucoin:

    api_key = os.environ['api_key']
    api_secret = os.environ['api_secret']
    api_passphrase = os.environ['api_passphrase']
    is_sandbox = True if os.environ['is_sandbox'] == 'yes' else False

    client_market = Market()
    client_trade = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)
    client_user = User(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)

    def get_currency_from_symbol(self, symbol):

        return symbol.split('-')[0]


    def get_symbol_from_currency(self, currency):

        return currency + '-USDT'


    def get_constant_round(self, currency):

        for bucket in ExceptionControl.with_send(self.client_market.get_symbol_list()):

            if bucket['symbol'] == self.get_symbol_from_currency(currency):

                return (len(bucket['baseIncrement']) - 2, len(bucket['priceIncrement']) - 2)
    
        telegram_bot.send('Symbol not found... Bot stopped')

        ExceptionControl.stop_bot()


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
        
        return cad


    def round_number_base(self, currency, number):

        return self.round_number(number, self.get_constant_round(currency)[0])


    def round_number_price(self, currency, number):

        return self.round_number(number, self.get_constant_round(currency)[1])


    def get_balance_currency(self, currency):

        try:

            return ExceptionControl.with_send(self.client_user.get_account_list, currency = currency, account_type = 'trade')[0]['balance']

        except:

            return str(0)


    def get_balance_usdt(self):

        try:

            return ExceptionControl.with_send(self.client_user.get_account_list, currency = 'USDT', account_type = 'trade')[0]['balance']

        except:

            return str(0)


    def get_price_currency(self, currency):

        return ExceptionControl(self.client_market.get_24h_stats, symbol = self.get_symbol_from_currency(currency))['last']


    def get_last_minutes(self, currency, minutes):

        tend = ExceptionControl.with_send(self.client_market.get_server_timestamp()) // 1000
        tstart = tend - minutes * 60

        arr = []

        for bucket in ExceptionControl.with_send(self.client_market.get_kline, symbol = self.get_symbol_from_currency(currency), kline_type = '1min', startAt = str(tstart), endAt = str(tend)):

            arr.append(bucket[2])

        return arr


    def buy_currency(self, currency, funds):

        # if float(self.get_balance_usdt()) < funds:

        #     telegram_bot.send('Insufficient usdt balance to buy... Bot stopped')

        #     ExceptionControl.stop_bot()

        # ExceptionControl.with_send(self.client_trade.create_market_order, symbol = self.get_symbol_from_currency(currency), side = 'buy', funds = self.round_number_price(currency, funds))
        
        while True:

            if ExceptionControl.with_send(self.client_trade.get_order_list, status = 'active')['items'] == 0:

                break
            
            telegram_bot.send('Buying currency...')

            ExceptionControl.check_stop()


    def sell_currency(self, currency, size):

        # if float(self.get_balance_currency(currency)) < size:

        #     telegram_bot.send('Insufficient currency balance to sell... Bot stopped')

        #     ExceptionControl.stop_bot()

        # ExceptionControl.with_send(self.client_trade.create_market_order, symbol = self.get_symbol_from_currency(currency), side = 'sell', size = self.round_number_base(currency, size))

        while True:

            if ExceptionControl.with_send(self.client_trade.get_order_list, status = 'active')['items'] == 0:

                break
            
            telegram_bot.send('Selling currency...')

            ExceptionControl.check_stop()
        
        
Kc = Kucoin()