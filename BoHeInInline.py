# This example show how to write an inline mode telegram bot use pyTelegramBotAPI.
import datetime
import sys

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_calendar import set_event
from bot_db import update_stat

API_TOKEN = '1224093712:AAGMlanq-8WRpDOGoPRXG0TYK4gBcuQeSPQ'
START_TIME = 8
END_TIME = 20
UPDATE_CALENDAR = True

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}


class Order:
    def __init__(self, name):
        self.name = name
        self.date = "None"
        self.hours = "None"
        self.minutes = "None"
        self.phone = "None"


# service functions
def add_reset(markup):
    new_row = []
    new_row.append(InlineKeyboardButton("התחל מחדש", callback_data="cb_restart"))
    markup.add(*new_row)
    return markup


def generate_todays_hours():
    now = datetime.datetime.now()
    current_hour = int(now.strftime("%H"))
    hours = []
    i = 0
    buttons_row = []
    markup = types.InlineKeyboardMarkup()
    for h in range(current_hour, END_TIME + 1):
        if i % 3 != 0 and i != 0:
            buttons_row.append(InlineKeyboardButton(h, callback_data="cb_hours_" + str(h)))
        else:
            markup.add(*buttons_row)
            buttons_row.clear()
            buttons_row.append(InlineKeyboardButton(h, callback_data="cb_hours_" + str(h)))
        i = i + 1
    if len(buttons_row) > 0:
        markup.add(*buttons_row)
    return markup


def generate_anyday_hours():
    i = 0
    buttons_row = []
    markup = types.InlineKeyboardMarkup()
    for h in range(START_TIME, END_TIME + 1):
        if i % 3 != 0 and i != 0:
            buttons_row.append(InlineKeyboardButton(h, callback_data="cb_hours_" + str(h)))
        else:
            markup.add(*buttons_row)
            buttons_row.clear()
            buttons_row.append(InlineKeyboardButton(h, callback_data="cb_hours_" + str(h)))
        i = i + 1
    if len(buttons_row) > 0:
        markup.add(*buttons_row)
    return markup


def generate_minutes():
    buttons_row = []
    markup = types.InlineKeyboardMarkup()
    buttons_row.append(InlineKeyboardButton("00", callback_data="cb_minutes_00"))
    buttons_row.append(InlineKeyboardButton("15", callback_data="cb_minutes_15"))
    markup.add(*buttons_row)
    buttons_row.clear()
    buttons_row.append(InlineKeyboardButton("30", callback_data="cb_minutes_30"))
    buttons_row.append(InlineKeyboardButton("45", callback_data="cb_minutes_45"))
    markup.add(*buttons_row)

    return markup


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
    מייד נזמין לך תור ! מה שמך ?
    """)
    bot.register_next_step_handler(msg, process_name_step)
    update_stat(Order("empty"), message.from_user, True)


# on restart
def restart_the_flow(call):
    chat_id = call.from_user.id
    msg = bot.send_message(chat_id, """\
    מייד נזמין לך תור ! מה שמך ?
    """)
    update_stat(Order("empty"), call.from_user, True)

    bot.register_next_step_handler(msg, process_name_step)


# steps
def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        order = Order(name)
        user_dict[chat_id] = order
        update_stat(order, message.from_user)

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("היום", callback_data="cb_day_today"),
                   InlineKeyboardButton("מחר", callback_data="cb_day_tomorrow"))
        markup = add_reset(markup)
        msg = bot.reply_to(message, 'איזה יום נוח לך?', reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_day_step(call):
    chat_id = call.from_user.id
    order = user_dict[chat_id]

    call.data = call.data.replace("cb_day_", "")
    markup = InlineKeyboardMarkup()
    if call.data == "today":
        order.date = datetime.date.today()
        bot.answer_callback_query(call.id, "Today selected")
        markup = generate_todays_hours()


    elif call.data == "tomorrow":
        order.date = datetime.date.today() + datetime.timedelta(days=1)
        bot.answer_callback_query(call.id, "Tomorrow selected")
        markup = generate_anyday_hours()
    markup = add_reset(markup)
    bot.send_message(chat_id, "איזה שעה ?", reply_markup=markup)
    update_stat(order, call.from_user)


def process_hours_step(call):
    chat_id = call.from_user.id
    order = user_dict[chat_id]

    call.data = call.data.replace("cb_hours_", "")
    order.hours = call.data

    markup = generate_minutes()
    markup = add_reset(markup)
    bot.send_message(chat_id, "מתי בדיוק ?", reply_markup=markup)
    update_stat(order, call.from_user)


def process_minutes_step(call):
    chat_id = call.from_user.id
    order = user_dict[chat_id]

    call.data = call.data.replace("cb_minutes_", "")
    order.minutes = call.data

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.KeyboardButton(text="שלח מספר שלי", request_contact=True))

    msg = bot.send_message(chat_id, "מה מספר הטלפון ?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_phone_step)
    update_stat(order, call.from_user)


def process_phone_step(message):
    try:
        chat_id = message.chat.id
        order = user_dict[chat_id]
        if message.contact is None:
            order.phone = message.text
        else:
            order.phone = message.contact.phone_number
        finalize_the_order(message)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def finalize_the_order(call):
    chat_id = call.from_user.id
    order = user_dict[chat_id]
    markup = InlineKeyboardMarkup()
    markup = add_reset(markup)
    bot.send_message(chat_id,
                     'מגניב !' + order.name + ' היקר!  ' + '\n אנו מחכים לך ב \n' + str(order.date) + ' ' + str(
                         order.hours) + ':' + str(order.minutes), reply_markup=markup)

    update_stat(order, call.from_user, close_record=True)
    if UPDATE_CALENDAR:
        try:
            set_event(order)
        except Exception as e:
            print(e)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if "cb_day" in call.data:
            process_day_step(call)
        elif "cb_hours_" in call.data:
            process_hours_step(call)
        elif "cb_minutes_" in call.data:
            process_minutes_step(call)
        elif "cb_restart" in call.data:
            restart_the_flow(call)






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
