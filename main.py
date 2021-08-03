import os

import telebot
from dotenv import load_dotenv
from telebot.types import Message

from action import get_list_cities
from work_database import add_to_bd

load_dotenv()

bot = telebot.TeleBot(token=os.getenv('TOKEN'))

MAIN_COMMANDS = ['/bestdeal', '/lowprice', '/highprice']

HELP_COMMANDS = ['/hello-world', '/start', '/help']


@bot.message_handler(commands=['hello-world', 'start', 'help'])
def hello_world(message: Message) -> None:
    if message.text in HELP_COMMANDS[:2]:
        bot.send_message(
            message.chat.id,
            """Приветствую, {0}. Выберете одну из следующих команд: {1}, {2}, {3}. Справка по командам - {4}""".format(
                message.from_user.first_name, *MAIN_COMMANDS, HELP_COMMANDS[-1])
        )
    elif message.text == HELP_COMMANDS[-1]:
        bot.send_message(message.chat.id,
                         '{0} — вывод отелей, наиболее подходящих по цене и расположению от центра \n'
                         '{1} — вывод самых дешёвых отелей в городе \n'
                         '{2} — вывод самых дорогих отелей в городе \n'
                         'стоп — прекращение выполнения команды'.format(*MAIN_COMMANDS))
    else:
        bot.reply_to(message, 'Введите следующие команды для получения информации: {}, {}, {}'.format(*HELP_COMMANDS))
    add_to_bd(message)


@bot.message_handler(commands=['bestdeal', 'lowprice', 'highprice'])
def input_city(message: Message) -> None:
    city = bot.send_message(message.chat.id, 'Введите город 🏙')
    type_sort = ('DISTANCE_FROM_LANDMARK', 'PRICE', 'PRICE_HIGHEST_PRICE')
    message_to_command = {MAIN_COMMANDS[i]: name_sort for i, name_sort in enumerate(type_sort)}
    bot.register_next_step_handler(city, get_list_cities, bot=bot, sort_order=message_to_command[message.text])


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'])
def func(message: Message) -> None:
    bot.send_message(message.chat.id, 'Введите /start')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
