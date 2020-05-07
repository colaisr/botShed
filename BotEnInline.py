# This example show how to write an inline mode telegram bot use pyTelegramBotAPI.
import datetime
import logging
import sys
import time

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '1224093712:AAGMlanq-8WRpDOGoPRXG0TYK4gBcuQeSPQ'
START_TIME = 8
END_TIME = 20

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}


class Order:
    def __init__(self, name):
        self.name = name
        self.date = None
        self.hours = None
        self.minutes = None


telebot.logger.setLevel(logging.DEBUG)


def generate_todays_hours():
    now = datetime.datetime.now()
    current_hour = int(now.strftime("%H"))
    hours = []
    i = 0
    buttons_row = []
    markup = types.InlineKeyboardMarkup()
    for h in range(current_hour, END_TIME + 1):
        if i % 3 != 0 and i != 0:
            buttons_row.append(InlineKeyboardButton(h, callback_data=h))
        else:
            markup.add(*buttons_row)
            buttons_row.clear()
            buttons_row.append(InlineKeyboardButton(h, callback_data=h))
        i = i + 1
    if len(buttons_row) > 0:
        markup.add(*buttons_row)
    return markup


def generate_anyday_hours():
    hours = []
    i = 0
    buttons_row = []
    markup = types.InlineKeyboardMarkup()
    for h in range(START_TIME, END_TIME + 1):
        if i % 3 != 0 and i != 0:
            buttons_row.append(InlineKeyboardButton(h, callback_data=h))
        else:
            markup.add(*buttons_row)
            buttons_row.clear()
            buttons_row.append(InlineKeyboardButton(h, callback_data=h))
        i = i + 1
    if len(buttons_row) > 0:
        markup.add(*buttons_row)
    return markup


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Lets schedule a window for You,
which name to use ?
""")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        order = Order(name)
        user_dict[chat_id] = order

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Today", callback_data="cb_today"),
                   InlineKeyboardButton("Tomorrow", callback_data="cb_tomorrow"))
        msg = bot.reply_to(message, 'Which day you prefer ?', reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, 'oooops')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        chat_id = call.from_user.id
        order = user_dict[chat_id]

        if call.data == "cb_today":
            order.date = datetime.date.today()
            bot.answer_callback_query(call.id, "Today selected")

            available_hours = generate_todays_hours()
            markup = InlineKeyboardMarkup()

            for h in available_hours:
                markup.add((InlineKeyboardButton(h, callback_data=h)))

        elif call.data == "cb_tomorrow":
            order.date = datetime.date.today() + datetime.timedelta(days=1)
            bot.answer_callback_query(call.id, "Tomorrow selected")
            markup = generate_anyday_hours()

        bot.send_message(chat_id, "Which time ?", reply_markup=markup)
    except Exception as e:
        print(e)


# ------------------------------------------------------


def main_loop():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)
