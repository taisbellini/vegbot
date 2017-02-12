#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!flask/bin/python

from flask import Flask, request, make_response
import StateMachine
from google_places import get_places, get_latlong
import json
import os

app = Flask(__name__)

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
        print 'output', output
        contexts = output.get('result').get('contexts', [])
        current_state = next((item for item in contexts if item['name'] == 'state'), 'Init')
        current_state_object = StateMachine.states_map[current_state]
        state = current_state_object.next(output)
        print 'next', state
        response = StateMachine.states_map[state.get('name')].run(state)
        print 'run response', response

        if 'speech' in response:
            res = {
                "speech": response['speech'],
                "displayText": response['speech'],
                "contextOut": [response],
                "source": "VegBot"
            }

            response = make_response(json.dumps(res))
            response.headers['Content-Type'] = 'application/json'
            return response
    return 'Done'


if __name__ == '__main__':
    app.run(debug=True)
