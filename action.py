import datetime

from telebot import types

from get_any_data import get_cities, get_destination_id, hotels


def get_list_cities(message, bot, sort_order):
    """
    ПОлучение списка городов
    :param message:
    :param bot:
    :param sort_order:
    :return:
    """
    rmk = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    bot.send_message(message.chat.id, 'Думаю, подождите...')
    cities = get_cities(message.text)
    if not cities:
        msg = bot.reply_to(message, 'Введенный город не найден, попробуйте еще раз')
        bot.register_next_step_handler(msg, get_list_cities, bot=bot, sort_order=sort_order)
        return
    for el in cities:
        rmk.add(types.KeyboardButton(el))
    city = bot.send_message(message.chat.id, 'Уточните город', reply_markup=rmk)
    bot.register_next_step_handler(city, get_city_by_destination_id, bot=bot, sort_order=sort_order)


def get_city_by_destination_id(message, bot, sort_order):
    """
    Получение конкретного города
    :param message:
    :param bot:
    :param sort_order:
    :return:
    """
    bot.send_message(message.chat.id, 'Секунду, всё уточню ⏳')
    destination_id = get_destination_id(message.text)
    count_hotels = bot.send_message(message.chat.id, 'Введите количество отелей\n'
                                                     '(не больше 10)')
    bot.register_next_step_handler(count_hotels, get_date, bot=bot, destination_id=destination_id,
                                   sort_order=sort_order)


def get_date(message, bot, destination_id, sort_order):
    """
    Получение даты заезда - выезда
    :param message:
    :param bot:
    :param destination_id:
    :param sort_order:
    :return:
    """
    count_hotels = message.text
    if not count_hotels.isdigit() or not 10 >= int(count_hotels) > 0:
        msg = bot.reply_to(message, 'Введите количество отелей (не больше 10)')
        bot.register_next_step_handler(msg, get_date, bot=bot, sort_order=sort_order, destination_id=destination_id)
        return
    date = bot.send_message(message.chat.id, 'Введите дату в формате: дата заселения - дата выезда.\n'
                                             'Пример, 2020.12.31-2021.01.31 ')
    if sort_order == 'DISTANCE_FROM_LANDMARK':
        bot.register_next_step_handler(date, get_price, bot=bot, count_hotels=count_hotels,
                                       destination_id=destination_id)
        return
    bot.register_next_step_handler(date, get_hotels, bot=bot, count_hotels=count_hotels,
                                   destination_id=destination_id, sort_order=sort_order)


def get_hotels(message, bot, count_hotels, destination_id, sort_order):
    """
    Выдача юзеру отелей
    :param message:
    :param bot:
    :param count_hotels:
    :param destination_id:
    :param sort_order:
    :return:
    """
    dates = check_date(message=message)
    if not dates:
        msg = bot.reply_to(message, 'Неверный формат даты! Будьте внимательней!\n'
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
        bot.send_message(message.chat.id, 'По заданным критериям ничего не найдено')


# Ниже функции для команды bestdeal


def get_price(message, bot, destination_id, count_hotels):
    """
    Получение диапазона цен
    :param message:
    :param bot:
    :param count_hotels:
    :param destination_id:
    :return:
    """
    dates = check_date(message=message)
    if not dates:
        msg = bot.reply_to(message, 'Неверный формат даты! Будьте внимательней!\n'
                                    'Пример, 2020.12.31-2021.01.31')
        bot.register_next_step_handler(msg, get_price, bot=bot, count_hotels=count_hotels,
                                       destination_id=destination_id, )
        return
    price = bot.send_message(message.chat.id, 'Укажите диапазон цен в рублях.\n'
                                              'Пример, 5000-10000')
    bot.register_next_step_handler(price, get_distance, bot=bot, destination_id=destination_id,
                                   dates=dates, count_hotels=count_hotels)


def get_distance(message, bot, destination_id, dates, count_hotels):
    """
    Получение расстояния от центра
    :param message:
    :param bot:
    :param count_hotels:
    :param destination_id:
    :param dates:
    :return:
    """
    price = tuple(map(int, filter(lambda x: x.isdigit(), message.text.split('-'))))
    if len(price) != 2 or price[0] > price[1] or price[0] <= 0 or price[1] <= 0:
        msg = bot.reply_to(message, 'Ценовой диапазон указан не корректно!\n'
                                    'Пример, 5000-10000')
        bot.register_next_step_handler(msg, get_distance, bot=bot, destination_id=destination_id,
                                       dates=dates, count_hotels=count_hotels)
        return

    distance = bot.send_message(message.chat.id,
                                'А теперь введите желаемое максимальное расстояние (в км) проживания от центра '
                                'заданого города!\nПример, 5')
    bot.register_next_step_handler(distance, get_hotels_for_best_deal, bot=bot, destination_id=destination_id,
                                   dates=dates, price=price, count_hotels=count_hotels)


def get_hotels_for_best_deal(message, bot, destination_id, dates, count_hotels, price):
    """
    Выдача юзеру отелей по команде /bestdeal
    :return:
    """
    distance = message.text
    if not distance.isdigit() or float(distance) < 0:
        msg = bot.reply_to(message, 'Не корректно указано расстояние! Попробуйте еще раз')
        bot.register_next_step_handler(msg, get_hotels_for_best_deal, bot=bot, destination_id=destination_id,
                                       dates=dates, price=price, count_hotels=count_hotels)
        return
    bot.send_message(message.chat.id, 'Минутку')
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
        bot.send_message(message.chat.id, 'По заданным критериям ничего не найдено')


def check_date(message, ):
    """
    функция для проверки даты введеной от юзера
    :param message:
    :return:
    """
    dates = []
    try:
        today = datetime.datetime.today()
        for date in message.text.split('-'):
            correct_data = datetime.datetime.strptime(date, '%Y.%m.%d')
            if correct_data > today:
                dates.append(datetime.datetime.strptime(date, '%Y.%m.%d'))
    finally:
        return dates
