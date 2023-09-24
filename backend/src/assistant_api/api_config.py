from fastapi import FastAPI
from .routes import route_registry


def get_api() -> FastAPI:
    app = FastAPI()
    route_registry(app)
    return app
