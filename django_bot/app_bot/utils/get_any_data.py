import logging

import requests
from bs4 import BeautifulSoup
from django.conf import settings

HEADERS = settings.HEADERS

logger = logging.getLogger(__name__)


def log_errors(func):

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.error(f'ERROR: {exc}')
            raise exc

    return wrapper


@log_errors
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


@log_errors
def get_destination_id(city: str):
    """
    Функция для получения id города
    :param city: город, в котором будет поиск
    :return: id города
    """
    data = prepare(city)
    destination_id = data['suggestions'][0]['entities'][0]['destinationId']
    return destination_id


@log_errors
def hotels(destination_id: str, page_size: str, sort_order: str, date_in, date_out,
           distance_from_centr=None, price_min=None, price_max=None) -> list or str:
    """
    Функция для получения списка отелей в городе
    :param destination_id: id города
    :param sort_order: тип сортировки
    :param distance_from_centr: список расстояний от центра
    :param date_in: дата проживания
    :param price_min: мин-ая цена за номер
    :param price_max: макс-ая цена за номер
    :param date_out: дата выезда
    :param page_size: количество отелей на странице, максимум 25,
     фактически вывод количества отелей юзеру
    :return: список отелей
    """
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {
        "adults1": "1",
        "pageNumber": "1",
        "destinationId": destination_id,
        "pageSize": page_size,
        "checkOut": date_out,
        "checkIn": date_in,
        "sortOrder": sort_order,
        "locale": "ru_RU",
        "currency": "RUB"
    }

    if price_min and price_max:
        querystring['priceMin'], querystring['priceMax'] = int(price_min), int(price_max)
    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code != 200:
        logger.error(f'{response.status_code}: {response.text}')
        return 'Извините, мне не хорошо('
    data = response.json()['data']['body']['searchResults']['results']

    h = []
    for el in data:
        distance = el.get('landmarks')[0]['distance'][:3]
        if distance_from_centr and distance_from_centr >= float(distance.replace(',', '.')):
            h.append(get_properties(el, distance))
        else:
            h.append(get_properties(el, distance))
    return h


@log_errors
def get_properties(el: dict, distance: str) -> list:
    properties = [
        el.get('name'), el.get('starRating', 0), el.get('address').get('streetAddress'), distance,
    ]
    properties.append(str(el.get('ratePlan').get('price').get('exactCurrent')) + ' руб.') if el.get(
        'ratePlan') else 'цена неизвестна 🤫'
    return properties


@log_errors
def prepare(city: str):
    """
    Функция для подготовки поиска
    :param city: город поиска
    :return:
    """
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": city, "locale": "ru_RU"}
    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code != 200:
        logger.error(f'{response.status_code}: {response.text}')
        raise Exception
    return response.json()
