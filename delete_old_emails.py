#!/usr/bin/env python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# https://developers.google.com/gmail/api/v1/reference/users/messages/get#examples_1
from apiclient import errors
import base64
import email

# https://stackoverflow.com/questions/1692388/python-list-of-dict-if-exists-increment-a-dict-value-if-not-append-a-new-dic
from collections import defaultdict

import mysql.connector

import logging
import time
from pprint import pprint
from pprint import pformat

# Initialize logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)4d %(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO)

log = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
# https://developers.google.com/gmail/api/auth/scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://mail.google.com/'
]

def insert_run(dbh, counter):
    sql = "\
        INSERT INTO `run` \
        SET query = %s \
          , older_than = %s \
          , bytes_deleted = %s \
          , messages_deleted = %s \
        ON DUPLICATE KEY UPDATE updated = NOW() \
    "

    pprint(counter)
    values = (
        counter['query']
      , counter['older_than']
      , counter['deleted_bytes']
      , counter['deleted']
    )
    print(sql)
    sth = dbh.cursor(dictionary=True)
    sth.execute(sql, values)
    dbh.commit()
    print(sth.rowcount, "record inserted.")
    insert_id = sth.lastrowid
    return insert_id

def get_size_estimate(msg):
    return msg['sizeEstimate']

def get_thread_id(msg):
    return msg['threadId']

def get_message_header(msg, header_name):
    payload = msg['payload']
    headers = payload['headers']

    header_value = ''
    for header in headers:
        if header['name'] == header_name:
            header_value = header['value']

    return header_value

def get_message_info(service, user_id, message):
    result = {}
    msg_id = message['id']

    for i in range(3):
        try:
            msg = service.users().messages().get(userId=user_id, id=msg_id).execute()
        except Exception as error:
            log.info(error)
            time.sleep(1)
    
    # pprint(msg)

    # print(from_header)

    result['from'] = get_message_header(msg, 'From')
    result['to'] = get_message_header(msg, 'To')
    result['subject'] = get_message_header(msg, 'Subject')
    result['date'] = get_message_header(msg, 'Date')
    result['size_estimate'] = get_size_estimate(msg)
    result['thread_id'] = get_thread_id(msg)
    return result

def process_message(service, user_id, message):
    msg_info = get_message_info(service, user_id, message)
    msg_id = message['id']
    msg_info['message_id'] = msg_id
    pprint(msg_info)

    service.users().messages().delete(userId=user_id, id=message['id']).execute()
    log.info(message['id'] + " deleted.")

    return msg_info

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    DBHOST = os.getenv('DBHOST')
    DBNAME = os.getenv('DBNAME')
    DBUSER = os.getenv('DBUSER')
    DBPASS = os.getenv('DBPASS')
    DBPORT = os.getenv('DBPORT')
    dbh = mysql.connector.connect(
        host=DBHOST,
        database=DBNAME,
        user=DBUSER,
        passwd=DBPASS,
        port=int(DBPORT)
    )
    print("MYSQL CONNECTED")

    # Find old messages for trashing
    # https://developers.google.com/gmail/api/v1/reference/users/messages/list#examples
    user_id = 'me'
    older_than = '2m'
    query = 'category:social OR category:updates OR category:promotions older_than:' + older_than

    # https://stackoverflow.com/questions/1692388/python-list-of-dict-if-exists-increment-a-dict-value-if-not-append-a-new-dic
    counter = defaultdict(int)
    try:
        # Fetch the first page of messages
        response = service.users().messages().list(userId=user_id,
                                                q=query).execute()
        if 'messages' in response:
            # print(response['messages'])
            for message in response['messages']:
                msg_info = process_message(service, user_id, message)
                counter['deleted'] += 1
                counter['deleted_bytes'] += msg_info['size_estimate']
                log.info(pformat(dict(counter)))

        while 'nextPageToken' in response:
            log.info("NEXT PAGE")
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q=query,
                                                pageToken=page_token).execute()
            for message in response['messages']:
                msg_info = process_message(service, user_id, message)
                counter['deleted'] += 1
                counter['deleted_bytes'] += msg_info['size_estimate']
                log.info(pformat(dict(counter)))

    except errors.HttpError as error:
        print('An error occurred: %s' % error)

    counter['query'] = query
    counter['older_than'] = older_than
    pprint(counter)
    insert_run(dbh, counter)

    

if __name__ == '__main__':
    main()
