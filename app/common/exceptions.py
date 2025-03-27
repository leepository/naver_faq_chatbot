from app.common.constants import StatusCode

class APIException(Exception):
    def __init__(
            self,
            *,
            status_code: StatusCode = StatusCode.HTTP_400,
            detail: str,
            ex: Exception
    ):
        self.status_code = status_code
        self.detail = detail
        self.ex = ex
        super().__init__(ex)

async def exception_handler(error: Exception):
    return APIException(ex=error, detail=str(error))

