from collections import namedtuple

import pytest

from matchwell import gmail


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
def test_gmail_source():
    gs = gmail.GmailSource()
    assert gs.name == 'gmail'


def test_gmail_source_pull():
    gs = gmail.GmailSource()
    gs.pull()


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
            'exp': '2016-06-29T19:05:59.000000000',
        }),
    ]
    for tc in testcases:
        obs = gmail.get_datetime(tc.msg, tc.as_numpy)
        assert str(obs) == tc.exp
