import os

from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from app_exception_control import ExceptionC

class TelegramCommands:

    def init(self, bot1, wallet1):

        self.bot1 = bot1
        self.wallet1 = wallet1

        self.keyboards = {
            'main-menu': [['💰Wallets'], ['🤖Bots'], ['❓Help']],
            'wallets': [[self.wallet1.wallet_name], ['⬅️Back to menu']],
            'wallet1-operations': [['⚖️Balance ' + self.wallet1.wallet_name, '📖History ' + self.wallet1.wallet_name], ['⬅️Back to wallets']],
            'bots': [[self.bot1.bot_name], ['⬅️Back to menu']],
            'bot1-operations': [['✅Start ' + self.bot1.bot_name, '🚫Stop ' + self.bot1.bot_name], ['⚖️Balance ' + self.bot1.bot_name, '📈Investment ' + self.bot1.bot_name], ['🔄Update ' + self.bot1.bot_name, '⬅️Back to bots']],
        }

        self.valid_ids = os.environ['valid_ids'].split(',')
        
        self.telegram_updater = Updater(os.environ['bot_token'], use_context = True)
        self.telegram_handler = self.telegram_updater.dispatcher

        self.telegram_handler.add_handler(CommandHandler('start', self.command_start))

        self.telegram_handler.add_handler(MessageHandler(Filters.text('💰Wallets'), self.show_wallets))
        self.telegram_handler.add_handler(MessageHandler(Filters.text(self.wallet1.wallet_name), self.wallet1_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⚖️Balance ' + self.wallet1.wallet_name), self.wallet1_balance))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('📖History ' + self.wallet1.wallet_name), self.wallet1_history))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🤖Bots'), self.show_bots))
        self.telegram_handler.add_handler(MessageHandler(Filters.text(self.bot1.bot_name), self.bot1_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('✅Start ' + self.bot1.bot_name), self.bot1_start))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🚫Stop ' + self.bot1.bot_name), self.bot1_stop))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⚖️Balance ' + self.bot1.bot_name), self.bot1_balance))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('📈Investment ' + self.bot1.bot_name), self.bot1_investment))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🔄Update ' + self.bot1.bot_name), self.bot1_update))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to menu'), self.command_start))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to wallets'), self.show_wallets))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to bots'), self.show_bots))


    def __init__(self, bot1, wallet1):

        ExceptionC.with_send(self.init, bot1 = bot1, wallet1 = wallet1)


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