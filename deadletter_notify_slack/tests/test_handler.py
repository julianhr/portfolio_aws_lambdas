import os
import re
import json
import pytest
from pprint import pprint

from aws_emailers import app


@pytest.fixture()
def test_event():
    return {
        "body": "{\"message\": \"hello world\"}",
        "path": "/path/to/resource",
    }


def test_logger_info(mocker, test_event):
    context = { 'body': 'test body' }
    pprint(test_event)

    mocker.patch('aws_emailers.app.logger')
    mocker.patch('aws_emailers.app.requests')
    app.lambda_handler(test_event, context)
    from aws_emailers.app import logger

    assert logger.info.call_count == 3


def test_posting_to_slack(mocker, test_event):
    mocker.patch('aws_emailers.app.logger')
    session_mock = mocker.Mock()
    mocker.patch(
        'aws_emailers.app.requests.Session',
        side_effect=lambda: session_mock
    )
    app.lambda_handler(test_event, '')
    from aws_emailers.app import requests
    message = f'*Deadletter Notification:*\n```{json.dumps(test_event)}```'

    session_mock.post.assert_called_once_with(
        url=os.environ['URL'],
        json={ 'text': message },
        timeout=5
    )


def test_post_slack_failure(mocker, test_event):
    mocker.patch('aws_emailers.app.logger')
    mocker.patch(
        'aws_emailers.app.requests.Session.post',
        side_effect=ConnectionError('test error')
    )
    try:
        app.lambda_handler(test_event, '')
    except:
        pass

    from aws_emailers.app import logger

    arg = logger.error.call_args[0][0]
    assert logger.error.call_count == 1
    assert type(arg) == ConnectionError
