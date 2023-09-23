from fastapi import FastAPI

from . import (
    data_preprocessing, vectorstore_processing,
    virtual_assistant, index
)


def route_registry(app: FastAPI):
    app.include_router(index.router)
    app.include_router(data_preprocessing.router)
    app.include_router(vectorstore_processing.router)
    app.include_router(virtual_assistant.router)
