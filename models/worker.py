import time
from kucoin.client import Client

from models import api, constant

# Gets the currencies balances and determines if it's holding trade coin or not
def evaluate_balance(client: Client, backup_currency: str, trading_currency: str):

    time.sleep(10) # Give time to the DB to refresh and avoid double purchases

    back, trade = api.get_trade_balances(client, backup_currency, trading_currency)

    # Not holding
    if trade < constant.EPSILON:
        check_past_prices(client, backup_currency, trading_currency)
    else:
        print('Preparing holding status')

# Compares the past average with the current price and executes the corresponding action
def check_past_prices(client: Client, backup_currency: str, trading_currency: str):

        while True:

            past_average = api.get_past_average(client, backup_currency, trading_currency)
            current_price = api.get_current_price(client, backup_currency, trading_currency)

            if past_average < current_price:
                time.sleep(constant.WAIT_TIME)
            else:
                symbol = trading_currency + '-' + backup_currency
                back, trade = api.get_trade_balances(client, backup_currency, trading_currency)
                funds = round(back * 2 / 3, constant.INCREMENT)

                client.create_market_order(symbol, 'buy', funds = funds)
                print('Successfully invested ' + str(funds) + ' ' + backup_currency)
                break

        evaluate_balance(client, backup_currency, trading_currency)
        
