import os
import config
import requests
from flask import Flask, request

#env variables
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

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
    if verify_token == WEBHOOK_VERIFY_TOKEN:
        # Responds with the challenge token from the request
        return request.args.get("hub.challenge")
    return 'Failed authorization.'

#send message back
@app.route("/webhook", methods=['POST'])
def webhook_handle():
    output = request.get_json()
    print(output)
    return 'ok'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)