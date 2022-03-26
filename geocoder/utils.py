import requests

from django.conf import settings

from .models import Coordinates


def get_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    apikey = settings.GEOCODER_API_KEY

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


def add_coordinates(address):
    try:
        lon, lat = get_coordinates(address)
    except Exception:
        pass
    print('=======')
    print(lon)
    print(lat)

    Coordinates.objects.create(address=address, lat=lat, lon=lon)

