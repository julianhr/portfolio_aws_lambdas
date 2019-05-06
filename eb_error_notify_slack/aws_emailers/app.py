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

    if 'Records' not in event:
        logger.error(f'missing key "Records" in event: {event}')
        return

    for record in event['Records']:
        try:
            sns = record['Sns']
            message = f"""
<!channel> Elastic Beanstalk issue:
Subject: {sns.get('Subject')}
Message: {sns.get('Message')}
Timestamp: {sns.get('Timestamp')}
"""
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session = requests.Session()
            session.mount(URL, adapter)
            resp = session.post(
                url=URL,
                json={'text': message.strip()},
                timeout=5
            )
            resp.raise_for_status()
            logger.info(f'successful response body: {resp.text}')
        except Exception as error:
            logger.error(error, exc_info=True)
