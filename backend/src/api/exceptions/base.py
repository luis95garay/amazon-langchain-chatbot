from typing import Callable


class HighsException(Exception):
    pass


class HTTPException(HighsException):
    def __init__(self, message: str, func: Callable) -> None:
        self.message = message
        self.to_response = func
