import os
import requests


def get_places(location):
    params = {
        'key': os.environ.get('GOOGLE_KEY'),
        'query': 'vegano+vegetariano',
        'location': '{},{}'.format(location['lat'], location['long']),
        'radius': 2000,
        'opennow': True,
        'types': 'food'
    }
    response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
    return response.content


