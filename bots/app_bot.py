import app_constants
import decimal
from decimal import Decimal

decimal.getcontext().prec = app_constants.FLOATING_PRECISION

from app_database_telegram import database_telegram
from app_telegram import telegram_bot
from app_exception_control import ExceptionC

class Bot:

    def change_state_turn_on(self):

        state = database_telegram.get_database_path(self.bot_name, 'turn_on').lower()

        if state == 'yes':

            database_telegram.write_database_path(self.bot_name, 'turn_on', 'no')

        else:

            database_telegram.write_database_path(self.bot_name, 'turn_on', 'yes')


    def is_turn_on(self):

        try:

            return database_telegram.get_database_path(self.bot_name, 'turn_on').lower() == 'yes'
        
        except Exception as e:

            telegram_bot.send(str(e))

            telegram_bot.send('There was an error extracting the ' + self.bot_name + ' \'turn_on\' parameter in the database...')

            telegram_bot.send(self.bot_name + ' stopped automatically...')

            while True:

                pass


    def update_with_database(self):

        data = database_telegram.get_database_path(self.bot_name)

        try:

            self.currency = data['currency']
            self.symbol = self.currency + '-USDT'
            self.investment_order_limit = str(data['investment_order_limit'])
            self.take_profit_percent = str(data['take_profit_percent'])
            self.stop_loss_percent = str(data['stop_loss_percent'])
            self.last_prices_limit_time = int(data['last_prices_limit_time'])
            self.trade_type = data['trade_type']
            self.eps = str(data['eps'])

            message = self.bot_name + ' constants were updated:\n\n'

            for var in data:

                message += var + ' = ' + data[var] + '\n'

            telegram_bot.send(message)

            return message

        except Exception as e:

            telegram_bot.send(str(e))

            telegram_bot.send('There was an error extracting the ' + self.bot_name + ' constants in the database...')

            telegram_bot.send(self.bot_name + ' stopped automatically...')

            while True:

                pass


    def __init__(self, bot_name, kucoin_wallet):

        self.bot_name = bot_name

        telegram_bot.send('Initializing ' + self.bot_name + '...')

        self.Kc = kucoin_wallet

        self.update_with_database()

        self.print_balance()


    def start_bot(self):

        while True:

            self.update()


    def get_average_last_prices(self):

        data = self.Kc.get_last_minutes(self.currency, self.last_prices_limit_time)

        sum = 0
        
        for x in data:

            sum += float(x)
        
        return sum / len(data)

    
    def print_balance(self):

        balance_usdt = self.Kc.get_balance_usdt()
        balance_currency = self.Kc.get_balance_currency(self.currency)
        price_currency = self.Kc.get_price_currency(self.currency)

        message = self.Kc.wallet_name + ' balance with ' + self.bot_name + ':\n\n'
        message += 'Total balance usdt: ' + self.Kc.round_number_quote(self.currency, balance_usdt) + ' USDT\n'
        message += 'Total balance currency: ' + self.Kc.round_number_quote(self.currency, balance_currency) + ' ' + self.currency + '\n'
        message += 'Total balance: ' + self.Kc.round_number_quote(self.currency, str(Decimal(balance_usdt) + Decimal(balance_currency) * Decimal(price_currency))) + ' USDT'

        telegram_bot.send(message)

        return message

    
    def investment_status(self):

        balance_currency = self.Kc.get_balance_currency(self.currency)
        price_currency = self.Kc.get_price_currency(self.currency)

        if Decimal(balance_currency) * Decimal(price_currency) < Decimal(self.eps):

            return False
        
        else:

            return True


    def print_investment_status(self):

        balance_currency = self.Kc.get_balance_currency(self.currency)
        price_currency = self.Kc.get_price_currency(self.currency)

        if Decimal(balance_currency) * Decimal(price_currency) < Decimal(self.eps):

            message = self.bot_name + ' investment status:\n\n\"No investment\"'

            telegram_bot.send(message)

            return message

        else:

            investment_price = Decimal(self.investment_order_limit) / Decimal(balance_currency)
            stop_loss = Decimal(investment_price) * (Decimal('100') - Decimal(self.stop_loss_percent)) / Decimal('100')
            take_profit = Decimal(investment_price) * (Decimal('100') + Decimal(self.take_profit_percent)) / Decimal('100')

            message = self.bot_name + ' investment status:\n\n'
            message += 'Current price: ' + self.Kc.round_number_quote(self.currency, str(price_currency)) + ' USDT\n'
            message += 'Investment price: ' + self.Kc.round_number_quote(self.currency, str(investment_price)) + ' USDT\n'
            message += 'Stop loss price: ' + self.Kc.round_number_quote(self.currency, str(stop_loss)) + ' USDT\n'
            message += 'Take profit price: ' + self.Kc.round_number_quote(self.currency, str(take_profit)) + ' USDT\n'
            message += 'Stop loss: -' + self.Kc.round_number_quote(self.currency, str(Decimal(self.investment_order_limit) * Decimal(self.stop_loss_percent) / Decimal('100'))) + ' USDT\n'
            message += 'Take profit: +' + self.Kc.round_number_quote(self.currency, str(Decimal(self.investment_order_limit) * Decimal(self.take_profit_percent) / Decimal('100'))) + ' USDT\n'

            fee = self.Kc.get_currency_taker_fee(self.currency)

            ratio_fee_up = Decimal('1') + Decimal(fee) 
            ratio_fee_down = Decimal('1') - Decimal(fee)

            investment_funds = Decimal(self.investment_order_limit) * Decimal(ratio_fee_up)
            investment_gain = Decimal(self.investment_order_limit) * Decimal(price_currency) / Decimal(investment_price) * Decimal(ratio_fee_down)

            current_gain = Decimal(investment_gain) - Decimal(investment_funds)

            if Decimal(self.Kc.round_number_quote(self.currency, current_gain)) <= Decimal('0'):

                message += 'Current gain: ' + self.Kc.round_number_quote(self.currency, str(current_gain)) + ' USDT'
            
            else:

                message += 'Current gain: +' + self.Kc.round_number_quote(self.currency, str(current_gain)) + ' USDT'

            telegram_bot.send(message)

            return message


    def update(self):

        if self.is_turn_on() == False:

            telegram_bot.send(self.bot_name + ' stopped manually... Waiting')

            while self.is_turn_on() == False:

                pass

            telegram_bot.send(self.bot_name + ' started manually...')
            

        balance_usdt = str(self.Kc.get_balance_usdt())
        balance_currency = str(self.Kc.get_balance_currency(self.currency))
        price_currency = str(self.Kc.get_price_currency(self.currency))
        average_last_prices = str(self.get_average_last_prices())
        fee = str(self.Kc.get_currency_taker_fee(self.currency))

        if Decimal(balance_currency) * Decimal(price_currency) < Decimal(self.eps):

            is_good_to_invest = False

            if self.trade_type == 'uptrend':

                if Decimal(price_currency) >= Decimal(average_last_prices):

                    is_good_to_invest = True
            
            elif self.trade_type == 'downtrend':

                if Decimal(price_currency) <= Decimal(average_last_prices):

                    is_good_to_invest = True
            
            else:

                telegram_bot.send('The trade type in ' + self.bot_name + ' is not recognized...')

                telegram_bot.send(self.bot_name + ' stopped automatically...')

                while True:

                    pass


            if is_good_to_invest:

                self.Kc.buy_currency(self.currency, self.investment_order_limit)

                new_balance_usdt = self.Kc.get_balance_usdt()
                new_balance_currency = self.Kc.get_balance_currency(self.currency)

                message = self.bot_name + ' buying complete:\n\n'
                message += 'Investment: buying currency in ' + self.Kc.round_number_quote(self.currency, str(price_currency)) + ' USDT\n'
                message += 'Market buying price: ' + self.Kc.round_number_quote(self.currency, str(Decimal(self.investment_order_limit) / Decimal(new_balance_currency))) + ' USDT\n'
                message += 'Total balance usdt: ' + self.Kc.round_number_quote(self.currency, new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.Kc.round_number_quote(self.currency, new_balance_currency) + ' ' + self.currency

                telegram_bot.send(message)

        else:

            investment_price = Decimal(self.investment_order_limit) / Decimal(balance_currency)
            stop_loss = Decimal(investment_price) * (Decimal('100') - Decimal(self.stop_loss_percent)) / Decimal('100')
            take_profit = Decimal(investment_price) * (Decimal('100') + Decimal(self.take_profit_percent)) / Decimal('100')

            if Decimal(price_currency) < Decimal(stop_loss) or Decimal(take_profit) < Decimal(price_currency):

                self.Kc.sell_currency(self.currency, self.Kc.get_balance_currency(self.currency))

                new_balance_usdt = self.Kc.get_balance_usdt()
                new_balance_currency = self.Kc.get_balance_currency(self.currency)

                message = self.bot_name + ' selling complete:\n\n'

                if price_currency < stop_loss:

                    message += 'Stop loss: selling currency in ' + self.Kc.round_number_quote(self.currency, str(price_currency)) + ' USDT\n'

                if take_profit < price_currency:

                    message += 'Take profit: selling currency in ' + self.Kc.round_number_quote(self.currency, str(price_currency)) + ' USDT\n'

                message += 'Market selling price: ' + self.Kc.round_number_quote(self.currency, str((Decimal(new_balance_usdt) - Decimal(balance_usdt)) * (Decimal('1') + Decimal(fee)) / Decimal(balance_currency))) + ' USDT\n'
                message += 'Total balance usdt: ' + self.Kc.round_number_quote(self.currency, new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.Kc.round_number_quote(self.currency, new_balance_currency) + ' ' + self.currency

                telegram_bot.send(message)