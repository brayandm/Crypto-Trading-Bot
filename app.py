import os
from kucoin.client import Client

from models import api, worker

# Environment variables
api_key = os.environ['api_key']
api_secret = os.environ['api_secret']
api_passphrase = os.environ['api_passphrase']
api_is_sandbox = False if os.environ['environment'] == 'production' else True
backup_currency = os.environ['backup_currency']
trading_currency = os.environ['trading_currency']

# Connecting to the API
client = Client(api_key, api_secret, api_passphrase, sandbox = api_is_sandbox)

worker.evaluate_balance(client, backup_currency, trading_currency)