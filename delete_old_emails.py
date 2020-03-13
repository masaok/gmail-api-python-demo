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

from pprint import pprint

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def insert(dbh, msg_info):
    sql = "\
        INSERT INTO `message` \
        SET gmail_message_id = %s \
          , gmail_thread_id = %s \
          , size_estimate = %s \
          , from_header_value = %s \
        ON DUPLICATE KEY UPDATE updated = NOW() \
    "

    pprint(msg_info)
    values = (
        msg_info['message_id']
      , msg_info['thread_id']
      , msg_info['size_estimate']
      , msg_info['from']
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

def get_message_info(service, user_id, message, header_name):
    result = {}
    msg_id = message['id']
    msg = service.users().messages().get(userId=user_id, id=msg_id).execute()
    # pprint(msg)

    # print(from_header)

    result['from'] = get_message_header(msg, 'From')
    result['to'] = get_message_header(msg, 'To')
    result['subject'] = get_message_header(msg, 'Subject')
    result['date'] = get_message_header(msg, 'Date')
    result['size_estimate'] = get_size_estimate(msg)
    result['thread_id'] = get_thread_id(msg)
    return result

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
    query = 'category:social OR category:updates OR category:promotions older_than:1m'
    try:
        # Fetch the first page of messages
        response = service.users().messages().list(userId=user_id,
                                                q=query).execute()
        if 'messages' in response:
            # print(response['messages'])
            for message in response['messages']:


                # Get message "info" here (From header, thread_id, sizeEstimate)
                msg_info = get_message_info(service, user_id, message, 'From')
                msg_id = message['id']
                msg_info['message_id'] = msg_id
                pprint(msg_info)
                # quit()

                # # Insert into MySQL if not already there
                # insert_id = insert(dbh, msg_info)
                # print(insert_id)

                service.users().messages().delete(userId=user_id, id=message['id']).execute()
                print(message['id'], "deleted.")

        quit()

        while 'nextPageToken' in response:
            print("NEXT PAGE")
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q=query,
                                                pageToken=page_token).execute()
            for message in response['messages']:
                msg_info = get_message_info(service, user_id, message, 'From')
                msg_id = message['id']
                msg_info['message_id'] = msg_id
                pprint(msg_info)

                # Insert into MySQL if not already there
                insert_id = insert(dbh, msg_info)
                print(insert_id)
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

    

if __name__ == '__main__':
    main()
