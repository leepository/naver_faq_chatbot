import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.container import Container
from app.common.config import get_config
from app.domains.domain_routers import domain_router
from app.domains.index.apis import index_router
from app.utils.common_utils import (
    get_api_env,
    get_ttl_hash
)

def create_app(api_env: str = None):
    if api_env is not None:
        os.environ['API_ENV'] = api_env
    else:
        api_env = get_api_env()

    conf = get_config(api_env=api_env, ttl_hash=get_ttl_hash())

    app = FastAPI(
        title='Naver FAQ Chatbot',
        version='v0.1.0-dev',
        contact={
            'nmame': 'Kevin Lee',
            'email': 'hleepublic@gmail.com'
        },
        docs_url='/docs',
        redoc_url='/redoc',
        debug=conf.DEBUG,
        swagger_ui_parameters={'persistAuthorization': True}
    )

    container = Container()
    app.container = container

    # Regist middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts = conf.TRUSTED_HOSTS
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Regist routers
    app.include_router(index_router)
    app.include_router(domain_router)

    return app
