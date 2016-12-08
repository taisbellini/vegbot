#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!flask/bin/python

from flask import Flask, request
from pymessenger.bot import Bot
from google_places import get_places
import json
import os

app = Flask(__name__)
bot = Bot('ACCESS_TOKEN')


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == os.environ.get('VERIFY_TOKEN'):
            return request.args.get("hub.challenge")
        else:
            return 'Invalid verification token'

    if request.method == 'POST':
        output = json.loads(request.body)

        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                recipient_id = x['sender']['id']
                payload = x['message']['attachments'][0]['payload'] if 'attachments' in x['message'] else None
                if payload and 'coordinates' in payload:
                    location = x['message']['attachments'][0]['payload']['coordinates']
                    response = json.loads(get_places(location))
                    bot.send_text_message(recipient_id, 'Aqui estão os restaurantes abertos perto de você:')
                    for restaurant in response['results']:
                        title = restaurant['name']
                        address = restaurant['vicinity']
                        bot.send_text_message(recipient_id, u'{}. {}'.format(title, address))
                else:
                    bot.send_text_message(recipient_id, 'Onde você está? Me envie sua localização.')
        return 'Success'


if __name__ == '__main__':
    app.run(debug=True)
