from fastapi import FastAPI, Request

from .base import HTTPException


def registry_exceptions(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def exception_handler(
            request: Request,
            exc: HTTPException):
        return exc.to_response(exc.message)
