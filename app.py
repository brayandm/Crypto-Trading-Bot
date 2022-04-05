import os
import json

from kucoin.client import Market
from kucoin.client import Trade
from kucoin.client import User

from telegram import Bot

telegram_bot = Bot(os.environ['bot_token'])

output_channel = os.environ['output_channel']
status_channel = os.environ['status_channel']
database_channel = os.environ['database_channel']

def send(message):

    print(message)

    while True:

        try:

            telegram_bot.send_message(output_channel, message)

            break

        except:

            print('Function \'send()\' failed... Attempting again')


def get_message_status():

    while True:

        try:

            data = telegram_bot.get_chat(status_channel)

            break

        except:

            send('Function \'get_message_status()\' failed... Attempting again')

    return (data.pinned_message.text, data.pinned_message.message_id)


def get_message_database():

    while True:

        try:

            data = telegram_bot.get_chat(database_channel)

            break

        except:

            send('Function \'get_message_database()\' failed... Attempting again')

    return (data.pinned_message.text, data.pinned_message.message_id)


class Bot:
    
    currency = 'NEAR'
    symbol = 'NEAR-USDT'
    investment_order_limit = 10
    take_profit_percent = 2.3
    stop_loss_percent = 5.7
    last_prices_limit_time = 12600
    eps = 0.01

    last_message_id_status = None

    api_key = os.environ['api_key']
    api_secret = os.environ['api_secret']
    api_passphrase = os.environ['api_passphrase']
    is_sandbox = True if os.environ['is_sandbox'] == 'yes' else False

    client_market = Market()
    client_trade = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)
    client_user = User(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=is_sandbox)

    def update_constants(self):

        while True:

            try:

                data = json.loads(get_message_database()[0])

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

                send(message)

                break
        
            except:

                send('Function \'update_constants()\' failed... Attempting again')

                self.update_status()


    def __init__(self):

        self.last_message_id_status = get_message_status()[1]
        
        while True:

            try:

                self.update_constants()    

                (self.constant_round_base, self.constant_round_price) = self.get_constant_round()

                break

            except: 

                send('Function \'__init__()\' failed... Attempting again')

                self.update_status()


    def get_constant_round(self):

        while True:

            try:

                data = self.client_market.get_symbol_list()

                for bucket in data:

                    if bucket['symbol'] == self.symbol:

                        return (len(bucket['baseIncrement']) - 2, len(bucket['priceIncrement'] - 2))
            
                send('Symbol not found... Bot stopped')

                while True:

                    self.update_status()

                    pass    

            except:

                send('Function \'get_constant_round()\' failed... Attempting again')

                self.update_status()


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


    def round_number_base(self, number):

        return self.round_number(number, self.constant_round_base)


    def round_number_price(self, number):

        return self.round_number(number, self.constant_round_price)


    def buy_currency(self):

        if float(self.get_balance_usdt()) < self.investment_order_limit:

            send('Insufficient balance to invest... Bot stopped')

            while True:

                self.update_status()

                pass
        
        while True:

            try:

                self.client_trade.create_market_order(self.symbol, 'buy', funds = self.round_number_price(self.investment_order_limit))
            
                break

            except:

                send('Function \'buy_currency()\' failed... Attempting again')

                self.update_status()


    def sell_currency(self):

        balance_currency = self.get_balance_currency()

        while True:

            try:

                self.client_trade.create_market_order(self.symbol, 'sell', size = self.round_number_base(balance_currency))
            
                break

            except:

                send('Function \'sell_currency()\' failed... Attempting again')

                self.update_status()


    def get_balance_currency(self):

        while True:

            try:

                data = self.client_user.get_account_list(self.currency, 'trade')

                break

            except:

                send('Function \'get_balance_currency()\' failed... Attempting again')

                self.update_status()
        
        try:

            return data[0]['balance']

        except:

            return str(0)

    
    def get_balance_usdt(self):

        while True:

            try:

                data = self.client_user.get_account_list('USDT', 'trade')

                break

            except:

                send('Function \'get_balance_usdt()\' failed... Attempting again')

                self.update_status()

        try:

            return data[0]['balance']

        except:

            return str(0)


    def get_price_currency(self):

        while True:

            try:

                data = self.client_market.get_24h_stats(self.symbol)

                break

            except:

                send('Function \'get_price_currency()\' failed... Attempting again')

                self.update_status()

        return data['last']


    def get_average_last_prices(self):

        while True:

            try:

                tnow = self.client_market.get_server_timestamp() // 1000

                tend = tnow
                tstart = tend - self.last_prices_limit_time

                data = self.client_market.get_kline(self.symbol, '1min', startAt = str(tstart), endAt = str(tend))

                break

            except:

                print('Function \'get_average_last_prices()\' failed... Attempting again')

                self.update_status()

        sum = 0
        
        for bucket in data:

            sum += float(bucket[1]) + float(bucket[2])
        
        return sum / (len(data) * 2)

    
    def print_balance(self):

        balance_usdt = self.get_balance_usdt()
        balance_currency = self.get_balance_currency()
        price_currency = self.get_price_currency()

        message = 'Total balance usdt: ' + self.round_number_price(balance_usdt) + ' USDT\n'
        message += 'Total balance currency: ' + self.round_number_price(balance_currency) + ' ' + self.currency + '\n'
        message += 'Total balance: ' + self.round_number_price(str(float(balance_usdt) + float(balance_currency) * float(price_currency))) + ' USDT'

        send(message)

    
    def investment_status(self):

        balance_currency = float(self.get_balance_currency())
        price_currency = float(self.get_price_currency())

        if balance_currency * price_currency < self.eps:

            return False
        
        else:

            return True


    def print_investment_status(self):

        balance_currency = float(self.get_balance_currency())
        price_currency = float(self.get_price_currency())

        if balance_currency * price_currency < self.eps:

            send('Investment status:\n\n\"No investment\"')

        else:

            investment_price = self.investment_order_limit / balance_currency
            stop_loss = investment_price * (100 - self.stop_loss_percent) / 100
            take_profit = investment_price * (100 + self.take_profit_percent) / 100

            message = 'Investment status:\n\n'
            message += 'Current price: ' + self.round_number_price(str(price_currency)) + ' USDT\n'
            message += 'Investment price: ' + self.round_number_price(str(investment_price)) + ' USDT\n'
            message += 'Stop loss price: ' + self.round_number_price(str(stop_loss)) + ' USDT\n'
            message += 'Take profit price: ' + self.round_number_price(str(take_profit)) + ' USDT\n'
            message += 'Stop loss: -' + self.round_number_price(str(self.investment_order_limit * self.stop_loss_percent / 100)) + ' USDT\n'
            message += 'Take profit: +' + self.round_number_price(str(self.investment_order_limit * self.take_profit_percent / 100)) + ' USDT\n'

            current_gain = self.investment_order_limit * price_currency / investment_price - self.investment_order_limit

            if current_gain < 0:

                message += 'Current gain: ' + self.round_number_price(str(current_gain)) + ' USDT'
            
            else:

                message += 'Current gain: +' + self.round_number_price(str(current_gain)) + ' USDT'
            
            send(message)


    def update_status(self):

        (message, message_id) = get_message_status()

        if message_id == self.last_message_id_status and message.lower() != 'stop':

            return
        
        self.last_message_id_status = message_id

        message = message.lower()

        if message == 'buynow':

            if self.investment_status() == False:

                price_currency = float(self.get_price_currency())
                
                self.buy_currency()

                new_balance_usdt = self.get_balance_usdt()
                new_balance_currency = self.get_balance_currency()

                message = 'Buying complete:\n\n'
                message += 'Investment: buying currency in ' + self.round_number_price(str(price_currency)) + ' USDT\n'
                message += 'Market buying price: ' + self.round_number_price(str(self.investment_order_limit / float(new_balance_currency))) + ' USDT\n'
                message += 'Total balance usdt: ' + self.round_number_price(new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.round_number_price(new_balance_currency) + ' ' + self.currency

                send(message)
            
            else:

                send('Buying canceled... There is already an investment')
        
        elif message == 'sellnow':

            if self.investment_status() == True:

                balance_usdt = float(self.get_balance_usdt())
                balance_currency = float(self.get_balance_currency())
                price_currency = float(self.get_price_currency())
               
                self.sell_currency()

                new_balance_usdt = self.get_balance_usdt()
                new_balance_currency = self.get_balance_currency()

                message = 'Selling complete:\n\n'
                message += 'Selling: selling currency in ' + self.round_number_price(str(price_currency)) + ' USDT\n'
                message += 'Market selling price: ' + self.round_number_price(str((float(new_balance_usdt) - balance_usdt) / balance_currency)) + ' USDT\n'
                message += 'Total balance usdt: ' + self.round_number_price(new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.round_number_price(new_balance_currency) + ' ' + self.currency

                send(message)
            
            else:

                send('Selling canceled... There is no investment right now')
        
        elif message == 'investment':

            self.print_investment_status()

        elif message == 'balance':

            self.print_balance()

        elif message == 'stop':

            send('Bot stopped manually... Waiting')

            while True:

                if get_message_status()[0].lower() == 'start':

                    self.update_constants()

                    send('Bot started manually...')

                    break


    def update(self):

        self.update_status()        
                    
        balance_usdt = float(self.get_balance_usdt())
        balance_currency = float(self.get_balance_currency())
        price_currency = float(self.get_price_currency())
        average_last_prices = self.get_average_last_prices()

        if balance_currency * price_currency < self.eps:

            if price_currency <= average_last_prices:

                self.buy_currency()

                new_balance_usdt = self.get_balance_usdt()
                new_balance_currency = self.get_balance_currency()

                message = 'Buying complete:\n\n'
                message += 'Investment: buying currency in ' + self.round_number_price(str(price_currency)) + ' USDT\n'
                message += 'Market buying price: ' + self.round_number_price(str(self.investment_order_limit / float(new_balance_currency))) + ' USDT\n'
                message += 'Total balance usdt: ' + self.round_number_price(new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.round_number_price(new_balance_currency) + ' ' + self.currency

                send(message)

        else:

            investment_price = self.investment_order_limit / balance_currency
            stop_loss = investment_price * (100 - self.stop_loss_percent) / 100
            take_profit = investment_price * (100 + self.take_profit_percent) / 100

            if price_currency < stop_loss or take_profit < price_currency:

                self.sell_currency()

                new_balance_usdt = self.get_balance_usdt()
                new_balance_currency = self.get_balance_currency()

                message = 'Selling complete:\n\n'

                if price_currency < stop_loss:

                    message += 'Stop loss: selling currency in ' + self.round_number_price(str(price_currency)) + ' USDT\n'

                if take_profit < price_currency:

                    message += 'Take profit: selling currency in ' + self.round_number_price(str(price_currency)) + ' USDT\n'

                message += 'Market selling price: ' + self.round_number_price(str((float(new_balance_usdt) - balance_usdt) / balance_currency)) + ' USDT\n'
                message += 'Total balance usdt: ' + self.round_number_price(new_balance_usdt) + ' USDT\n'
                message += 'Total balance currency: ' + self.round_number_price(new_balance_currency) + ' ' + self.currency

                send(message)


send('Initializing bot...')

B = Bot()

B.print_balance()

while True:

    B.update()