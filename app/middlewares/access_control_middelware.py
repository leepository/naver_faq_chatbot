import time

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Callable

from app.common.exceptions import APIException, exception_handler
from app.utils.log_utils import api_logger

class AccessControl(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        request.state.start_time = time.time()

        ip = request.headers['x-forwarded-for'] if 'x-forwarded-for' in request.headers.keys() else request.client.host
        request.state.ip = ip.split(',')[0] if ',' in ip else ip

        response = await call_next(request)
        await api_logger(request=request, response=response)


        return response