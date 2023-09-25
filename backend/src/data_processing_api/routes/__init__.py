from fastapi import FastAPI

from . import text_extraction


def route_registry(app: FastAPI):
    app.include_router(text_extraction.router)
