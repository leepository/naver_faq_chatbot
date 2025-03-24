import os
import time

def get_api_env():
    """
    환경 변수에 설정되어 있는 API_ENV 조회
    :return:
    """
    return os.getenv('API_ENV', 'DEV')

def get_ttl_hash(seconds=864000):
    """
    Return the same value within 'seconds' time period
    :param seconds:
    :return:
    """
    return round(time.time() / seconds)
