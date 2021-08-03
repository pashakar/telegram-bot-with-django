import sqlite3
import time

from telebot.types import Message


def add_to_bd(message: Message):
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER,
        first_name TEXT,
        date DATE 
        )""")
    cursor.execute(f'SELECT user_id FROM users WHERE user_id={message.from_user.id}')
    data = cursor.fetchone()
    if not data:
        tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
        cursor.execute(f'INSERT INTO users VALUES(?, ?, ?);',
                       (message.from_user.id, message.from_user.first_name, tconv(message.date)))
        db.commit()
