from django.core.management.base import BaseCommand
import datetime

import telebot
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telebot.types import Message, CallbackQuery
from django.conf import settings

from app_bot.utils.work_database import add_to_bd
from app_bot.utils.action import Action, calendar, calendar_1_callback, calendar_2_callback, STOP_MESSAGE, \
    input_correct_date

TOKEN = settings.TOKEN
MAIN_COMMANDS = ['/bestdeal', '/lowprice', '/highprice']

CONTENT_TYPES = ['audio', 'photo', 'voice', 'video', 'document',
                 'text', 'location', 'contact', 'sticker']

HELP_COMMANDS = ['/hello-world', '/start', '/help']

bot = telebot.TeleBot(token=TOKEN, threaded=False)


@csrf_exempt
def bot_view(request):
    if request.method != 'POST':
        return HttpResponse(status=403)
    if request.META.get('CONTENT_TYPE') != 'application/json':
        return HttpResponse(status=403)

    json_string = request.body.decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])

    return HttpResponse(status=200)


@bot.message_handler(commands=['hello-world', 'start', 'help'])
def hello_world(message: Message) -> None:
    if message.text in HELP_COMMANDS[:2]:
        next_message = "Приветствую, {0}.\n" \
                       "Выберете одну из следующих команд:\n" \
                       "{1}, {2}, {3}.\n" \
                       "Справка по командам - {4}"
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
        input_correct_date(
            call=call, bot=bot, now=now, calendar_callback=calendar_1_callback
        )
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
        input_correct_date(
            call=call, bot=bot, calendar_callback=calendar_2_callback, now=now
        )
    elif action == 'CANCEL':
        bot.send_message(call.from_user.id, STOP_MESSAGE)


@bot.message_handler(content_types=CONTENT_TYPES)
def answer_to_any_messages(message: Message) -> None:
    bot.send_message(message.chat.id, f'Введите {HELP_COMMANDS[1]}')


class Command(BaseCommand):
    help = 'Запуск бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_SERVER_ERROR(
            f'Бот запущен в {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        )
        bot.polling(none_stop=True, interval=0)
