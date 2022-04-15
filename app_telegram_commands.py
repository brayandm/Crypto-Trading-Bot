import os

from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from app_exception_control import ExceptionC
from app_info import info
from app_database import database

class TelegramCommands:

    def init(self, bot1, bot2, wallet1, wallet2):

        self.bot1 = bot1
        self.bot2 = bot2
        self.wallet1 = wallet1
        self.wallet2 = wallet2

        self.keyboards = {
            'main-menu': [['💰Wallets'], ['🤖Bots'], ['❓Help']],
            'wallets': [[self.wallet1.wallet_name, self.wallet2.wallet_name], ['⬅️Back to menu']],
            'wallet1-operations': [['⚖️Balance ' + self.wallet1.wallet_name, '📖History ' + self.wallet1.wallet_name], ['⬅️Back to wallets']],
            'wallet2-operations': [['⚖️Balance ' + self.wallet2.wallet_name, '📖History ' + self.wallet2.wallet_name], ['⬅️Back to wallets']],
            'bots': [[self.bot1.bot_name, self.bot2.bot_name], ['⬅️Back to menu']],
            'bot1-operations': [['✅Start ' + self.bot1.bot_name, '🚫Stop ' + self.bot1.bot_name], ['⚖️Balance ' + self.bot1.bot_name, '📈Investment ' + self.bot1.bot_name], ['🔄Update ' + self.bot1.bot_name, '⬅️Back to bots']],
            'bot2-operations': [['✅Start ' + self.bot2.bot_name, '🚫Stop ' + self.bot2.bot_name], ['⚖️Balance ' + self.bot2.bot_name, '📈Investment ' + self.bot2.bot_name], ['🔄Update ' + self.bot2.bot_name, '⬅️Back to bots']],
        }

        self.valid_ids = os.environ['valid_ids'].split(',')
        
        self.telegram_updater = Updater(os.environ['bot_token'], use_context = True)
        self.telegram_handler = self.telegram_updater.dispatcher

        self.telegram_handler.add_handler(CommandHandler('start', self.command_start))
        self.telegram_handler.add_handler(CommandHandler('reboot', self.command_reboot))
        self.telegram_handler.add_handler(CommandHandler('price', self.command_price))
        self.telegram_handler.add_handler(CommandHandler('plot', self.command_plot))
        self.telegram_handler.add_handler(CommandHandler('get', self.command_get))
        self.telegram_handler.add_handler(CommandHandler('dbclear', self.command_dbclear))
        self.telegram_handler.add_handler(CommandHandler('dbupdate', self.command_dbupdate))
        self.telegram_handler.add_handler(CommandHandler('dbdelete', self.command_dbdelete))


        self.telegram_handler.add_handler(MessageHandler(Filters.text('💰Wallets'), self.show_wallets))

        self.telegram_handler.add_handler(MessageHandler(Filters.text(self.wallet1.wallet_name), self.wallet1_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⚖️Balance ' + self.wallet1.wallet_name), self.wallet1_balance))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('📖History ' + self.wallet1.wallet_name), self.wallet1_history))

        self.telegram_handler.add_handler(MessageHandler(Filters.text(self.wallet2.wallet_name), self.wallet2_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⚖️Balance ' + self.wallet2.wallet_name), self.wallet2_balance))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('📖History ' + self.wallet2.wallet_name), self.wallet2_history))


        self.telegram_handler.add_handler(MessageHandler(Filters.text('🤖Bots'), self.show_bots))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('❓Help'), self.show_help))

        self.telegram_handler.add_handler(MessageHandler(Filters.text(self.bot1.bot_name), self.bot1_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('✅Start ' + self.bot1.bot_name), self.bot1_start))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🚫Stop ' + self.bot1.bot_name), self.bot1_stop))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⚖️Balance ' + self.bot1.bot_name), self.bot1_balance))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('📈Investment ' + self.bot1.bot_name), self.bot1_investment))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🔄Update ' + self.bot1.bot_name), self.bot1_update))

        self.telegram_handler.add_handler(MessageHandler(Filters.text(self.bot2.bot_name), self.bot2_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('✅Start ' + self.bot2.bot_name), self.bot2_start))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🚫Stop ' + self.bot2.bot_name), self.bot2_stop))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⚖️Balance ' + self.bot2.bot_name), self.bot2_balance))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('📈Investment ' + self.bot2.bot_name), self.bot2_investment))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🔄Update ' + self.bot2.bot_name), self.bot2_update))


        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to menu'), self.command_start))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to wallets'), self.show_wallets))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to bots'), self.show_bots))


    def __init__(self, bot1, bot2, wallet1, wallet2):

        ExceptionC.with_send(self.init, bot1 = bot1, bot2 = bot2, wallet1 = wallet1, wallet2 = wallet2)


    def listen(self):

        self.telegram_updater.start_polling()


    def validate_user(self, id):

        for valid_id in self.valid_ids:

            if int(id) == int(valid_id):

                return True

        return False


    def command_start(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        reply_markup = ReplyKeyboardMarkup(self.keyboards['main-menu'], resize_keyboard = True)

        update.message.reply_text('Welcome to the Jungle', reply_markup = reply_markup)


    def command_reboot(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        update.message.reply_text('Rebooting the system')

        os._exit(os.EX_OK)

    
    def command_price(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        currency = update.message.text.split()[1].upper()
        price = info.get_price_currency(currency)

        if price == None:

            update.message.reply_text('The currency is invalid')
        
        else:

            update.message.reply_text('The price of ' + currency + ' is ' + price + ' USDT')


    def command_plot(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        currency = update.message.text.split()[1].upper()

        try:
        
            days = update.message.text.split()[2].upper()

            filename = str(update.message.chat_id) + '_' + str(update.message.message_id) + '.png'

            info.generate_image_currency_prices(currency, filename, days)

            update.message.reply_photo(open(filename, 'rb'))
            os.remove(filename)

        except:

            filename = str(update.message.chat_id) + '_' + str(update.message.message_id) + '.png'

            info.generate_image_currency_prices(currency, filename)

            update.message.reply_photo(open(filename, 'rb'))
            os.remove(filename)


    def command_get(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        currency = update.message.text.split()[1].upper()

        try:
        
            days = update.message.text.split()[2].upper()

            filename = currency + '_' + days + '_' + str(database.get_last_minutes_prices()['time']) + '_' + str(update.message.chat_id) + '_' + str(update.message.message_id) + '.txt'

            data = database.get_currency_days_before(currency, days)
        
            file = open(filename, 'w')
            
            for price in data:

                file.write(str(price) + '\n')

            file.close()

            update.message.reply_document(open(filename, 'r'))
            os.remove(filename)

        except:

            filename = currency + '_' + str(database.get_last_minutes_prices()['time']) + '_' + str(update.message.chat_id) + '_' + str(update.message.message_id) + '.txt'

            data = database.get_currency(currency)
        
            file = open(filename, 'w')
            
            for price in data:

                file.write(str(price) + '\n')

            file.close()

            update.message.reply_document(open(filename, 'r'))
            os.remove(filename)

    
    def command_dbclear(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        database.clear()

        update.message.reply_text('The database was cleaned')


    def command_dbupdate(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        currency = update.message.text.split()[1].upper()

        try:
        
            days = update.message.text.split()[2].upper()

            database.update_currency_days_before(currency, days)

            update.message.reply_text('The ' + currency + ' database was updated with the last ' + days + ' days')

        except:

            database.update_currency(currency)
            
            update.message.reply_text('The ' + currency + ' database was updated up to this point')


    def command_dbdelete(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        currency = update.message.text.split()[1].upper()

        try:
        
            days = update.message.text.split()[2].upper()

            database.delete_currency_days_before(currency, days)

            update.message.reply_text('The ' + currency + ' database only kept the information ' + days + ' days ago, the rest was deleted')

        except:

            database.delete_currency(currency)
            
            update.message.reply_text('The ' + currency + ' database was deleted')
        

    def show_help(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        message = ''
        message += 'List of commands:\n\n'
        message += '/start\n'
        message += '/reboot\n'
        message += '/price [currency]\n'
        message += '/plot [currency] [days]\n'
        message += '/get [currency] [days]\n'
        message += '/dbclear\n'
        message += '/dbupdate [currency] [days]\n'
        message += '/dbdelete [currency] [days]\n'

        update.message.reply_text(message)


    def show_wallets(self, update, context):
        
        if not self.validate_user(update.message.chat_id): return

        reply_markup = ReplyKeyboardMarkup(self.keyboards['wallets'], resize_keyboard = True)

        update.message.reply_text('Which wallet do you want to check?', reply_markup = reply_markup)


    def wallet1_operations(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        message = update.message.text

        reply_markup = ReplyKeyboardMarkup(self.keyboards['wallet1-operations'], resize_keyboard = True)

        update.message.reply_text('Select the operation to execute on: <b>' + message + '</b>', reply_markup = reply_markup, parse_mode = 'HTML')


    def wallet1_balance(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        data = self.wallet1.get_balance_total()

        message = 'Your balance in ' + self.wallet1.wallet_name + ' is:\n\n'

        for key in data:

            message += data[key] + ' ' + key + '\n'
    
        update.message.reply_text(message)


    def wallet1_history(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        update.message.reply_text('Your order history in ' + self.wallet1.wallet_name + ' is clear')

    
    def wallet2_operations(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        message = update.message.text

        reply_markup = ReplyKeyboardMarkup(self.keyboards['wallet2-operations'], resize_keyboard = True)

        update.message.reply_text('Select the operation to execute on: <b>' + message + '</b>', reply_markup = reply_markup, parse_mode = 'HTML')


    def wallet2_balance(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        data = self.wallet2.get_balance_total()

        message = 'Your balance in ' + self.wallet2.wallet_name + ' is:\n\n'

        for key in data:

            message += data[key] + ' ' + key + '\n'
    
        update.message.reply_text(message)


    def wallet2_history(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        update.message.reply_text('Your order history in ' + self.wallet2.wallet_name + ' is clear')


    def show_bots(self, update, context):
        
        if not self.validate_user(update.message.chat_id): return

        reply_markup = ReplyKeyboardMarkup(self.keyboards['bots'], resize_keyboard = True)

        update.message.reply_text('Which bot do you want to check?', reply_markup = reply_markup)


    def bot1_start(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        if self.bot1.is_turn_on() == False:

            self.bot1.change_state_turn_on()

            update.message.reply_text(self.bot1.bot_name + ' started manually...')
        
        else:

            update.message.reply_text(self.bot1.bot_name + ' is already started...')


    def bot1_stop(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        if self.bot1.is_turn_on() == True:

            self.bot1.change_state_turn_on()

            update.message.reply_text(self.bot1.bot_name + ' stopped manually... Waiting')

        else:

            update.message.reply_text(self.bot1.bot_name + ' is already stopped... Waiting')


    def bot1_balance(self, update, context):

        if not self.validate_user(update.message.chat_id): return
        
        update.message.reply_text(self.bot1.print_balance())


    def bot1_investment(self, update, context):

        if not self.validate_user(update.message.chat_id): return
        
        update.message.reply_text(self.bot1.print_investment_status())


    def bot1_update(self, update, context):

        if not self.validate_user(update.message.chat_id): return
        
        update.message.reply_text(self.bot1.update_with_database())
        

    def bot1_operations(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        message = update.message.text

        reply_markup = ReplyKeyboardMarkup(self.keyboards['bot1-operations'], resize_keyboard = True)
        
        update.message.reply_text('Select the operation to execute on: <b>' + message + '</b>', reply_markup = reply_markup, parse_mode = 'HTML')

    
    def bot2_start(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        if self.bot2.is_turn_on() == False:

            self.bot2.change_state_turn_on()

            update.message.reply_text(self.bot2.bot_name + ' started manually...')
        
        else:

            update.message.reply_text(self.bot2.bot_name + ' is already started...')


    def bot2_stop(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        if self.bot2.is_turn_on() == True:

            self.bot2.change_state_turn_on()

            update.message.reply_text(self.bot2.bot_name + ' stopped manually... Waiting')

        else:

            update.message.reply_text(self.bot2.bot_name + ' is already stopped... Waiting')


    def bot2_balance(self, update, context):

        if not self.validate_user(update.message.chat_id): return
        
        update.message.reply_text(self.bot2.print_balance())


    def bot2_investment(self, update, context):

        if not self.validate_user(update.message.chat_id): return
        
        update.message.reply_text(self.bot2.print_investment_status())


    def bot2_update(self, update, context):

        if not self.validate_user(update.message.chat_id): return
        
        update.message.reply_text(self.bot2.update_with_database())
        

    def bot2_operations(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        message = update.message.text

        reply_markup = ReplyKeyboardMarkup(self.keyboards['bot2-operations'], resize_keyboard = True)
        
        update.message.reply_text('Select the operation to execute on: <b>' + message + '</b>', reply_markup = reply_markup, parse_mode = 'HTML')