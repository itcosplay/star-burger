import requests
from django.conf import settings


def get_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    apikey = '0014b90e-8180-4781-a17a-ea38ab5d8175'

    response = requests.get (
        base_url,
        params = {
            "geocode": address,
            "apikey": apikey,
            "format": "json"
        }
    )
    response.raise_for_status()

    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant_place = found_places[0]
    lon, lat = most_relevant_place['GeoObject']['Point']['pos'].split(" ")
    
    return lon, lat

lon, lat = get_coordinates('Москва, ул. Новый Арбат, 15')

print(lon)
print(lat)