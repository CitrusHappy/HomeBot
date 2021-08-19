from __future__ import print_function
import os.path
import datetime
import requests
import chatbot
import psycopg2

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from rq import Queue
from worker import conn

from flask import Flask, request

#env variables
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SELF_ID = os.getenv("SELF_ID")
DATABASE_URL = os.environ['DATABASE_URL']


app = Flask(__name__)
q = Queue(connection=conn)

#database creation
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()
cursor.execute("CREATE DATABASE chatbot;")
cursor.execute("CREATE TABLE tbl_user (UserID int(16))")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


#handles json recreation and sending to facebook api
def send_message(sender_id, message_text):
    request_body = {
    'recipient': {
        'id': sender_id
    },
    'message': {"text":message_text}
    }
    print(message_text)
    requests.post('https://graph.facebook.com/v11.0/me/messages?access_token='+ACCESS_TOKEN,json=request_body)


#checks to see if any google calendar events are starting
def event_checker():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=60896)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    service = build('calendar', 'v3', credentials=creds)



    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 3 events')
    events_result = service.events().list(calendarId='5tiecqs27can12s13cfqi8n91g@group.calendar.google.com', timeMin=now,
                                        maxResults=3, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return "No upcoming events found."
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

            print(now, ' == ', start)

            if start <= now:
                # Create a cursor to perform database operations
                cursor.execute("SELECT UserID FROM tbl_user;")
                userlist = cursor.fetchall()

                #sends a single message to each user database
                for user in userlist:
                    print('notifying ',user, ' of event: ', start, event['summary'])
                    send_message(user, event['summary'])
                
                conn.close()
                return 'done'
            else:
                return "it is not time to notify"


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/')
def home():
    q.enqueue(event_checker)
    return 'This is the homebot default page.'


#single one-on-one chat response protocol
#verify token to make sure its a message from facebook
@app.route('/webhook', methods=['GET'])
def webhook_authorization():
    verify_token = request.args.get("hub.verify_token")
    if verify_token == WEBHOOK_VERIFY_TOKEN and verify_token != None:
        return request.args.get("hub.challenge")
    return 'Failed authorization.'

#when a message is recieved, send one back
@app.route('/webhook', methods=['POST'])
def webhook_handle():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        #check if user sent a message
        if 'message' in data['entry'][0]['messaging'][0]:
            #check if there is text in the message
            if 'text' in data['entry'][0]['messaging'][0]['message']:
                text = data['entry'][0]['messaging'][0]['message']['text']
                sender_id = data['entry'][0]['messaging'][0]['sender']['id']
                
                #check to see if our message was echo'd
                if sender_id == SELF_ID:
                    print('that was my message')
                    return 'that was my message'
                else:
                    ints = chatbot.predict_class(text)
                    res = chatbot.get_response(ints, chatbot.intents, sender_id)
                    send_message(sender_id, res)
                    return 'done'
            else:
                print('no text found in message')
                return 'no text found in message'
        print('no message found')
        return 'no message found'
    print('i tried to post myself :(')
    return 'i tried to post myself :('



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
    