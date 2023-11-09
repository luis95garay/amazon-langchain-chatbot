from fastapi import FastAPI

from . import (
    data_preprocessing, text_extraction, status, vectorstore_processing
)


def route_registry(app: FastAPI):
    # app.include_router(text_extraction.router)
    # app.include_router(data_preprocessing.router)
    app.include_router(vectorstore_processing.router)
    app.include_router(status.router)
