"""
gmail
=====
Tools for common operations involving Gmail's API.
"""
import argparse
import base64
import email
import os

import httplib2
import oauth2client
from apiclient import discovery, errors
from bs4 import BeautifulSoup
from oauth2client import client, tools


class Gmail:
    """Gmail encapsulates talking to the Gmail API."""
    # If modifying these scopes, delete your previously saved credentials
    scopes = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
    ]
    client_secret_file = 'client_secret.json'
    application_name = 'MatchWell'

    def __init__(self,
                 user_id='me',
                 credentials='gmail-python.json',
                 service=None):
        """
        Args:
            service: Google API service instance.
        """
        self.credentials = credentials
        self.user = user_id
        self.service = service

    def get_credentials(self, flags=None):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, self.credentials)

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(
                    self.client_secret_file, self.scopes)
            flow.user_agent = self.application_name
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def build_service(self):
        """Shows basic usage of the Gmail API.

        Creates a Gmail API service object and outputs a list of label names
        of the user's Gmail account.
        """
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args([
            '--noauth_local_webserver'
        ])
        credentials = self.get_credentials(flags)
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

    def get_label_ids(self, labels=[]):
        """Retrieve the label ID for each label."""
        try:
            response = self.service.users().labels().list(
                    userId=self.user
                    ).execute()
            return {
                lbl['name']: lbl['id'] for lbl in response['labels']
                if lbl['name'] in labels
            }
        except errors.HttpError:
            raise

    def create_label(self, name):
        """Create or retrieve label, if already exists."""
        try:
            return self.service.users().labels().create(
                userId=self.user,
                body={
                    'messageListVisibility': 'hide',
                    'labelListVisibility': 'labelShow',
                    'name': name,
                }).execute()
        except errors.HttpError as e:
            if e.resp.status == 409:  # Something other than label exists
                all_labels = self.service.users().labels().list(
                    userId=self.user
                ).execute()
                print("retrieved %d labels" % len(all_labels['labels']))
                return next(l for l in all_labels['labels']
                            if l['name'] == name)
            raise

    # Retrieve all messages under each label
    def get_message_ids(self, labels=[]):
        d = {}
        for label in labels:
            print("Retrieving all messages with label(s) '{}'".format(label))
            try:
                response = self.service.users().messages().list(
                    userId=self.user, labelIds=[label]
                ).execute()
                d[label] = []
                if 'messages' in response:
                    d[label].extend(response['messages'])

                while 'nextPageToken' in response:
                    page_token = response['nextPageToken']
                    response = self.service.users().messages().list(
                        userId=self.user, labelIds=[label],
                        pageToken=page_token
                    ).execute()
                    d[label].extend(response['messages'])
                print("Retrieved {:d} messages".format(len(d[label])))
            except errors.HttpError as e:
                print("Error: ", e)
                return None
        return d

    def get_email(gmail, msg_id, format='full', user_id='me'):
        """Download an email in Google's pre-hierarchied format.

        https://developers.google.com/gmail/api/v1/reference/users/messages/get

        Returns:
            https://developers.google.com/gmail/api/v1/reference/users/messages
        """
        msg = gmail.users().messages().get(
            userId=user_id, id=msg_id, format=format
        ).execute()
        # Convert raw emails into Python objects
        if format == 'raw':
            msg_str = base64.urlsafe_b64decode(msg['raw']).decode()
            return email.message_from_string(msg_str)
        return msg


# Utility functions
def extract_gmail_text(payload):
    """Parse the *most likely* source of human-readable text from
    the email.

    "Most likely" uses the following search along the MIME types of
    messages parts:

    * text/plain, which is base64 decoded.
    * text/html, which is base64 decoded and then
      parsed for text elements.
    """
    if payload['mimeType'] == 'text/plain':
        return base64.urlsafe_b64decode(payload['body']['data']).decode()
    if payload['mimeType'] == 'text/html':
        return parse_html_email(payload['body']['data'])
    # Else, recurse
    for part in payload.get('parts', []):
        return extract_gmail_text(part)


def extract_by_mimetype(msg, mimetype='text/plain'):
    """Pull the first text/plain message part out of the email."""
    for part in msg.walk():
        if part.get_content_type() == mimetype:
            return part.get_payload(decode=True)


def parse_html_email(data):
    """Parse a text/html Email message part."""
    text = base64.urlsafe_b64decode(data).decode()
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()
