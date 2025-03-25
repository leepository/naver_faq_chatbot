import pytest
from tests.base import TestBase
from tests.mock_data import ask_response, get_chat_mockdata

class TestChatbot(TestBase):

    def test100_ask_api(self, client, mocker):
        mocker.patch(
            "app.domains.chatbot.externals.openai.openai_external.OpenAIExternal.query",
            return_value=ask_response
        )

        url = '/chatbot/ask'
        data = {
            'query': '해외 사업자의 가입 기준은?'
        }
        result = self.run_request(
            test_client=client,
            method='POST',
            url=url,
            data=data
        )
        assert result['status_code'] == 200
        assert result['data'] is not None
        assert result['data']['answer'] is not None

    def test200_chat_api(self, client, mocker):
        chat_response = get_chat_mockdata(mocker)
        mocker.patch(
            "app.domains.chatbot.externals.openai.openai_async_external.OpenAIAsyncExternal.query",
            return_value=chat_response
        )

        url = '/chatbot/chat'
        data = {
            'query': '해외 사업자의 가입 기준은?'
        }
        result = self.run_request(
            test_client=client,
            method='POST',
            url=url,
            data=data
        )

        assert result['status_code'] == 200
        assert result['data'] is not None