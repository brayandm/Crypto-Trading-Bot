import os
import json
import time

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

    return data.pinned_message.text


def get_message_database():

    while True:

        try:

            data = telegram_bot.get_chat(database_channel)

            break

        except:

            send('Function \'get_message_database()\' failed... Attempting again')

    return data.pinned_message.text


class Bot:
    
    currency = 'NEAR'
    symbol = 'NEAR-USDT'
    investment_order_limit = 10
    take_profit_percent = 2.3
    stop_loss_percent = 5.7
    last_prices_limit_time = 12600
    eps = 0.01

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

                data = json.loads(get_message_database())

                self.currency = data['currency']
                self.symbol = data['symbol']
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


    def __init__(self):

        while True:

            try:

                self.update_constants()                

                self.constant_round = self.get_constant_round()   

                break

            except: 

                send('Function \'__init__()\' failed... Attempting again')


    def get_constant_round(self):

        while True:

            try:

                data = self.client_market.get_symbol_list()

                for bucket in data:

                    if bucket['symbol'] == self.symbol:

                        return len(bucket['baseIncrement']) - 2
            
                send('Symbol not found... Bot stopped')

                while True:

                    pass    

            except:

                send('Function \'get_constant_round()\' failed... Attempting again')


    def round_number(self, number):

        cad = str(number)

        point_position = -1

        for i in range(len(cad)):

            if cad[i] == '.':

                point_position = i
        
        if point_position == -1:

            return cad
            
        while point_position + self.constant_round + 1 < len(cad):

            cad = cad[0:-1]
        
        return cad


    def buy_currency(self):

        if float(self.get_balance_usdt()) < self.investment_order_limit:

            send('Insufficient balance to invest... Bot stopped')

            while True:

                pass
        
        while True:

            try:

                self.client_trade.create_market_order(self.symbol, 'buy', funds = self.round_number(self.investment_order_limit))
            
                break

            except:

                send('Function \'buy_currency()\' failed... Attempting again')


    def sell_currency(self):

        balance_currency = self.get_balance_currency()

        while True:

            try:

                self.client_trade.create_market_order(self.symbol, 'sell', size = self.round_number(balance_currency))
            
                break

            except:

                send('Function \'sell_currency()\' failed... Attempting again')


    def get_balance_currency(self):

        while True:

            try:

                data = self.client_user.get_account_list(self.currency, 'trade')

                break

            except:

                send('Function \'get_balance_currency()\' failed... Attempting again')
        
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

        sum = 0
        
        for bucket in data:

            sum += float(bucket[1]) + float(bucket[2])
        
        return sum / (len(data) * 2)

    
    def update(self):

        if get_message_status().lower() == 'stop':

            send('Bot stopped manually... Waiting')

            while True:

                if get_message_status().lower() == 'start':

                    self.update_constants()

                    send('Bot started manually...')

                    break
                    
        balance_currency = float(self.get_balance_currency())
        price_currency = float(self.get_price_currency())
        average_last_prices = self.get_average_last_prices()

        if balance_currency * price_currency < self.eps:

            if price_currency <= average_last_prices:

                self.buy_currency()

                send('Investment: buying currency in ' + str(price_currency) + ' usdt')

        else:

            investment_price = self.investment_order_limit / balance_currency
            stop_loss = investment_price * (100 - self.stop_loss_percent) / 100
            take_profit = investment_price * (100 + self.take_profit_percent) / 100

            if price_currency < stop_loss or take_profit < price_currency:

                self.sell_currency()

                if price_currency < stop_loss:

                    send('Stop loss: selling currency in ' + str(price_currency) + ' usdt')

                if take_profit < price_currency:

                    send('Take profit: selling currency in ' + str(price_currency) + ' usdt')

                send('Total balance: ' + self.get_balance_usdt() + ' usdt')


send('Initializing bot...')

B = Bot()

while True:

    B.update()
