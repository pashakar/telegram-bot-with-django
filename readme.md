## Бот, с помощью которого пользователь может выполнить следующие действия:

1. Узнать топ самых дешёвых отелей в городе (команда __/lowprice__).
2. Узнать топ самых дорогих отелей в городе (команда __/highprice__).
3. Узнать отели, наиболее подходящих по цене и расположению от центра
   (самые дешёвые и находятся ближе всего к центру) (команда __/bestdeal__).
***

Запуск бота осуществляется по команде

    python manage.py bot


Зависимости указаны в файле requirements.txt.


## Описание работы команд ##

### Команда /lowprice ###

После ввода команды у пользователя запрашивается:

1. Город, где будет проводиться поиск.
2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
***

### Команда /highprice ###

После ввода команды у пользователя запрашивается:

1. Город, где будет проводиться поиск.
2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
***

### Команда /bestdeal ###

После ввода команды у пользователя запрашивается:

1. Город, где будет проводиться поиск.
2. Диапазон цен.
3. Диапазон расстояния, на котором находится отель от центра.
4. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).

