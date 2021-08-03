import datetime

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message

from get_any_data import get_cities, get_destination_id, hotels


def get_list_cities(message: Message, bot: TeleBot, sort_order: str) -> None:
    """
    ПОлучение списка городов
    :param message:
    :param bot:
    :param sort_order:
    :return:
    """
    if message.text.lower() == 'стоп':
        bot.send_message(message.chat.id, 'Останавливаю работу 📛...')
        return
    rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    bot.send_message(message.chat.id, 'Думаю, подождите...')
    cities = get_cities(message.text)
    if not cities:
        msg = bot.reply_to(message, 'Введенный город не найден, попробуйте еще раз ❗️')
        bot.register_next_step_handler(msg, get_list_cities, bot=bot, sort_order=sort_order)
        return
    for el in cities:
        rmk.add(KeyboardButton(el))
    city = bot.send_message(message.chat.id, 'Уточните город', reply_markup=rmk)
    bot.register_next_step_handler(city, get_city_by_destination_id, bot=bot, sort_order=sort_order)


def get_city_by_destination_id(message: Message, bot: TeleBot, sort_order: str) -> None:
    """
    Получение конкретного города
    :param message:
    :param bot:
    :param sort_order:
    :return:
    """
    if message.text.lower() == 'стоп':
        bot.send_message(message.chat.id, 'Останавливаю работу 📛...')
        return
    bot.send_message(message.chat.id, 'Секунду, всё уточню ⏳')
    destination_id = get_destination_id(message.text)

    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(1, 11):
        reply_markup.add(KeyboardButton(i))

    count_hotels = bot.send_message(message.chat.id, 'Укажите количество отелей\n'
                                                     '(не больше 10) ❗️', reply_markup=reply_markup)
    bot.register_next_step_handler(count_hotels, get_date, bot=bot, destination_id=destination_id,
                                   sort_order=sort_order)


def get_date(message: Message, bot: TeleBot, destination_id: str, sort_order: str) -> None:
    """
    Получение даты заезда - выезда
    :param message:
    :param bot:
    :param destination_id:
    :param sort_order:
    :return:
    """
    if message.text.lower() == 'стоп':
        bot.send_message(message.chat.id, 'Останавливаю работу 📛...')
        return
    count_hotels = message.text
    if not count_hotels.isdigit() or not 10 >= int(count_hotels) > 0:
        msg = bot.reply_to(message, 'Введите количество отелей (не больше 10) ❗️')
        bot.register_next_step_handler(msg, get_date, bot=bot, sort_order=sort_order, destination_id=destination_id)
        return
    date = bot.send_message(message.chat.id, 'Введите дату в формате: дата заселения-дата выезда.\n'
                                             'Пример, 2020.12.31-2021.01.31 ')
    if sort_order == 'DISTANCE_FROM_LANDMARK':
        bot.register_next_step_handler(date, get_price, bot=bot, count_hotels=count_hotels,
                                       destination_id=destination_id)
        return
    bot.register_next_step_handler(date, get_hotels, bot=bot, count_hotels=count_hotels,
                                   destination_id=destination_id, sort_order=sort_order)


def get_hotels(message: Message, bot: TeleBot, count_hotels: str, destination_id, sort_order: str) -> None:
    """
    Выдача юзеру отелей
    :param message:
    :param bot:
    :param count_hotels:
    :param destination_id:
    :param sort_order:
    :return:
    """
    if message.text.lower() == 'стоп':
        bot.send_message(message.chat.id, 'Останавливаю работу 📛...')
        return
    dates = check_date(message=message)
    if not dates:
        msg = bot.reply_to(message, 'Неверный формат даты❗️ Будьте внимательней❗️\n'
                                    'Пример, 2020.12.31-2021.01.31')
        bot.register_next_step_handler(msg, get_hotels, bot=bot, count_hotels=count_hotels,
                                       destination_id=destination_id,
                                       sort_order=sort_order)
        return
    bot.send_message(message.chat.id, 'Минутку')
    my_hotels = hotels(destination_id, page_size=count_hotels, sort_order=sort_order,
                       date_in=dates[0].date(), date_out=dates[1].date())
    if my_hotels:
        for hotel in my_hotels:
            bot.send_message(message.chat.id,
                             'Название 🏨 - {0}\nКоличество звезд ⭐️- {1}\nАдрес 🌆- {2}\n'
                             'Расстояние от центра 🚘- {3}\n'
                             'Цена 💵 - {4}'.format(*hotel))
    else:
        bot.send_message(message.chat.id, 'По заданным критериям ничего не найдено ☹️')


# Ниже функции для команды bestdeal

def get_price(message: Message, bot: TeleBot, destination_id: str, count_hotels: str) -> None:
    """
    Получение диапазона цен
    :param message:
    :param bot:
    :param count_hotels:
    :param destination_id:
    :return:
    """
    if message.text.lower() == 'стоп':
        bot.send_message(message.chat.id, 'Останавливаю работу 📛...')
        return
    dates = check_date(message=message)
    if not dates:
        msg = bot.reply_to(message, 'Неверный формат даты❗️ Будьте внимательней❗️\n'
                                    'Пример, 2020.12.31-2021.01.31')
        bot.register_next_step_handler(msg, get_price, bot=bot, count_hotels=count_hotels,
                                       destination_id=destination_id, )
        return
    price = bot.send_message(message.chat.id, 'Укажите диапазон цен в рублях 💰💰💰\n'
                                              'Пример, 5000-10000')
    bot.register_next_step_handler(price, get_distance, bot=bot, destination_id=destination_id,
                                   dates=dates, count_hotels=count_hotels)


def get_distance(message: Message, bot: TeleBot, destination_id: str,
                 dates: tuple, count_hotels) -> None:
    """
    Получение расстояния от центра
    :param message:
    :param bot:
    :param count_hotels:
    :param destination_id:
    :param dates:
    :return:
    """
    if message.text.lower() == 'стоп':
        bot.send_message(message.chat.id, 'Останавливаю работу 📛...')
        return
    price = tuple(map(int, filter(lambda x: x.isdigit(), message.text.split('-'))))
    if len(price) != 2 or price[0] > price[1] or price[0] <= 0 or price[1] <= 0:
        msg = bot.reply_to(message, 'Ценовой диапазон указан не корректно❗️\n'
                                    'Пример, 5000-10000')
        bot.register_next_step_handler(msg, get_distance, bot=bot, destination_id=destination_id,
                                       dates=dates, count_hotels=count_hotels)
        return

    distance = bot.send_message(message.chat.id,
                                'А теперь введите желаемое максимальное расстояние (в км) проживания от центра '
                                'заданого города!\nПример, 5')
    bot.register_next_step_handler(distance, get_hotels_for_best_deal, bot=bot, destination_id=destination_id,
                                   dates=dates, price=price, count_hotels=count_hotels)


def get_hotels_for_best_deal(message: Message, bot: TeleBot, destination_id: str,
                             dates: tuple, count_hotels: str, price: tuple) -> None:
    """
    Выдача юзеру отелей по команде /bestdeal
    :return:
    """
    if message.text.lower() == 'стоп':
        bot.send_message(message.chat.id, 'Останавливаю работу 📛...')
        return
    distance = message.text
    if not distance.isdigit() or float(distance) < 0:
        msg = bot.reply_to(message, 'Не корректно указано расстояние❗️ Попробуйте еще раз')
        bot.register_next_step_handler(msg, get_hotels_for_best_deal, bot=bot, destination_id=destination_id,
                                       dates=dates, price=price, count_hotels=count_hotels)
        return
    bot.send_message(message.chat.id, 'Минутку 🦖')
    my_hotels = hotels(destination_id, page_size=count_hotels, sort_order='DISTANCE_FROM_LANDMARK',
                       date_in=dates[0].date(), date_out=dates[1].date(), price_min=price[0], price_max=price[1],
                       distance_from_centr=float(distance))
    if my_hotels:
        for hotel in my_hotels:
            bot.send_message(message.chat.id,
                             'Название 🏨 - {0}\nКоличество звезд ⭐️- {1}\nАдрес 🌆- {2}\n'
                             'Расстояние от центра 🚘- {3}\n'
                             'Цена 💵 - {4}'.format(*hotel))
    else:
        bot.send_message(message.chat.id, 'По заданным критериям ничего не найдено 😞')


def check_date(message: Message) -> tuple or list:
    """
    функция для проверки даты введеной от юзера
    :param message:
    :return:
    """
    dates = []
    today = datetime.datetime.today()
    try:
        dates = tuple(filter(lambda x: x > today, map(lambda y: datetime.datetime.strptime(y, '%Y.%m.%d'),
                                                      message.text.split('-'))))
    finally:
        return dates
