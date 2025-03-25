from openai.types.chat.chat_completion import ChatCompletionMessage, Choice, CompletionUsage, ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk, ChoiceDelta, Choice as Choice_chunk
from openai.types.completion_usage import CompletionTokensDetails, PromptTokensDetails
from openai import AsyncStream
from pytest_mock import mocker

ask_response = ChatCompletion(
    id='chatcmpl-BEqQlB1gpsrejWQOGnmqp4rrjNUYv',
    choices=[
        Choice(
            finish_reason='stop',
            index=0,
            logprobs=None,
            message=ChatCompletionMessage(
                content='{\n    "answer": "[MOCK] 해외 사업자는 가입 신청 시 필요한 서류를 준비하여 업로드해야 합니다. 필요한 서류로는 대표자 여권 사본, 사업자등록증 사본, 그리고 해외계좌 인증 서류(또는 사업자 또는보 > 심사내역 조회] 메뉴에서 업로드할 수 있습니다. 모든 서류 제출 후 3영업일 이내에 심사가 진행됩니다.",\n    "questions": [\n        "해외 사업자로 가입할 때 필요한 서류는 무엇자의 가입 심사는 얼마나 걸리나요?"\n    ],\n    "related_question": true\n}',
                refusal=None,
                role='assistant',
                annotations=[],
                audio=None,
                function_call=None,
                tool_calls=None
            )
        )
    ],
    created=1742877835,
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier='default',
    system_fingerprint='fp_eb9dce56a8',
    usage=CompletionUsage(
        completion_tokens=190,
        prompt_tokens=1684,
        total_tokens=1874,
        completion_tokens_details=CompletionTokensDetails(
            accepted_prediction_tokens=0,
            audio_tokens=0,
            reasoning_tokens=0,
            rejected_prediction_tokens=0
        ),
        prompt_tokens_details=PromptTokensDetails(
            audio_tokens=0,
            cached_tokens=0
        )
    )
)

def get_chat_mockdata(mocker):
    chat_response = mocker.AsyncMock(spec=AsyncStream)
    chat_response.__aiter__.return_value = [
        ChatCompletionChunk(
            id='chatcmpl-BErXvd0064VnGPjBuVV1Pf92GW6OX',
            choices=[
                Choice_chunk(
                    delta=ChoiceDelta(
                        content='MOCK-1',
                        function_call=None,
                        refusal=None,
                        role=None,
                        tool_calls=None
                    ),
                    finish_reason=None,
                    index=0,
                    logprobs=None
                )
            ],
            created=1742882123,
            model='gpt-4o-2024-08-06',
            object='chat.completion.chunk',
            service_tier='default',
            system_fingerprint='fp_eb9dce56a8',
            usage=None
        ),
        ChatCompletionChunk(
            id='chatcmpl-BErXvd0064VnGPjBuVV1Pf92GW6OX',
            choices=[
                Choice_chunk(
                    delta=ChoiceDelta(
                        content='MOCK-2',
                        function_call=None,
                        refusal=None,
                        role=None,
                        tool_calls=None
                    ),
                    finish_reason=None,
                    index=0,
                    logprobs=None
                )
            ],
            created=1742882123,
            model='gpt-4o-2024-08-06',
            object='chat.completion.chunk',
            service_tier='default',
            system_fingerprint='fp_eb9dce56a8',
            usage=None
        ),
        ChatCompletionChunk(
            id='chatcmpl-BErXvd0064VnGPjBuVV1Pf92GW6OX',
            choices=[
                Choice_chunk(
                    delta=ChoiceDelta(
                        content=None,
                        function_call=None,
                        refusal=None,
                        role=None,
                        tool_calls=None
                    ),
                    finish_reason='stop',
                    index=0,
                    logprobs=None
                )
            ],
            created=1742882123,
            model='gpt-4o-2024-08-06',
            object='chat.completion.chunk',
            service_tier='default',
            system_fingerprint='fp_eb9dce56a8',
            usage=None
        )
    ]

    return chat_response