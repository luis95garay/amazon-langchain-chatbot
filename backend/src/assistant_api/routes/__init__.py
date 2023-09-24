from fastapi import FastAPI

from . import (
    virtual_assistant, index
)


def route_registry(app: FastAPI):
    app.include_router(index.router)
    app.include_router(virtual_assistant.router)
