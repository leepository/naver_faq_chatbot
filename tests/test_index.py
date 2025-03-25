import pytest
from tests.base import TestBase

class TestIndex(TestBase):

    def test100_index(self, client):
        url = '/'
        result = self.run_request(
            test_client=client,
            url=url,
            method='GET'
        )
        assert result['status_code'] == 200

    def test200_health_check(self, client):
        url = '/health'
        result = self.run_request(
            test_client=client,
            method='GET',
            url=url
        )
        assert result['status_code'] == 200
