"""
gmail
=====
Tools for common operations involving Gmail's API.
"""
import argparse
import base64
import email
import json
import os
import time
from datetime import datetime

import httplib2
import numpy as np
import oauth2client
import pandas as pd
from apiclient import discovery, errors
from bs4 import BeautifulSoup
from oauth2client import client, tools

from matchwell import util
from matchwell.source import Sourcerer


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
        # Properties
        self._labels = None
        self._label_names = None
        self._label_ids = None

    def connect(self):
        """Creates a Gmail API service object."""
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args([
            '--noauth_local_webserver'
        ])
        credentials = self.get_credentials(flags)
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)
        return self

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

    @property
    def labels(self):
        """Build a ID=>Name & Name=>ID mapping for labels"""
        if not self._labels:
            try:
                response = self.service.users().labels().list(
                        userId=self.user
                        ).execute()
                self._labels = response['labels']
            except errors.HttpError:
                raise
        return self._labels

    @property
    def label_names(self):
        if self._label_names:
            self._label_names = {lbl['name']: lbl['id'] for lbl in
                                 self.labels}
        return self._label_names

    @property
    def label_ids(self):
        if not self._label_ids:
            self._label_ids = {lbl['id']: lbl['name'] for lbl in self.labels}
        return self._label_ids

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

    @property
    def label_tree(self):
        label_names = set([l['name'] for l in self.labels])
        return util.build_prefix_tree(label_names)

    def print_label_tree(self):
        """Print a JSON representation of your label hierarchy."""
        print(json.dumps(self.label_tree, indent=2))

    def list_messages(self, label_ids=None, limit=None, query=None):
        """Retrieve a list of {msgId, threadId} by label ID(s).

        Args:
            label_ids (List[str]): List of specific label IDs to retrieve. None
                implies messages of *any* labels should be retrieved.
            limit (int): Total number of messages to collect.
            query (str): Gmail query string.
        Returns:
           List(dict)
        """
        list_kwargs = {'userId': self.user,
                       'q': query}
        if label_ids is not None:
            list_kwargs['labelIds'] = label_ids
            print("Retrieving all messages with label ID(s) '{}'"
                  .format(label_ids))
        else:
            print("Retrieving ALL messages")

        start = time.clock()
        try:
            response = self.service.users().messages().list(
                    **list_kwargs
                ).execute()

            count = 0
            if 'messages' in response:
                print("Retrieved %d message IDs in %.3f seconds" %
                      (response['resultSizeEstimate'], time.clock() - start))
                yield response['messages']
                count += response['resultSizeEstimate']

            while 'nextPageToken' in response:
                now = time.clock()
                list_kwargs['pageToken'] = response['nextPageToken']
                response = self.service.users().messages().list(
                        **list_kwargs
                    ).execute()
                print("Retrieved another %d message IDs in %.3f seconds" %
                      (response['resultSizeEstimate'], time.clock() - now))
                yield response['messages']
                count += response['resultSizeEstimate']
                if limit is not None and count >= limit:
                    print("Collected %d message IDs; stopping" % count)
                    break
        except errors.HttpError:
            print("Errored on pageToken='%s'" %
                  list_kwargs.get('nextPageToken', 'None!'))
            raise

        print("Retrieved %d total message IDs in %.3f seconds" %
              (count, time.clock() - start))

    def get_email(self, msg_id, format='full', user_id='me'):
        """Download a Users.Message resource, i.e. Gmail's format for email.

        https://developers.google.com/gmail/api/v1/reference/users/messages/get

        Returns:
            https://developers.google.com/gmail/api/v1/reference/users/messages
        """
        msg = self.service.users().messages().get(
            userId=user_id, id=msg_id, format=format
        ).execute()
        # Convert raw emails into Python objects
        if format == 'raw':
            msg_str = base64.urlsafe_b64decode(msg['raw']).decode()
            return email.message_from_string(msg_str)
        return msg

    def download_emails(self, msgs):
        """Download the raw emails.

        Args:
            msgs: List of results from list_messages; dicts containing 'msgId'
                and 'threadId'.
        Returns:
            List[:class:`users.messages.Resource`]: List of full-format emails.
        """
        if len(msgs) > 1000:
            print("Can only batch <=1000 downloads at a time")
            return
        emails = []

        def callback(request_id, response, exception):
            if exception is not None:
                pass
            else:
                emails.append(response)

        batch = self.service.new_batch_http_request()
        for msg in msgs:
            batch.add(
                self.serivce.users().messages().get(
                    userId='me', id=msg['id'], format='full'
                )
            )
        batch.execute()
        return emails


class GmailSource(Sourcerer):
    name = 'gmail'

    def __init__(self, gmail=None):
        self._gmail = gmail

    @property
    def gmail(self):
        if self._gmail is None:  # Initialize
            self._gmail = Gmail().connect()
        return self._gmail

    def pull(self, newer_than=None, **kwargs):
        """Retrieve emails."""
        if newer_than is not None:
            query = 'after:' + newer_than
        else:
            query = None

        return self._transform(self._extract(query))

    def _extract(self, query):
        messages = []
        for msgs in self.gmail.list_messages(self, query=query):
            messages.extend(self.gmail.download_emails(msgs))
        return messages

    def _transform(self, messages):
        df = pd.DataFrame()
        df['raw'] = messages
        df['timestamp'] = df.apply(lambda x: get_datetime(x.raw, True), axis=1)
        df.set_index('timestamp')
        df['type'] = self.name
        df['text'] = df.apply(
            lambda x: extract_gmail_text(x.raw['payload']), axis=1)
        # Remove null entries
        df = df[df['text'].notnull()]
        # Translate IDs to string names
        df['labels'] = df.apply(
            lambda x: [self.gmail.label_ids[lbl] for lbl
                       in x.raw.get('labelIds', [])],
            axis=1)
        # Drop unwanted labels
        blacklist = ['CHAT', 'SMS']
        for blk in blacklist:
            df = df.apply(
                lambda x: util.contains_substring(blk, x['labels'],
                                                  inverse=True),
                axis=1)
        # Message id serves as the unique ID for the message;
        # could turn into the full URL
        df['id'] = df.apply(lambda x: x.raw['id'], axis=1)
        return df


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


def get_datetime(message, numpy=True):
    """Extract the datetime from the Gmail message.

    Args:
        message (dict): Message to pull the datetime from.
        numpy (bool): Output as :class:`numpy.datetime64`, else
            :class:`datetime.datetime`.
    Returns:
        :class:`numpy.datetime64` if :arg:`numpy` is True, else
        :class:`datetime.datetime`.
    """
    # Convert from milliseconds to seconds
    epoch = int(message['internalDate']) / 1e3
    dt = datetime.utcfromtimestamp(epoch)
    if numpy:
        return np.datetime64(dt.isoformat())
    return dt


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
