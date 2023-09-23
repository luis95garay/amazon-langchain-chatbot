from fastapi import FastAPI
from .exceptions import registry_exceptions
from .routes import route_registry


def get_api() -> FastAPI:
    app = FastAPI()
    route_registry(app)
    registry_exceptions(app)
    return app
