from http import HTTPStatus
from typing import Optional

from fastapi.responses import JSONResponse

FAILURE_MESSAGE = "failure"
SUCCESS_MESSAGE = "success"


class Responses:

    @classmethod
    def response(cls,
                 status: str,
                 error: Optional[str],
                 data: Optional[dict],
                 status_code: HTTPStatus):
        json_response = {"status": status, "error": error, "data": data}
        return JSONResponse(content=json_response, status_code=status_code)

    @classmethod
    def ok(cls, data=None):
        return cls.response(SUCCESS_MESSAGE, None, data, HTTPStatus.OK)

    @classmethod
    def created(cls, data=None):
        return cls.response(SUCCESS_MESSAGE, None, data, HTTPStatus.CREATED)

    @classmethod
    def accepted(cls, data=None):
        return cls.response(SUCCESS_MESSAGE, None, data, HTTPStatus.ACCEPTED)

    @classmethod
    def bad_request(cls, error=None):
        return cls.response(FAILURE_MESSAGE, error, None,
                            HTTPStatus.BAD_REQUEST)

    @classmethod
    def unauthorized(cls, error=None):
        return cls.response(FAILURE_MESSAGE, error, None,
                            HTTPStatus.UNAUTHORIZED)

    @classmethod
    def forbidden(cls, error=None):
        return cls.response(FAILURE_MESSAGE, error, None, HTTPStatus.FORBIDDEN)

    @classmethod
    def not_found(cls, error=None):
        return cls.response(FAILURE_MESSAGE, error, None, HTTPStatus.NOT_FOUND)

    @classmethod
    def internal_server_error(cls, error=None):
        return cls.response(FAILURE_MESSAGE, error, None,
                            HTTPStatus.INTERNAL_SERVER_ERROR)
