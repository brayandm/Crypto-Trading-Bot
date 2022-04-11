import os

from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from app import wallet
from app import bot

class Telegram:

    def __init__(self):

        self.keyboards = {
            'main-menu': [['💰Wallets'], ['🤖Bots'], ['📑Info']],
            'wallets': [['Wallet #1', "Wallet #2"], ["Wallet #3", 'Wallet #4'], ['⬅️Back to menu']],
            'wallet-operations': [['⚖️Balance', '📖History'], ['⬅️Back to wallets']],
            'bots': [['Bot #1'], ['⬅️Back to menu']],
            'bot1-operations': [['Start Bot #1', 'Stop Bot #1'], ['⬅️Back to bots']],
        }

        self.valid_ids = os.environ['valid_ids'].split(',')
        
        self.telegram_bot = Bot(os.environ['bot_token'])
        self.output_channel = os.environ['output_channel']
        self.status_channel = os.environ['status_channel']
        self.database_channel = os.environ['database_channel']

        self.telegram_updater = Updater(os.environ['bot_token'], use_context = True)
        self.telegram_handler = self.telegram_updater.dispatcher

        self.telegram_handler.add_handler(CommandHandler('start', self.command_start))

        self.telegram_handler.add_handler(MessageHandler(Filters.text('💰Wallets'), self.show_wallets))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to menu'), self.command_start))
        self.telegram_handler.add_handler(MessageHandler(Filters.regex('Wallet #\d+'), self.wallet_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to wallets'), self.show_wallets))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⚖️Balance'), self.show_balance))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('📖History'), self.show_history))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('🤖Bots'), self.show_bots))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('Bot #1'), self.bot1_operations))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('Start Bot #1'), self.bot1_start))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('Stop Bot #1'), self.bot1_stop))
        self.telegram_handler.add_handler(MessageHandler(Filters.text('⬅️Back to bots'), self.show_bots))


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

        update.message.reply_text('Welcome to this bot', reply_markup = reply_markup)


    def show_wallets(self, update, context):
        
        if not self.validate_user(update.message.chat_id): return

        reply_markup = ReplyKeyboardMarkup(self.keyboards['wallets'], resize_keyboard = True)

        update.message.reply_text('Which wallet do you want to check?', reply_markup = reply_markup)


    def wallet_operations(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        message = update.message.text

        reply_markup = ReplyKeyboardMarkup(self.keyboards['wallet-operations'], resize_keyboard = True)

        update.message.reply_text('Select the operation to execute on: <b>' + message + '</b>', reply_markup = reply_markup, parse_mode = 'HTML')


    def show_balance(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        update.message.reply_text('Your balance is 5 CUP')


    def show_history(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        update.message.reply_text('Your order history is clear')


    def show_bots(self, update, context):
        
        if not self.validate_user(update.message.chat_id): return

        reply_markup = ReplyKeyboardMarkup(self.keyboards['bots'], resize_keyboard = True)

        update.message.reply_text('Which bot do you want to check?', reply_markup = reply_markup)


    def bot1_start(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        if bot.turn_on == False:

            bot.turn_on = True

            update.message.reply_text('Bot started manually...')
        
        else:

            update.message.reply_text('Bot is already started...')


    def bot1_stop(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        if bot.turn_on == True:

            bot.turn_on = False

            update.message.reply_text('Bot stopped manually... Waiting')

        else:

            update.message.reply_text('Bot is already stopped... Waiting')


    def bot1_operations(self, update, context):

        if not self.validate_user(update.message.chat_id): return

        message = update.message.text

        reply_markup = ReplyKeyboardMarkup(self.keyboards['bot1-operations'], resize_keyboard = True)
        
        update.message.reply_text('Select the operation to execute on: <b>' + message + '</b>', reply_markup = reply_markup, parse_mode = 'HTML')


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