import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "hotels4.p.rapidapi.com"
}


def get_cities(city: str) -> list or None:
    """
    Функция получения списка возможных городов
    :param city: город, введенный юзером
    :return: список городов, один из них город юзера
    """
    data = prepare(city)
    data = data['suggestions'][0]['entities']

    cities = [BeautifulSoup(city['caption'], features='html.parser').getText() for city in data]
    return cities if cities else None


def get_destination_id(city: str) -> str:
    """
    Функция для получения id города
    :param city: город, в котором будет поиск
    :return: id города
    """
    data = prepare(city)
    destination_id = data['suggestions'][0]['entities'][0]['destinationId']
    return destination_id


def hotels(destination_id: str, page_size: str, sort_order: str, date_in, date_out,
           distance_from_centr=None, price_min=None, price_max=None) -> list:
    """
    Функция для получения списка отелей в городе
    :param destination_id: id города
    :param sort_order: тип сортировки
    :param distance_from_centr: список расстояний от центра
    :param date_in: дата проживания
    :param price_min: мин-ая цена за номер
    :param price_max: макс-ая цена за номер
    :param date_out: дата выезда
    :param page_size: количество отелей на странице, максимум 25, фактически вывод количества отелей юзеру
    :return: список отелей
    """
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"adults1": "1", "pageNumber": "1", "destinationId": destination_id, "pageSize": page_size,
                   "checkOut": date_out, "checkIn": date_in, "sortOrder": sort_order, "locale": "ru_RU",
                   "currency": "RUB"}
    if price_min and price_max:
        querystring['priceMin'], querystring['priceMax'] = int(price_min), int(price_max)
    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    data = response.json()['data']['body']['searchResults']['results']

    h = []
    for el in data:
        distance = el.get('landmarks')[0]['distance'][:3]
        if distance_from_centr:
            if distance_from_centr >= float(distance.replace(',', '.')):
                h.append(get_properties(el, distance))
        else:
            h.append(get_properties(el, distance))
    return h


def get_properties(el: dict, distance: str) -> list:
    properties = [
        el.get('name'), el.get('starRating', 0), el.get('address').get('streetAddress'), distance,
    ]
    properties.append(str(el.get('ratePlan').get('price').get('exactCurrent')) + ' руб.') if el.get(
        'ratePlan') else 'цена неизвестна 🤫'
    return properties


def prepare(city: str) -> dict:
    """
    Функция для подготовки поиска
    :param city: город поиска
    :return:
    """
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": city, "locale": "ru_RU"}

    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    return response.json()
