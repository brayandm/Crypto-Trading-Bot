import threading
import os

from exchanges.kucoin import Kucoin
from bots.bot import Bot
from app_telegram import telegram_bot

api_key = os.environ['api_key']
api_secret = os.environ['api_secret']
api_passphrase = os.environ['api_passphrase']
is_sandbox = True if os.environ['is_sandbox'] == 'yes' else False

wallet = Kucoin(api_key, api_secret, api_passphrase, is_sandbox)
bot = Bot(wallet)

thread1 = threading.Thread(target=bot.start_bot)
thread2 = threading.Thread(target=telegram_bot.listen)

thread1.start()
thread2.start()

thread1.join()
thread2.join()