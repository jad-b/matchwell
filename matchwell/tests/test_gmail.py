import base64
import uuid
from collections import namedtuple
from unittest.mock import patch

import pytest
import pandas as pd

from matchwell import gmail
from matchwell.gmail import GmailSource


def junk(n=12):
    """Create a random string of length _n_."""
    b = str(uuid.uuid4()).encode()
    s = base64.b64encode(b).decode()
    return s[:n]


@pytest.yield_fixture(scope='session')
def service():
    yield gmail.Gmail().connect()


@pytest.mark.skip(reason='Need to generate sample data')
def test_create_label(service, data):
    # Setup a test label
    TEST_LABEL_NAME = 'TestLabel'
    test_label = service.create_label(TEST_LABEL_NAME)
    # Randomly sample a row from our data
    test_email = data.sample(n=1)
    test_email_id = test_email.id.values[0]
    print("Testing %s" % test_email_id)
    assert test_label not in test_email.email.values[0]['labelIds']

    # Execute
    recv = service.add_gmail_labels(test_email_id,
                                    labels=[test_label['id']])

    # Assert
    assert test_label['id'] in recv['labelIds'], recv['labelIds']


@pytest.mark.skip(reason='Expensive operation')
def test_list_messages(service):
    msgs = service.list_messages()
    assert len(msgs) > 0


# GmailSource tests
def test_gmail_source_initialization():
    gs = gmail.GmailSource()
    assert gs.name == 'gmail'


@patch.object(GmailSource, '_transform', autospec=True)
@patch.object(GmailSource, '_extract', autospec=True)
def test_gmail_source_extract(mock_ex, mock_tf):
    gs = gmail.GmailSource()
    messages = [
        {'id': junk(), 'threadId': junk()},
        {'id': junk(), 'threadId': junk()},
        {'id': junk(), 'threadId': junk()},
    ]
    mock_ex.return_value = messages
    mock_tf.return_value = pd.DataFrame()

    gs.pull(newer_than='1988/12/14')

    mock_ex.assert_called_with(gs, 'after:1988/12/14')
    mock_tf.assert_called_with(gs, messages)


# Utility function tests
def test_get_datetime():
    TC = namedtuple('TestCase', ('msg', 'as_numpy', 'exp'))
    testcases = [
        TC(**{
            'msg': {'internalDate': '1467232146000'},
            'as_numpy': True,
            'exp': '2016-06-29T20:29:06+0000',
        }),
        TC(**{
            'msg': {'internalDate': '1467227159000'},
            'as_numpy': False,
            'exp': '2016-06-29 19:05:59',
        }),
    ]
    for tc in testcases:
        obs = gmail.get_datetime(tc.msg, tc.as_numpy)
        assert str(obs) == tc.exp
