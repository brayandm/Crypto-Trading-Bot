from app_telegram import telegram_bot

class ExceptionControl:

    def stop_bot(self):

        while True:

            pass
        

    def check_stop(self):

        if telegram_bot.get_message_status()[0].lower() == 'stop':

            telegram_bot.send('Bot stopped manually... Waiting')

            while True:

                if telegram_bot.get_message_status()[0].lower() == 'start':

                    telegram_bot.send('Bot started manually...')

                    break


    def with_print(self, function, **kwargs):

        while True:

            self.check_stop()
            
            try:

                return function(**kwargs)

            except Exception as e:

                print(str(e))

                print(str(function) + ' failed... Attempting again')



    def with_send(self, function, **kwargs):

        while True:

            self.check_stop()
            
            try:

                return function(**kwargs)

            except Exception as e:

                telegram_bot.send(str(e))

                telegram_bot.send(str(function) + ' failed... Attempting again')


ExceptionC = ExceptionControl()