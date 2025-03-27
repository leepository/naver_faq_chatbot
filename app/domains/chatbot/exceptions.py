from app.common.constants import StatusCode
from app.common.exceptions import APIException

class LLMLengthOverError(APIException):
    def __init__(self):
        exception_detail = 'Insufficient token : LMM Response length over'
        super().__init__(
            status_code=StatusCode.HTTP_400,
            detail=exception_detail,
            ex=Exception(exception_detail)
        )
