from app_telegram import telegram_bot

class ExceptionControl:

    def with_print(self, function, **kwargs):

        while True:

            try:

                return function(**kwargs)

            except Exception as e:

                print(str(e))

                print(str(function) + ' failed... Attempting again')



    def with_send(self, function, **kwargs):

        while True:

            try:

                return function(**kwargs)

            except Exception as e:

                telegram_bot.send(str(e))

                telegram_bot.send(str(function) + ' failed... Attempting again')


ExceptionC = ExceptionControl()