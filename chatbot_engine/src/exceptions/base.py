from typing import Callable


class HTTPException(Exception):
    def __init__(self, message: str, func: Callable) -> None:
        self.message = message
        self.to_response = func
