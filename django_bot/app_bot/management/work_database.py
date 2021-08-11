from telebot.types import Message
from app_bot.models import DataUser


def add_to_bd(message: Message):
    data_user, _ = DataUser.objects.get_or_create(
        username=message.from_user.first_name, tg_id=message.from_user.id
    )