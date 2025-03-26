import os
import uvicorn

from app.common import config
from app.utils.common_utils import get_ttl_hash

# Huggingface tokenizer 라이브러리 병령처리에 대한 경고 대응
os.environ['TOKENIZERS_PARALEELISM'] = 'false'

if __name__ == '__main__':
    api_env = os.getenv('API_ENV', 'DEV')
    conf = config.get_config(api_env=api_env, ttl_hash=get_ttl_hash())

    uvicorn.run(
        'app.main:create_app',
        host='0.0.0.0',
        port=9000,
        factory=True,
        reload=conf.PROJECT_RELOAD
    )
