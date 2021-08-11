from django.core.management.base import BaseCommand
import datetime

import telebot
from telebot.types import Message, CallbackQuery
from django.conf import settings

from ..work_database import add_to_bd
from ..new_action import Action, calendar, calendar_1_callback, calendar_2_callback, STOP_MESSAGE

TOKEN = settings.TOKEN
MAIN_COMMANDS = ['/bestdeal', '/lowprice', '/highprice']

HELP_COMMANDS = ['/hello-world', '/start', '/help']

bot = telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands=['hello-world', 'start', 'help'])
def hello_world(message: Message) -> None:
    if message.text in HELP_COMMANDS[:2]:
        next_message = "Приветствую, {0}. Выберете одну из следующих команд: {1}, {2}, {3}. Справка по командам - {4}"
        bot.send_message(
            message.chat.id,
            next_message.format(message.from_user.first_name, *MAIN_COMMANDS, HELP_COMMANDS[-1])
        )
    elif message.text == HELP_COMMANDS[-1]:
        bot.send_message(
            message.chat.id,
            '{0} — вывод отелей, наиболее подходящих по цене и расположению от центра\n'
            '{1} — вывод самых дешёвых отелей в городе\n'
            '{2} — вывод самых дорогих отелей в городе\n'
            'стоп — прекращение выполнения команды'.format(*MAIN_COMMANDS)
        )
    else:
        bot.reply_to(
            message,
            'Введите следующие команды для получения информации: {}, {}, {}'.format(*HELP_COMMANDS)
        )


@bot.message_handler(commands=['bestdeal', 'lowprice', 'highprice'])
def input_city(message: Message) -> None:
    city = bot.send_message(message.chat.id, 'Введите город 🏙')
    type_sort = ('DISTANCE_FROM_LANDMARK', 'PRICE', 'PRICE_HIGHEST_PRICE')
    message_to_command = {MAIN_COMMANDS[i]: name_sort for i, name_sort in enumerate(type_sort)}
    add_to_bd(message)
    bot.register_next_step_handler(city, Action(message=message, bot=bot).get_list_cities,
                                   sort_order=message_to_command[message.text])


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def get_date_out(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    now = datetime.datetime.now()
    if action == 'DAY':

        if date > now:
            data_user = Action(message=call, bot=bot).data_user
            data_user.date_in = date
            data_user.save(update_fields=['date_in'])
            bot.send_message(
                call.from_user.id, 'Введите дату выезда',
                reply_markup=calendar.create_calendar(
                    name=calendar_2_callback.prefix, year=now.year, month=now.month
                ))
            return

        bot.send_message(
            call.from_user.id,
            'Укажите корректную дату',
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix, year=now.year, month=now.month
            ))

    elif action == 'CANCEL':
        bot.send_message(call.from_user.id, STOP_MESSAGE)


@bot.callback_query_handler(lambda call: call.data.startswith(calendar_2_callback.prefix))
def finish(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_2_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    now = datetime.datetime.now()
    data_user = Action(message=call, bot=bot).data_user
    if action == 'DAY':

        if date.date() > data_user.date_in:
            data_user.date_out = date
            data_user.save(update_fields=['date_out'])
            Action(call, bot).get_hotels(call)
            return

        bot.send_message(
            call.from_user.id,
            'Укажите корректную дату',
            reply_markup=calendar.create_calendar(
                name=calendar_2_callback.prefix, year=now.year, month=now.month
            ))

    elif action == 'CANCEL':
        bot.send_message(call.from_user.id, STOP_MESSAGE)


CONTENT_TYPES = ['audio', 'photo', 'voice', 'video', 'document',
                 'text', 'location', 'contact', 'sticker']


@bot.message_handler(content_types=CONTENT_TYPES)
def answer_to_any_messages(message: Message) -> None:
    bot.send_message(message.chat.id, f'Введите {HELP_COMMANDS[1]}')


class Command(BaseCommand):
    help = 'Запуск бота'

    def handle(self, *args, **options):
        bot.polling(none_stop=True, interval=0)