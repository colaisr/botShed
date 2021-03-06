# -*- coding: utf-8 -*-
"""
This Example will show you how to use register_next_step handler.
"""
import logging

import telebot
from telebot import types
import datetime
telebot.logger.setLevel(logging.DEBUG)

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton

API_TOKEN = '1224093712:AAGMlanq-8WRpDOGoPRXG0TYK4gBcuQeSPQ'
START_TIME=8
END_TIME=20

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}


class Order:
    def __init__(self, name):
        self.name = name
        self.date = None
        self.hours = None
        self.minutes=None

def generate_todays_hours():
    # datetime object containing current date and time
    now = datetime.datetime.now()
    current_hour=int(now.strftime("%H"))
    hours=[]
    for h in range(current_hour,END_TIME+1):
        hours.append(str(h))

    return hours


def generate_anyday_hours():

    hours = []
    for h in range(START_TIME, END_TIME + 1):
        hours.append(str(h))

    return hours


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
שלום, מיד נקבע לך חלון, איך אפשר לפנות אליך ?
""")
    bot.register_next_step_handler(msg, process_name_step)



def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        order = Order(name)
        user_dict[chat_id] = order

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('היום', 'מחר')
        msg = bot.reply_to(message, 'איזה יום נוח לך?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_day_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')





def process_day_step(message):
    try:
        chat_id = message.chat.id
        order = user_dict[chat_id]
        day_text = message.text


        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        if day_text=="היום":
            order.date = datetime.date.today()
            markup.add(*generate_todays_hours())
        else:
            order.date = datetime.date.today() + datetime.timedelta(days=1)
            markup.add(*generate_anyday_hours())
        msg = bot.reply_to(message, 'איזה שעה ?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_hour_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_hour_step(message):
    try:
        chat_id = message.chat.id
        order = user_dict[chat_id]
        order.hours = message.text


        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        markup.add("00","15","30","45")

        msg = bot.reply_to(message, 'מתי בדיוק ?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_minutes_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_minutes_step(message):
    try:
        chat_id = message.chat.id
        order = user_dict[chat_id]
        order.minutes = message.text
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        markup.add("עוד ביקור")

        # markup = InlineKeyboardMarkup()
        # markup.row_width = 2
        # markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
        #            InlineKeyboardButton("No", callback_data="cb_no"))
        bot.send_message(chat_id, 'מגניב !' + order.name +' היקר!  '+'\n אנו מחכים לך ב \n'+str(order.date)+ ' '+str(order.hours)+':'+str(order.minutes), reply_markup=markup)
        bot.register_next_step_handler(message, send_welcome)
    except Exception as e:
        bot.reply_to(message, 'oooops')




# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.polling()
