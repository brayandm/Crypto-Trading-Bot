import json

from app_telegram import telegram_bot


class Database:

    def exists_database_path(self, *args):

        data = json.loads(telegram_bot.get_message_database()[0])

        for path in args:

            try:

                data = data[path]

            except:

                return False

        return True


    def get_database_path(self, *args):

        data = json.loads(telegram_bot.get_message_database()[0])

        for path in args:

            data = data[path]

        return data


    def write_database_path(self, *args):

        if len(args) == 0:

            return

        def recursive_write_database_path(data, *args):

            if len(args) == 1:

                return args[0]

            try:

                data[args[0]]

            except:

                data[args[0]] = {}

            data[args[0]] = recursive_write_database_path(data[args[0]], *args[1:])

            return data

        data = recursive_write_database_path(json.loads(telegram_bot.get_message_database()[0]), *args)

        telegram_bot.edit_message_database(json.dumps(data))


database = Database()