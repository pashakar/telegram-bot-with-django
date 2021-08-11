# import datetime
#
# from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
# from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
# from telebot import TeleBot
#
# from .get_any_data import get_cities, get_destination_id, hotels
# from app_bot.models import DataUser
#
# calendar = Calendar(language=RUSSIAN_LANGUAGE)
# calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")
# calendar_2_callback = CallbackData("calendar_2", "action", "year", "month", "day")
#
# STOP_MESSAGE = 'Останавливаю работу 📛...'
#
#
# def get_list_cities(message: Message, **kwargs) -> None:
#     """
#     Получение списка городов
#     :param message:
#     :return:
#     """
#     user = DataUser.objects.get(pk=message.from_user.id)
#     bot = kwargs['bot']
#     user.sort_order = sort_order = kwargs['sort_order']
#     print(user.sort_order)
#     user.save(update_fields=['sort_order'])
#
#     if message.text.lower() == 'стоп':
#         bot.send_message(message.chat.id, STOP_MESSAGE)
#         return
#
#     rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     bot.send_message(message.chat.id, 'Думаю, подождите...')
#     cities = get_cities(message.text)
#     if not cities:
#         msg = bot.reply_to(message, 'Введенный город не найден, попробуйте другой ❗️')
#         bot.register_next_step_handler(msg, get_list_cities, bot=bot, sort_order=sort_order)
#         return
#
#     for el in cities:
#         rmk.add(KeyboardButton(el))
#
#     city = bot.send_message(message.chat.id, 'Уточните город', reply_markup=rmk)
#     bot.register_next_step_handler(city, get_city_by_destination_id, bot)
#
#
# def get_city_by_destination_id(message: Message, bot: TeleBot) -> None:
#     """
#     Получение конкретного города
#     :param message:
#     :param bot:
#     :return:
#     """
#
#     if message.text.lower() == 'стоп':
#         bot.send_message(message.chat.id, STOP_MESSAGE)
#         return
#
#     bot.send_message(message.chat.id, 'Секунду, всё уточню ⏳')
#     destination_id = get_destination_id(message.text)
#     data_user = DataUser.objects.get(pk=message.from_user.id)
#     data_user.destination_id = destination_id
#     data_user.save(update_fields=['destination_id'])
#     print(data_user.destination_id)
#
#     reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     for i in range(1, 11):
#         reply_markup.add(KeyboardButton(i))
#
#     count_hotels = bot.send_message(
#         message.chat.id,
#         'Укажите количество отелей\n(не больше 10) ❗️',
#         reply_markup=reply_markup
#     )
#     if data_user.sort_order == 'DISTANCE_FROM_LANDMARK':
#         bot.register_next_step_handler(count_hotels, get_price, bot)
#         return
#     bot.register_next_step_handler(count_hotels, get_date_in, bot)
#
#
# def get_date_in(message: Message, bot: TeleBot) -> None:
#     """
#     Получение даты заезда - выезда
#     :param message:
#     :param bot:
#     :return:
#     """
#     data_user = DataUser.objects.get(pk=message.from_user.id)
#     now = datetime.datetime.now()
#
#     if message.text.lower() == 'стоп':
#         bot.send_message(message.chat.id, STOP_MESSAGE)
#         return
#
#     if not data_user.price_min:
#         count_hotels = message.text
#         if check_count(count_hotels):
#             msg = bot.reply_to(message, 'Введите количество отелей (не больше 10) ❗️')
#             bot.register_next_step_handler(msg, get_date_in, bot)
#             return
#         data_user.count_hotels = count_hotels
#         print(data_user.count_hotels)
#         data_user.save(update_fields=['count_hotels'])
#
#     else:
#         distance = message.text
#         if not distance.isdigit() or float(distance) < 0:
#             msg = bot.reply_to(message, 'Не корректно указано расстояние❗ Попробуйте еще раз')
#             bot.register_next_step_handler(msg, get_date_in, bot)
#             return
#
#         data_user.distance = float(distance)
#         data_user.save(update_fields=['distance'])
#         print(data_user.distance)
#
#     bot.send_message(
#         message.chat.id,
#         'Введите дату заселения',
#         reply_markup=calendar.create_calendar(
#             name=calendar_1_callback.prefix, year=now.year, month=now.month
#         )
#     )
#
#
# def get_hotels(call: CallbackQuery, bot: TeleBot) -> None:
#     """
#     Выдача юзеру отелей
#     :return:
#     """
#     data_user = DataUser.objects.get(pk=call.from_user.id)
#     if data_user.sort_order == 'DISTANCE_FROM_LANDMARK':
#         my_hotels = hotels(
#             destination_id=data_user.destination_id,
#             page_size=data_user.count_hotels,
#             sort_order=data_user.sort_order,
#             date_in=data_user.date_in,
#             date_out=data_user.date_out,
#             price_min=data_user.price_min,
#             price_max=data_user.price_max,
#             distance_from_centr=data_user.distance
#         )
#     else:
#         my_hotels = hotels(
#             destination_id=data_user.destination_id,
#             page_size=data_user.count_hotels,
#             sort_order=data_user.sort_order,
#             date_in=data_user.date_in,
#             date_out=data_user.date_out
#         )
#     if not my_hotels:
#         bot.send_message(call.from_user.id, 'По заданным критериям ничего не найдено ☹️')
#         return
#     for hotel in my_hotels:
#         bot.send_message(
#             call.from_user.id,
#             'Название 🏨 - {0}\nКоличество звезд ⭐️- {1}\nАдрес 🌆- {2}\n'
#             'Расстояние от центра 🚘- {3}\n'
#             'Цена 💵 - {4}'.format(*hotel)
#         )
#
#
# # Ниже функции для команды bestdeal
#
# def get_price(message: Message, bot: TeleBot) -> None:
#     """
#     Получение диапазона цен
#     :param message:
#     :param bot:
#     :return:
#     """
#     data_user = DataUser.objects.get(pk=message.from_user.id)
#
#     if message.text.lower() == 'стоп':
#         bot.send_message(message.chat.id, STOP_MESSAGE)
#         return
#
#     count_hotels = message.text
#     if check_count(count_hotels):
#         msg = bot.reply_to(message, 'Введите количество отелей (не больше 10) ❗️')
#         bot.register_next_step_handler(msg, get_price, bot)
#         return
#     data_user.count_hotels = message.text
#     data_user.save(update_fields=['count_hotels'])
#     print(data_user.count_hotels)
#
#     price = bot.send_message(
#         message.chat.id,
#         'Укажите диапазон цен в рублях 💰💰💰\nПример, 5000-10000'
#     )
#     bot.register_next_step_handler(price, get_distance, bot)
#
#
# def get_distance(message: Message, bot: TeleBot) -> None:
#     """
#     Получение расстояния от центра
#     :param message:
#     :param bot:
#     :return:
#     """
#     data_user = DataUser.objects.get(pk=message.from_user.id)
#
#     if message.text.lower() == 'стоп':
#         bot.send_message(message.chat.id, STOP_MESSAGE)
#         return
#
#     price = tuple(map(int, filter(lambda x: x.isdigit(), message.text.split('-'))))
#     correct_price = len(price) == 2 and price[1] > price[0] and all(i > 0 for i in price)
#
#     if not correct_price:
#         msg = bot.reply_to(
#             message, 'Ценовой диапазон указан не корректно❗️\n'
#                      'Пример, 5000-10000 \n'
#                      'Наименьшая цена ввода должна быть больше 0'
#         )
#         bot.register_next_step_handler(msg, get_distance)
#         return
#
#     data_user.price_min, data_user.price_max = price
#     data_user.save(update_fields=['price_min', 'price_max'])
#     print(data_user.price_min, data_user.price_max)
#     msg = bot.send_message(
#         message.chat.id,
#         'А теперь введите желаемое максимальное расстояние (в км) проживания от центра '
#         'заданого города!\nПример, 5'
#     )
#
#     bot.register_next_step_handler(msg, get_date_in, bot)
#
#
# def check_count(count_hotels):
#     """
#     Проверка введенного количества отелей
#     :param count_hotels:
#     :return:
#     """
#     return not count_hotels.isdigit() or not 10 >= int(count_hotels) > 0
