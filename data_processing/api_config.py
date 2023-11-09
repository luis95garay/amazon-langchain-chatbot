from fastapi import FastAPI
from api.exceptions import registry_exceptions
from api.v2.routes import route_registry as route_registry_v2


def get_api() -> FastAPI:
    app = FastAPI(title="Data Processing API")
    route_registry_v2(app)
    registry_exceptions(app)
    return app
