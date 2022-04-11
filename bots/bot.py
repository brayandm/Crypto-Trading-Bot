import json

from app_telegram import telegram_bot
from app_exception_control import ExceptionC

class Bot:
    
    # currency = 'NEAR'
    # symbol = 'NEAR-USDT'
    # investment_order_limit = 10
    # take_profit_percent = 2.3
    # stop_loss_percent = 5.7
    # last_prices_limit_time = 210
    # eps = 0.01

    def update_constants(self):

        data = json.loads(telegram_bot.get_message_database()[0])

        try:

            self.currency = data['currency']
            self.symbol = self.currency + '-USDT'
            self.investment_order_limit = float(data['investment_order_limit'])
            self.take_profit_percent = float(data['take_profit_percent'])
            self.stop_loss_percent = float(data['stop_loss_percent'])
            self.last_prices_limit_time = int(data['last_prices_limit_time'])
            self.eps = float(data['eps'])

            message = 'Bot constants were updated:\n\n'

            for var in data:

                message += var + ' = ' + data[var] + '\n'

            telegram_bot.send(message)

        except:

            telegram_bot.send('There was an error extracting the constants in the database...')

            ExceptionC.stop_bot()


    def __init__(self, kucoin_wallet):

        telegram_bot.send('Initializing bot...')

        self.turn_on = True

        self.Kc = kucoin_wallet

        self.last_message_id_status = telegram_bot.get_message_status()[1]
        
        self.update_constants()

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

        message = 'Total balance usdt: ' + self.Kc.round_number_price(self.currency, balance_usdt) + ' USDT\n'
        message += 'Total balance currency: ' + self.Kc.round_number_price(self.currency, balance_currency) + ' ' + self.currency + '\n'
        message += 'Total balance: ' + self.Kc.round_number_price(self.currency, str(float(balance_usdt) + float(balance_currency) * float(price_currency))) + ' USDT'

        telegram_bot.send(message)

    
    def investment_status(self):

        balance_currency = float(self.Kc.get_balance_currency(self.currency))
        price_currency = float(self.Kc.get_price_currency(self.currency))

        if balance_currency * price_currency < self.eps:

            return False
        
        else:

            return True


    def print_investment_status(self):

        balance_currency = float(self.Kc.get_balance_currency(self.currency))
        price_currency = float(self.Kc.get_price_currency(self.currency))

        if balance_currency * price_currency < self.eps:

            telegram_bot.send('Investment status:\n\n\"No investment\"')

        else:

            investment_price = self.investment_order_limit / balance_currency
            stop_loss = investment_price * (100 - self.stop_loss_percent) / 100
            take_profit = investment_price * (100 + self.take_profit_percent) / 100

            message = 'Investment status:\n\n'
            message += 'Current price: ' + self.Kc.round_number_price(self.currency, str(price_currency)) + ' USDT\n'
            message += 'Investment price: ' + self.Kc.round_number_price(self.currency, str(investment_price)) + ' USDT\n'
            message += 'Stop loss price: ' + self.Kc.round_number_price(self.currency, str(stop_loss)) + ' USDT\n'
            message += 'Take profit price: ' + self.Kc.round_number_price(self.currency, str(take_profit)) + ' USDT\n'
            message += 'Stop loss: -' + self.Kc.round_number_price(self.currency, str(self.investment_order_limit * self.stop_loss_percent / 100)) + ' USDT\n'
            message += 'Take profit: +' + self.Kc.round_number_price(self.currency, str(self.investment_order_limit * self.take_profit_percent / 100)) + ' USDT\n'

            current_gain = self.investment_order_limit * price_currency / investment_price - self.investment_order_limit

            if current_gain < 0:

                message += 'Current gain: ' + self.Kc.round_number_price(self.currency, str(current_gain)) + ' USDT'
            
            else:

                message += 'Current gain: +' + self.Kc.round_number_price(self.currency, str(current_gain)) + ' USDT'
            
            telegram_bot.send(message)


    def update_status(self):

        (message, message_id) = telegram_bot.get_message_status()

        if message_id == self.last_message_id_status and message.lower() != 'stop':

            return
        
        self.last_message_id_status = message_id

        message = message.lower()

        if message == 'price':

            telegram_bot.send('Currency price: ' + self.Kc.get_price_currency(self.Kc.currency) + ' USDT')
        
        elif message == 'investment':

            self.print_investment_status()

        elif message == 'balance':

            self.print_balance()
        
        elif message == 'update':

            self.update_constants()

        elif message == 'stop':

            telegram_bot.send('Bot stopped manually... Waiting')

            while True:

                if telegram_bot.get_message_status()[0].lower() == 'start':

                    telegram_bot.send('Bot started manually...')

                    break


    def update(self):

        if self.turn_on == False:

            telegram_bot.send('Bot stopped manually... Waiting')

            while self.turn_on == False:

                pass

            telegram_bot.send('Bot started manually...')
            

        self.update_status()        
                    
        balance_usdt = float(self.Kc.get_balance_usdt())
        balance_currency = float(self.Kc.get_balance_currency(self.currency))
        price_currency = float(self.Kc.get_price_currency(self.currency))
        average_last_prices = self.get_average_last_prices()

        if balance_currency * price_currency < self.eps:

            if price_currency <= average_last_prices:

                self.Kc.buy_currency(self.currency, self.investment_order_limit)

                new_balance_usdt = self.Kc.get_balance_usdt()
                new_balance_currency = self.Kc.get_balance_currency(self.currency)

                message = 'Buying complete:\n\n'
                message += 'Investment: buying currency in ' + self.Kc.round_number_price(self.currency, str(price_currency)) + ' USDT\n'
                message += 'Market buying price: ' + self.Kc.round_number_price(self.currency, str(self.investment_order_limit / float(new_balance_currency))) + ' USDT\n'
                message += 'Total balance usdt: ' + self.Kc.round_number_price(self.currency, new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.Kc.round_number_price(self.currency, new_balance_currency) + ' ' + self.currency

                telegram_bot.send(message)

        else:

            investment_price = self.investment_order_limit / balance_currency
            stop_loss = investment_price * (100 - self.stop_loss_percent) / 100
            take_profit = investment_price * (100 + self.take_profit_percent) / 100

            if price_currency < stop_loss or take_profit < price_currency:

                self.Kc.sell_currency(self.currency, self.Kc.get_balance_currency(self.currency))

                new_balance_usdt = self.Kc.get_balance_usdt()
                new_balance_currency = self.Kc.get_balance_currency(self.currency)

                message = 'Selling complete:\n\n'

                if price_currency < stop_loss:

                    message += 'Stop loss: selling currency in ' + self.Kc.round_number_price(self.currency, str(price_currency)) + ' USDT\n'

                if take_profit < price_currency:

                    message += 'Take profit: selling currency in ' + self.Kc.round_number_price(self.currency, str(price_currency)) + ' USDT\n'

                message += 'Market selling price: ' + self.Kc.round_number_price(self.currency, str((float(new_balance_usdt) - balance_usdt) / balance_currency)) + ' USDT\n'
                message += 'Total balance usdt: ' + self.Kc.round_number_price(self.currency, new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.Kc.round_number_price(self.currency, new_balance_currency) + ' ' + self.currency

                telegram_bot.send(message)