import asyncio
import os
import time
import uuid

from typing import List, AsyncIterator

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

def get_uuid():
    """
    UUID 생성
    :return:
    """
    return str(uuid.uuid4())

async def async_list_iterator(items: List[str]) -> AsyncIterator[str]:
    for item in items:
        await asyncio.sleep(0.1)
        yield item
