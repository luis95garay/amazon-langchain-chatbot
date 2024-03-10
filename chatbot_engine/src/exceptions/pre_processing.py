from src.exceptions.base import HTTPException
from src.responses.response import Responses


class NotProcessingException(HTTPException):
    def __init__(self) -> None:
        super().__init__("Not found", Responses.not_found)


class StillProcessingException(HTTPException):
    def __init__(self) -> None:
        super().__init__("Not ready", Responses.pending)


class Internal_server_errorException(HTTPException):
    def __init__(self, message) -> None:
        super().__init__(message, Responses.internal_server_error)


class BadRequestException(HTTPException):
    def __init__(self, message) -> None:
        super().__init__(message, Responses.unprocessable_entity)


class NotFoundException(HTTPException):
    def __init__(self, message) -> None:
        super().__init__(message, Responses.not_found)
