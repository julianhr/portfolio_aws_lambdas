import os
import json
import logging
from botocore.vendored import requests
from pprint import pprint


URL = os.environ['URL']
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    logger.info(context)

    try:
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session = requests.Session()
        session.mount(URL, adapter)
        message = f'*Deadletter Notification:*\n```{json.dumps(event)}```'
        resp = session.post(
            url=URL,
            json={ 'text': message },
            timeout=5,
        )
        resp.raise_for_status()
        logger.info(f'successful response body: {resp.text}')
    except Exception as error:
        logger.error(error, exc_info=True)
        raise error
