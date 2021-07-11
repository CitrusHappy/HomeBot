import os
import config
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/')
def hello_world():
    return 'This is the homebot default page.'


#receive message
# Adds support for GET requests to our webhook
@app.route('/webhook',methods=['GET'])
def webhook_authorization():
    verify_token = request.args.get("hub.verify_token")
    # Check if sent token is correct
    if verify_token == config.verify_token:
        # Responds with the challenge token from the request
        return request.args.get("hub.challenge")
    return 'Failed authorization.'

#send message back
@app.route("/webhook", methods=['POST'])
def webhook_handle():
    data = request.get_json()
    message = data['entry'][0]['messaging'][0]['message']
    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
    if message['text']:
        request_body = {
                'recipient': {
                    'id': sender_id
                },
                'message': {"text":"hello, world!"}
            }
        response = requests.post('https://graph.facebook.com/v5.0/me/messages?access_token='+config.access_token,json=request_body).json()
        return response
    return 'ok'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)