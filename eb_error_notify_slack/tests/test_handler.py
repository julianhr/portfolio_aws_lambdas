import os
import re
import json
import pytest
from pprint import pprint

from aws_emailers import app


path = os.path.dirname(os.path.abspath(__file__))
fh = open(os.path.join(path, '../event.json'))
loaded_event = json.load(fh)
fh.close()


@pytest.fixture()
def test_event():
    return loaded_event


def test_logger_info(mocker):
    """ logger.info is called 4 times if all goes well,
    twice for event and context, and once for each record """

    event = {
        "Records": [
            {
                "Sns": {
                    "Subject": "test subject",
                    "Message": "test message",
                    "Timestamp": "test timestamp" 
                }
            },
            {
                "Sns": {
                    "Subject": "test subject",
                    "Message": "test message",
                    "Timestamp": "test timestamp" 
                }
            }
        ]
    }

    context = {
        'body': 'test body'
    }

    mocker.patch('aws_emailers.app.logger')
    mocker.patch('aws_emailers.app.requests')
    app.lambda_handler(event, context)
    from aws_emailers.app import logger

    assert logger.info.call_count == 4


def test_posting_to_slack(mocker):
    event = {
        "Records": [
            {
                "Sns": {
                    "Subject": "test subject",
                    "Message": "test message",
                    "Timestamp": "test timestamp" 
                }
            }
        ]
    }

    mocker.patch('aws_emailers.app.logger')
    session_mock = mocker.Mock()
    mocker.patch(
        'aws_emailers.app.requests.Session',
        side_effect=lambda: session_mock
    )
    app.lambda_handler(event, '')
    from aws_emailers.app import requests

    sns = event['Records'][0]['Sns']
    message = f"""
<!channel> Elastic Beanstalk issue:
Subject: {sns['Subject']}
Message: {sns['Message']}
Timestamp: {sns['Timestamp']}
"""

    session_mock.post.assert_called_once_with(
        url=os.environ['URL'],
        json={'text': message.strip()},
        timeout=5
    )


def test_record_key_missing(mocker):
    event = {
        "Invalid": [
            {
                "Sns": {
                    "Subject": "test subject",
                    "Message": "test message",
                    "Timestamp": "test timestamp" 
                }
            },
        ]
    }

    mocker.patch('aws_emailers.app.logger')
    app.lambda_handler(event, '')
    from aws_emailers.app import logger

    assert logger.error.call_count == 1
    assert re.match(r'missing key', logger.error.call_args[0][0])


def test_malformed_record_keys(mocker):
    event = {
        "Records": [
            {
                "InvalidKey": {}
            },
        ]
    }

    mocker.patch('aws_emailers.app.logger')
    app.lambda_handler(event, '')
    from aws_emailers.app import logger

    arg = logger.error.call_args[0][0]
    assert logger.error.call_count == 1
    assert type(arg) == KeyError


def test_post_slack_failure(mocker):
    mocker.patch('aws_emailers.app.logger')
    mocker.patch(
        'aws_emailers.app.requests.Session.post',
        side_effect=ConnectionError('test error')
    )
    app.lambda_handler(loaded_event, '')
    from aws_emailers.app import logger

    arg = logger.error.call_args[0][0]
    assert logger.error.call_count == 2
    assert type(arg) == ConnectionError
