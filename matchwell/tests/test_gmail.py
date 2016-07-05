import pytest

from matchwell.gmail import Gmail


@pytest.yield_fixture(scope='session')
def gmail():
    gmail = Gmail()
    gmail.connect()
    yield gmail


def test_create_label(gmail, data):
    # Setup a test label
    TEST_LABEL_NAME = 'TestLabel'
    test_label = gmail.create_label(TEST_LABEL_NAME)
    # Randomly sample a row from our data
    test_email = data.sample(n=1)
    test_email_id = test_email.id.values[0]
    print("Testing %s" % test_email_id)
    assert test_label not in test_email.email.values[0]['labelIds']

    # Execute
    recv = gmail.add_gmail_labels(test_email_id,
                                  labels=[test_label['id']])

    # Assert
    assert test_label['id'] in recv['labelIds'], recv['labelIds']


def test_list_messages(gmail):
    msgs = gmail.list_messages()
    assert len(msgs) > 0
