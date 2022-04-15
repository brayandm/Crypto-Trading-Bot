import app_constants
import decimal
from decimal import Decimal

decimal.getcontext().prec = app_constants.FLOATING_PRECISION

from kucoin.client import Market
from kucoin.client import Trade
from kucoin.client import User

from app_database_telegram import database_telegram
from app_telegram import telegram_bot
from app_exception_control import ExceptionC
from app_exception_control import ExceptionC

class WalletVirtual:

    def __init__(self, wallet_name):

        self.wallet_name = wallet_name


    def get_balance_all_currencies(self):

        if database_telegram.exists_database_path(self.wallet_name) == False:

            database_telegram.write_database_path(self.wallet_name, {})

        return database_telegram.get_database_path(self.wallet_name)


    def get_balance_currency(self, currency):

        if database_telegram.exists_database_path(self.wallet_name, currency) == False:

            database_telegram.write_database_path(self.wallet_name, currency, '0')

        return database_telegram.get_database_path(self.wallet_name, currency)


    def set_balance_currency(self, currency, value):

        database_telegram.write_database_path(self.wallet_name, currency, value)


class UserVirtual:

    def __init__(self, wallet):

        self.wallet = wallet


    def get_account_list(self, currency = None, account_type = None):

        data = self.wallet.get_balance_all_currencies()

        arr = []

        for key in data:

            if currency == None or currency == key:

                arr.append({'currency': str(key), 'balance': str(data[key])})
        
        return arr


class TradeVirtual:

    def __init__(self, wallet):

        self.wallet = wallet
        self.client_market = Market()


    def get_price_currency(self, symbol = None):

        return ExceptionC.with_send(self.client_market.get_24h_stats, symbol = symbol)['last'] 


    def get_currency_taker_fee(self, symbol = None):

        return ExceptionC.with_send(self.client_market.get_24h_stats, symbol = symbol)['takerFeeRate']


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


    def create_market_order(self, symbol = None, side = None, funds = None, size = None):

        sell_side = symbol.split('-')[0]
        buy_side = symbol.split('-')[1]

        price = self.get_price_currency(symbol)
        fee = self.get_currency_taker_fee(symbol)

        if side == 'buy':

            new_balance_usdt = str(Decimal(self.wallet.get_balance_currency(buy_side)) - Decimal(funds) * (Decimal('1') + Decimal(fee)))
            new_balance_currency = str(Decimal(self.wallet.get_balance_currency(sell_side)) + Decimal(funds) / Decimal(price))

            self.wallet.set_balance_currency(buy_side, self.round_number_quote(sell_side, new_balance_usdt))
            self.wallet.set_balance_currency(sell_side, self.round_number_base(sell_side, new_balance_currency))

        if side == 'sell':

            new_balance_currency = str(Decimal(self.wallet.get_balance_currency(sell_side)) - Decimal(size))
            new_balance_usdt = str(Decimal(self.wallet.get_balance_currency(buy_side)) + Decimal(size) * Decimal(price) * (Decimal('1') - Decimal(fee)))

            self.wallet.set_balance_currency(sell_side, self.round_number_base(sell_side, new_balance_currency))
            self.wallet.set_balance_currency(buy_side, self.round_number_quote(sell_side, new_balance_usdt))


    def get_order_list(self, status = None):

        return {'items' : []}


class KucoinVirtual:

    def __init__(self, wallet_name):

        self.wallet_name = wallet_name

        self.wallet_virtual = WalletVirtual(wallet_name)

        self.client_market = Market()
        self.client_trade = TradeVirtual(self.wallet_virtual)
        self.client_user = UserVirtual(self.wallet_virtual)


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


    def get_order_list(self, currency):

        return ExceptionC.with_send(self.client_trade.get_order_list)


    def buy_currency(self, currency, funds):

        if Decimal(self.get_balance_usdt()) < Decimal(funds) * (Decimal('1') + Decimal(self.get_currency_taker_fee(currency))):

            telegram_bot.send('Insufficient usdt balance in ' + self.wallet_name + ' to buy...')

            telegram_bot.send('Bot in ' + self.wallet_name + ' stopped automatically...')

            while True:

                pass

        ExceptionC.with_send(self.client_trade.create_market_order, symbol = self.get_symbol_from_currency(currency), side = 'buy', funds = self.round_number_quote(currency, funds))
        
        while True:

            if len(ExceptionC.with_send(self.client_trade.get_order_list, status = 'active')['items']) == 0:

                break
            
            telegram_bot.send('Buying currency in ' + self.wallet_name + '...')


    def sell_currency(self, currency, size):

        if Decimal(self.get_balance_currency(currency)) < Decimal(size):

            telegram_bot.send('Insufficient currency balance in ' + self.wallet_name + ' to sell...')

            telegram_bot.send('Bot in ' + self.wallet_name + ' stopped automatically...')

            while True:

                pass

        ExceptionC.with_send(self.client_trade.create_market_order, symbol = self.get_symbol_from_currency(currency), side = 'sell', size = self.round_number_base(currency, size))

        while True:

            if len(ExceptionC.with_send(self.client_trade.get_order_list, status = 'active')['items']) == 0:

                break
            
            telegram_bot.send('Selling currency in ' + self.wallet_name + '...')