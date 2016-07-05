#!/usr/bin/env python3
# coding: utf-8

"""
MatchWell's Daemon
==================
Learn to predict hierarchical categories of text.

The workflow looks like this:

1. Data Acquisition
    1. Authorize w/ Gmail
    2. Lookup IDs of labels
    3. Get list of message IDs by label ID
    4. Download all emails
    5. Parse text from email
2. Feature Extraction
    1. Tokenize
    2. TF-IDF
3. Learn & Predict
    1. Train
    2. Cross-Validate
    3. Visualize
"""
import pandas as pd

from matchwell.gmail import Gmail

# Constants
POS_LABEL = 'job-offers/yes'
NEG_LABEL = 'job-offers-no'
DATAFILE = './emails.json'
CLASSIFIER = './text_pipeline.pkl'


def download_emails(gmail=None, df=None, labels=[]):
    """Retrieves emails for the user.

    Args:
        df (pandas.DataFrame): Pre-existing data. Only non-existent emails
            will be retrieved.
    Returns:
        A new DataFrame w/ downloaded emails.
    """
    reqd_columns = ['id', 'labelName', 'email']
    if df is None:
        df = pd.DataFrame(columns=reqd_columns)
    else:
        assert reqd_columns in df.columns
    if gmail is None:
        gmail = Gmail()  # Ctrl-Enter to save verification code
    labels = [POS_LABEL, NEG_LABEL]

    # Get all labels, and build a map of label names => label IDs
    lbl_name_ids = gmail.get_label_ids(labels)
    label_ids = [lbl_name_ids[lbl] for lbl in labels]
    # Lookup message IDs associated with labels: labelName => [{message IDs,
    # threadID}]
    messages = {label_ids: gmail.list_messages([label_id])
                for label_id in label_ids}

    # Load messages into the DataFrame
    for lbl, msgs in messages.items():
        tmpdf = pd.DataFrame(msgs)
        tmpdf['labelName'] = lbl
        df = df.append(tmpdf, ignore_index=True)
    df.head()

    # Download each missing email by ID
    def get_emails(row):
        return gmail.get_email(gmail, row.id)

    # Retrieve each missing email
    df['email'] = df.apply(get_emails, axis=1)
    df.head()

    def fill_in_text(row):
        return gmail.extract_gmail_text(row.email['payload'])

    # Extract text from the email
    df['text'] = df.apply(fill_in_text, axis=1)
    df.head()
    df.to_json(DATAFILE)
