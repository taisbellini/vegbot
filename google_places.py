import os
import requests

def get_places(location):
    params = {
        'key': os.environ.get('GOOGLE_KEY'),
        'query': 'vegano+vegetariano',
        'location': '{},{}'.format(location['lat'], location['lng']),
        'radius': 2000,
        'opennow': True,
        'types': 'food'
    }
    response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
    return response.content


def get_latlong(address):
    params = {
        'key': os.environ.get('GOOGLE_KEY'),
        'address': address
    }

    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=params)
    return response.content