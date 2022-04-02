from kucoin.client import Client

from models import api, constant

# Gets the currencies balances and determines if it's holding trade coin or not
def evaluate_balance(client: Client, backup_currency: str, trading_currency: str):

    back, trade = api.get_trade_balances(client, backup_currency, trading_currency)

    if trade < constant.EPSILON:
        check_past_prices(client, backup_currency, trading_currency)

# Compares the past average with the current price and executes the corresponding action
def check_past_prices(client: Client, backup_currency: str, trading_currency: str):

        past_average = api.get_past_average(client, backup_currency, trading_currency)
        current_price = api.get_current_price(client, backup_currency, trading_currency)
        
        print(past_average, current_price)

