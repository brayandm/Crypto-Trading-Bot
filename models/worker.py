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
        holding(client, backup_currency, trading_currency)

# Compares the past average with the current price and executes the corresponding action
def check_past_prices(client: Client, backup_currency: str, trading_currency: str):

        while True:

            past_average = api.get_past_average(client, backup_currency, trading_currency)
            current_price = api.get_current_price(client, backup_currency, trading_currency)

            print('Average and price: ' + str(past_average), str(current_price))

            if past_average < current_price:
                time.sleep(constant.WAIT_TIME * 3 / 2)
            else:
                symbol = trading_currency + '-' + backup_currency
                back, trade = api.get_trade_balances(client, backup_currency, trading_currency)
                funds = round(back * 2 / 3, constant.INCREMENT)

                client.create_market_order(symbol, 'buy', funds = funds)
                print('Successfully invested ' + str(funds) + ' ' + backup_currency)
                break

        evaluate_balance(client, backup_currency, trading_currency)

# Determines the best moment to sell the currency
def holding(client: Client, backup_currency: str, trading_currency: str):
    
    bought_price = api.get_last_order_price(client, backup_currency, trading_currency)
    upper_limit = bought_price + bought_price / 50
    lower_limit = bought_price - bought_price * 3 / 50
    symbol = trading_currency + '-' + backup_currency

    while True:

        current_price = api.get_current_price(client, backup_currency, trading_currency)

        print('Price and limits: ' + str(current_price), str(upper_limit), str(lower_limit))

        if current_price > upper_limit:
            back, trade = api.get_trade_balances(client, backup_currency, trading_currency)
            rounded = round(round(trade, constant.INCREMENT) - (10 ** -constant.INCREMENT), constant.INCREMENT)
            client.create_limit_order(symbol, 'sell', round(upper_limit, constant.INCREMENT), rounded)
            print('Take Profit: Successfully sold ' + str(rounded) + ' ' + trading_currency)
            break

        elif current_price <= lower_limit:
            back, trade = api.get_trade_balances(client, backup_currency, trading_currency)
            rounded = round(round(trade, constant.INCREMENT) - (10 ** -constant.INCREMENT), constant.INCREMENT)
            client.create_market_order(symbol, 'sell', size = rounded)
            print('Stop Loss: Successfully sold ' + str(rounded) + ' ' + trading_currency)
            break

        else:
            time.sleep(constant.WAIT_TIME)

    evaluate_balance(client, backup_currency, trading_currency)
