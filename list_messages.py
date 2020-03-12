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

from pprint import pprint

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_message_header(service, user_id, message, header_name):
    msg_id = message['id']
    msg = service.users().messages().get(userId=user_id, id=msg_id).execute()
    payload = msg['payload']
    headers = payload['headers']

    header_value = ''
    for header in headers:
        if header['name'] == header_name:
            header_value = header['value']

    return header_value

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

    # List All Messages
    # https://developers.google.com/gmail/api/v1/reference/users/messages/list#examples
    user_id = 'me'
    query = ''
    from_values = defaultdict(int)
    try:
        response = service.users().messages().list(userId='me',
                                                q='').execute()
        messages = []
        if 'messages' in response:
            # print(response['messages'])
            for message in response['messages']:
                from_header = get_message_header(service, user_id, message, 'From')
                print(from_header)
                from_values[from_header] += 1

            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            print("NEXT PAGE")
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q='',
                                                pageToken=page_token).execute()
            messages.extend(response['messages'])
            for message in response['messages']:
                from_header = get_message_header(service, user_id, message, 'From')
                print(from_header)
                from_values[from_header] += 1

        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

    

if __name__ == '__main__':
    main()
