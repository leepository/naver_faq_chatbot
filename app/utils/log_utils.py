import logging
import time
import ujson

from datetime import datetime, timedelta
from fastapi.logger import logger
from starlette.requests import Request

from app.utils.common_utils import get_api_env

# logger 설정
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '[API_LOGGER] %(levelname)s: %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

async def api_logger(request: Request, response=None, error=None):
    api_env = get_api_env()
    time_format = "%Y-%m-%d %H:%M:%S"
    t = time.time() - request.state.start_time
    status_code = error.status_code if error is not None else response.status_code
    error_log = None
    user =  request.state.user if hasattr(request.state, 'user') else None
    if error:
        # frame = inspect.currentframe()
        frame = None
        if frame:
            error_file = frame.f_code.co_filename
            error_func = frame.f_code.co_name
            error_line = frame.f_lineno

        else:
            error_func = error_file = error_line = "UNKNOWN"

        error_log = dict(
            errorfunc=error_func,
            location="{0} line in {1}".format(str(error_line), error_file),
            raised=str(error.__class__.__name__),
            detail=error.detail
        )

    user_log = dict(
        client=request.state.ip,
        user=user.id if user is not None else None
    )

    log_dict = dict(
        url=request.url.path,
        method=str(request.method),
        statusCode=status_code,
        errorDetail=error_log,
        client=user_log,
        processedTime=str(round(t * 1000, 5)) + "ms",
        datetimeUTC=datetime.now().strftime(time_format),
        datetimeKST=(datetime.now() + timedelta(hours=9)).strftime(time_format)
    )

    if error:
        # traceback.print_exc()
        logger.error(ujson.dumps(log_dict))
    else:
        if api_env != 'TEST':
            logger.info(ujson.dumps(log_dict))
