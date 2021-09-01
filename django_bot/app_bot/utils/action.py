import datetime

from app_bot.models import DataUser
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot import TeleBot

from app_bot.utils.get_any_data import get_cities, get_destination_id, hotels

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")
calendar_2_callback = CallbackData("calendar_2", "action", "year", "month", "day")

STOP_MESSAGE = 'Останавливаю работу 📛...'


class Action:

    def __init__(self, message: Message or CallbackQuery, bot: TeleBot):
        self.bot = bot
        self.data_user = DataUser.objects.get(pk=message.from_user.id)

    def get_list_cities(self, message: Message, **kwargs) -> None:
        """
        Получение списка городов
        :param message:
        :param kwargs:
        :return:
        """
        self.data_user.sort_order = kwargs['sort_order']
        self.data_user.save(update_fields=['sort_order'])
        if message.text.lower() == 'стоп':
            self.bot.send_message(message.chat.id, STOP_MESSAGE)
            return
        rmk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        self.bot.send_message(message.chat.id, 'Думаю, подождите...')
        cities = get_cities(message.text)
        if not cities:
            msg = self.bot.reply_to(message, 'Введенный город не найден, попробуйте другой ❗️')
            self.bot.register_next_step_handler(
                msg, self.get_list_cities, sort_order=kwargs['sort_order']
            )
            return
        for el in cities:
            rmk.add(KeyboardButton(el))
        city = self.bot.send_message(message.chat.id, 'Уточните город', reply_markup=rmk)
        self.bot.register_next_step_handler(city, self.get_city_by_destination_id)

    def get_city_by_destination_id(self, message: Message) -> None:
        """
        Получение конкретного города
        :param message:
        :return:
        """
        if message.text.lower() == 'стоп':
            self.bot.send_message(message.chat.id, STOP_MESSAGE)
            return
        self.bot.send_message(message.chat.id, 'Секунду, всё уточню ⏳')
        self.data_user.destination_id = get_destination_id(message.text)
        if self.data_user.destination_id is None:
            self.bot.send_message(message.chat.id, 'что-то мне не хорошо')
            return
        self.data_user.save(update_fields=['destination_id'])
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for i in range(1, 11):
            reply_markup.add(KeyboardButton(i))
        count_hotels = self.bot.send_message(
            message.chat.id,
            'Укажите количество отелей\n(не больше 10) ❗️',
            reply_markup=reply_markup
        )
        if self.data_user.sort_order == 'DISTANCE_FROM_LANDMARK':
            self.bot.register_next_step_handler(count_hotels, self.get_price)
            return
        self.bot.register_next_step_handler(count_hotels, self.get_date_in)

    def get_date_in(self, message: Message) -> None:
        """
        Получение даты заезда
        :param message:
        :return:
        """
        if message.text.lower() == 'стоп':
            self.bot.send_message(message.chat.id, STOP_MESSAGE)
            return
        if self.data_user.sort_order == 'DISTANCE_FROM_LANDMARK':
            if not message.text.isdigit() or float(message.text) < 0:
                msg = self.bot.reply_to(message, 'Не корректно указано расстояние❗ Попробуйте еще раз')
                self.bot.register_next_step_handler(msg, self.get_date_in)
                return
            self.data_user.distance = float(message.text)
            self.data_user.save(update_fields=['distance'])
        else:
            if self.check_count(message.text):
                msg = self.bot.reply_to(message, 'Введите количество отелей (не больше 10) ❗️')
                self.bot.register_next_step_handler(msg, self.get_date_in)
                return
            self.data_user.count_hotels = message.text
            self.data_user.save(update_fields=['count_hotels'])
        self.send_calendar(message=message)

    def send_calendar(self, message) -> None:
        now = datetime.datetime.now()
        self.bot.send_message(
            message.chat.id,
            'Введите дату заселения',
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix, year=now.year, month=now.month
            ))

    def get_hotels(self, call: CallbackQuery, ) -> None:
        """
        Выдача юзеру отелей
        :param call:
        :return:
        """
        if self.data_user.sort_order == 'DISTANCE_FROM_LANDMARK':
            my_hotels = hotels(
                destination_id=self.data_user.destination_id,
                page_size=self.data_user.count_hotels,
                sort_order=self.data_user.sort_order,
                date_in=self.data_user.date_in,
                date_out=self.data_user.date_out,
                price_min=self.data_user.price_min,
                price_max=self.data_user.price_max,
                distance_from_centr=self.data_user.distance
            )
        else:
            my_hotels = hotels(
                destination_id=self.data_user.destination_id,
                page_size=self.data_user.count_hotels,
                sort_order=self.data_user.sort_order,
                date_in=self.data_user.date_in,
                date_out=self.data_user.date_out
            )
        if not my_hotels:
            self.bot.send_message(call.from_user.id, 'По заданным критериям ничего не найдено ☹️')
            return
        for hotel in my_hotels:
            self.bot.send_message(
                call.from_user.id,
                'Название 🏨 - {0}\nКоличество звезд ⭐️- {1}\nАдрес 🌆- {2}\n'
                'Расстояние от центра 🚘- {3}\n'
                'Цена 💵 - {4}'.format(*hotel)
            )

    def get_price(self, message: Message) -> None:
        """
        Получение диапазона цен
        :param message:
        :return:
        """
        if message.text.lower() == 'стоп':
            self.bot.send_message(message.chat.id, STOP_MESSAGE)
            return
        if self.check_count(message.text):
            msg = self.bot.reply_to(message, 'Введите количество отелей (не больше 10) ❗️')
            self.bot.register_next_step_handler(msg, self.get_price)
            return
        self.data_user.count_hotels = message.text
        self.data_user.save(update_fields=['count_hotels'])
        price = self.bot.send_message(
            message.chat.id,
            'Укажите диапазон цен в рублях 💰💰💰\nПример, 5000-10000'
        )
        self.bot.register_next_step_handler(price, self.get_distance)

    def get_distance(self, message: Message) -> None:
        """
        Получение расстояния от центра
        :param message:
        :return:
        """
        if message.text.lower() == 'стоп':
            self.bot.send_message(message.chat.id, STOP_MESSAGE)
            return
        price = tuple(map(int, filter(lambda x: x.isdigit(), message.text.split('-'))))
        correct_price = len(price) == 2 and price[1] > price[0] and all(i > 0 for i in price)
        if not correct_price:
            msg = self.bot.reply_to(
                message, 'Ценовой диапазон указан не корректно❗️\n'
                         'Пример, 5000-10000 \n'
                         'Наименьшая цена ввода должна быть больше 0'
            )
            self.bot.register_next_step_handler(msg, self.get_distance)
            return
        self.data_user.price_min, self.data_user.price_max = price
        self.data_user.save(update_fields=['price_min', 'price_max'])
        msg = self.bot.send_message(
            message.chat.id,
            'А теперь введите желаемое максимальное расстояние (в км) проживания от центра '
            'заданого города!\nПример, 5'
        )
        self.bot.register_next_step_handler(msg, self.get_date_in)

    @staticmethod
    def check_count(count_hotels) -> bool:
        """
        Проверка введенного количества отелей
        :param count_hotels:
        :return:
        """
        return not count_hotels.isdigit() or not 10 >= int(count_hotels) > 0


def input_correct_date(call, bot, calendar_callback, now, date=calendar):
    """
    Повторное отправление календаря юзеру
    """
    bot.send_message(
        call.from_user.id,
        'Укажите корректную дату',
        reply_markup=date.create_calendar(
            name=calendar_callback.prefix, year=now.year, month=now.month
        ))
