import os

from telegram import Bot


class Telegram:

    def __init__(self):

        self.telegram_bot = Bot(os.environ['bot_token'])
        self.output_channel = os.environ['output_channel']
        self.status_channel = os.environ['status_channel']
        self.database_channel = os.environ['database_channel']


    def send(self, message):

        print(message)

        while True:

            try:

                self.telegram_bot.send_message(self.output_channel, message)

                break

            except Exception as e:

                print(e)

                print('Function \'send()\' failed... Attempting again')

    
    def get_message_status(self):

        while True:

            try:

                data = self.telegram_bot.get_chat(self.status_channel)

                break

            except Exception as e:

                self.send(e)

                self.send('Function \'get_message_status()\' failed... Attempting again')

        return (data.pinned_message.text, data.pinned_message.message_id)


    def get_message_database(self):

        while True:

            try:

                data = self.telegram_bot.get_chat(self.database_channel)

                break

            except Exception as e:

                self.send(e)

                self.send('Function \'get_message_database()\' failed... Attempting again')

        return (data.pinned_message.text, data.pinned_message.message_id)