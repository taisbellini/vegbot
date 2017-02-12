#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!flask/bin/python

import os
import json
from google_places import get_latlong, get_places
from pymessenger.bot import Bot

from itertools import islice

bot = Bot(os.environ.get('PAGE_ACCESS_TOKEN'))


def prepare_content(recipient_id, title, location):
    return {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": {
                        "element": {
                            "title": title,
                            "image_url": "https://maps.googleapis.com/maps/api/staticmap?size=764x400&center="
                                         + str(location['lat']) + "," + str(location['lng']) + "&zoom=25&markers="
                                         + str(location['lat']) + "," + str(location['lng']),
                            "item_url": "http://maps.apple.com/maps?q=" + str(location['lat']) + ","
                                        + str(location['lng']) + "&z=16"
                        }
                    }
                }
            }
        }
    }


class State:
    def run(self, data):
        assert 0, "run not implemented"

    def next(self, data):
        contexts = data.get('result').get('contexts', [])
        print 'data', data
        location = next((item for item in contexts if item['name'] == 'facebook_location'), None)
        address = next((item['parameters']['any'] for item in contexts if item['name'] == 'generic'), None)
        print address
        if not location:
            location = json.loads(get_latlong(address))
        if not location:
            return {'name': 'Invalid'}
        elif 'parameters' in location or len(location.get('results')) == 1:
            print location, type(location)
            return {
                'name': 'Location',
                'parameters': {
                    'location': location['results'][0]['geometry']['location'],
                    'recipient_id': next((item['parameters']['facebook_sender_id'] for item in data['result']['contexts'] if
                                          item['name'] == 'generic'))
                }

            }
        else:
            return {
                'name': 'MoreInfo',
                'parameters': {
                    'address': address
                }
            }


class StateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        self.currentState.run()

    # Template method:
    def runAll(self, inputs):
        for i in inputs:
            print(i)
            self.currentState = self.currentState.next(i)
            self.currentState.run()


class Location(State):

    def run(self, data):
        response = get_places(data['parameters']['location'])
        recipient_id = data['parameters']['recipient_id']
        bot.send_text_message(recipient_id, 'Aqui estão os restaurantes abertos perto de você:')
        response = json.loads(response)
        for restaurant in islice(response['results'], 0, 4):
            title = restaurant['name']
            address = restaurant['formatted_address']
            bot.send_raw(
                prepare_content(recipient_id, u'{}. {}'.format(title, address), restaurant['geometry']['location']))
        return {
            'state': 'Location'
        }


class MoreInfo(State):

    def run(self, data):
        response_phrase = u'Legal! Já entendi seu endereço! Agora, preciso saber em que cidade você está.'
        return {
            'speech': response_phrase,
            'state': 'MoreInfo',
            'address': data.get('parameters').get('address'),
            'lifespan': 5
        }


class Invalid(State):
    def run(self, data):
        response_phrase = u"Preciso de mais detalhes da sua localização. " \
                              u"Um endereço com rua, número e cidade é o ideal! " \
                              u"Ou se preferir, pode usar o app do messenger para me enviar a sua localização."
        return {
            'speech': response_phrase,
            'state': 'Invalid'
        }

states_map = {
    'Init': Location(),
    'Location': Location(),
    'MoreInfo': MoreInfo(),
    'Invalid': Invalid()
}
