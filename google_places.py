import os
import requests


def get_places(location):
    params = {
        'key': os.environ.get('GOOGLE_KEY'),
        'keyword': 'vegan',
        'location': '{},{}'.format(location['lat'], location['long']),
        'radius': 8000,
        'opennow': True,
        'types': 'food'
    }
    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)
    return response.content
