import os
import requests
import sys
import chatbot

from fbchat import Client, log
from fbchat.models import *
from flask import Flask, request


#env variables
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

app = Flask(__name__)
#
#@app.route('/favicon.ico')
#def favicon():
#    return app.send_static_file('favicon.ico')
#
#
#@app.route('/')
#def hello_world():
#    return 'This is the homebot default page.'
#
#
##single one-on-one chat response protocol
##verify token to make sure its a message from facebook
#@app.route('/webhook', methods=['GET'])
#def webhook_authorization():
#    verify_token = request.args.get("hub.verify_token")
#    if verify_token == WEBHOOK_VERIFY_TOKEN and verify_token != None:
#        return request.args.get("hub.challenge")
#    return 'Failed authorization.'
#
##send message back
#@app.route('/webhook', methods=['POST'])
#def webhook_handle():
#    data = request.get_json()
#    message = data['entry'][0]['messaging'][0]['message']
#    if message != None:
#        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
#        if message.get('message', {}).get('text'):
#            message_text = message['text']
#            ints = chatbot.predict_class(message_text)
#            res = chatbot.get_response(ints, chatbot.intents)
#
#            request_body = {
#                    'recipient': {
#                        'id': sender_id
#                    },
#                    'message': {"text":res}
#                }
#            response = requests.post('https://graph.facebook.com/v11.0/me/messages?access_token='+ACCESS_TOKEN,json=request_body).json()
#            return response
#        return 'ok'
#    return 'empty message'



#group chat listener
class Echobot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        # If you're not the author, echo
        if author_id != self.uid:
            self.send(message_object, thread_id=thread_id, thread_type=thread_type)

client = Echobot(EMAIL, PASSWORD)
client.listen()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)