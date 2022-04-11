import os

from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class Telegram:

    def __init__(self):

        self.telegram_bot = Bot(os.environ['bot_token'])
        self.output_channel = os.environ['output_channel']
        self.status_channel = os.environ['status_channel']
        self.database_channel = os.environ['database_channel']


    def exception_control_only_print(self, function, **kwargs):

        while True:

            try:

                return function(**kwargs)

            except Exception as e:

                print(str(e))

                print(str(function) + ' failed... Attempting again')


    def exception_control(self, function, **kwargs):

        while True:

            try:

                return function(**kwargs)

            except Exception as e:

                self.send(str(e))

                self.send(str(function) + ' failed... Attempting again')


    def send(self, message):

        print(message)

        self.exception_control_only_print(self.telegram_bot.send_message, chat_id = self.output_channel, text = message)

    
    def get_message_status(self):

        data = self.exception_control(self.telegram_bot.get_chat, chat_id = self.status_channel)

        return (data.pinned_message.text, data.pinned_message.message_id)


    def get_message_database(self):

        data = self.exception_control(self.telegram_bot.get_chat, chat_id = self.database_channel)

        return (data.pinned_message.text, data.pinned_message.message_id)


telegram_bot = Telegram()