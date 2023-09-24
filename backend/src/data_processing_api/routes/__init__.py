from fastapi import FastAPI

from . import (
    data_preprocessing, text_extraction
)


def route_registry(app: FastAPI):
    app.include_router(text_extraction.router)
    app.include_router(data_preprocessing.router)
