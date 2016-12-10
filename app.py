#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!flask/bin/python

from flask import Flask, request
from pymessenger.bot import Bot
from google_places import get_places
import json
import os
from itertools import islice

app = Flask(__name__)
bot = Bot(os.environ.get('PAGE_ACCESS_TOKEN'))


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == os.environ.get('VERIFY_TOKEN'):
            return str(request.args.get("hub.challenge"))
        else:
            return 'Invalid verification token'

    if request.method == 'POST':
        output = json.loads(request.data)

        x = output['entry'][0]['messaging'][0]
        recipient_id = x['sender']['id']
        payload = x['message']['attachments'][0]['payload'] if 'attachments' in x['message'] else None
        if payload and 'coordinates' in payload:
            location = x['message']['attachments'][0]['payload']['coordinates']
            response = json.loads(get_places(location))
            bot.send_text_message(recipient_id, 'Aqui estão os restaurantes abertos perto de você:')
            for restaurant in islice(response['results'], 0, 4):
                title = restaurant['name']
                address = restaurant['formatted_address']
                bot.send_text_message(recipient_id, u'{}. {}'.format(title, address))
        elif any(expr in x['message']['text'].lower for expr in ['oi', 'olá']):
            bot.send_text_message(recipient_id, 'Olá! Estou aqui para facilitar a vida no vegetarianismo! '
                                                'Basta me enviar sua localização e eu te indicarei os restaurantes'
                                                ' vegetarianos abertos mais próximos de você! :)')
        else:
            bot.send_text_message(recipient_id, 'Onde você está? '
                                                'Me envie sua localização pelo app do celular ou habilite '
                                                'essa função no navegador.')
        return 'Success'


if __name__ == '__main__':
    app.run(debug=True)
