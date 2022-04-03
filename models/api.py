from datetime import datetime
from kucoin.client import Client

# Gets the trade accounts balances for the backup coin and the trading coin
def get_trade_balances(client: Client, backup_currency: str, trading_currency: str):
    
    back = 0.0
    trade = 0.0

    flag = False
    while flag == False:
        try:
            data = client.get_accounts()
            flag = True
        except:
            print('Balance Failed... Attempting again')
            flag = False
    
    for account in data:
        if account['type'] == 'trade':
            if account['currency'] == backup_currency:
                back = account['balance']
            elif account['currency'] == trading_currency:
                trade = account['balance']

    return [float(back), float(trade)]

# Gets the average price of the past 3 hours
def get_past_average(client: Client, backup_currency: str, trading_currency: str):

    past_date = int(datetime.today().timestamp()) - 60 * 60 * 3
    symbol = trading_currency + '-' + backup_currency

    flag = False
    while flag == False:
        try:
            past_data = client.get_kline_data(symbol, '1min', past_date)
            flag = True
        except:
            print('Kline Failed... Attempting again')
            flag = False

    total = 0.0
    for mark in past_data:
        total += float(mark[1]) + float(mark[2])
    
    average = total / (len(past_data) * 2)
    return average

# Gets the current coin price
def get_current_price(client: Client, backup_currency: str, trading_currency: str):

    symbol = trading_currency + '-' + backup_currency

    flag = False
    while flag == False:
        try:
            price = client.get_24hr_stats(symbol)
            flag = True
        except:
            print('Price Failed... Attempting again')
            flag = False
    
    return float(price['last'])

# Returns the currency price at the moment of the last buy order
def get_last_order_price(client: Client, backup_currency: str, trading_currency: str):

    symbol = trading_currency + '-' + backup_currency

    flag = False
    while flag == False:
        try:
            history = client.get_orders(symbol, 'done', side = 'buy', trade_type = 'TRADE', limit = 10)
            flag = True
        except:
            print('Last Order Failed... Attempting again')
            flag = False

    invested, purchased = ( float(history['items'][0]['dealFunds']), float(history['items'][0]['dealSize']) )
    return invested / purchased
    