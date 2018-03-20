import os
import logging
from time import time, sleep
import requests

check_timeout = os.getenv('POSTGRES_CHECK_TIMEOUT', 60)
check_interval = os.getenv('POSTGRES_CHECK_INTERVAL', 5)
interval_unit = 'second' if check_interval == 1 else 'seconds'
start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

config = {
    'host': 'server',
    'port': '8000'
}


def server_isready(host, port):
    while time() - start_time < check_timeout:
        sleep(check_interval)
        try:
            requests.get('http://%s:%s/' % (host, port))
            logger.info('Server is ready! ✨💅')
            return True
        except requests.exceptions.ConnectionError:
            pass

    logger.error(f'We could not connect to the server within {check_timeout} seconds.')
    return False


server_isready(**config)
