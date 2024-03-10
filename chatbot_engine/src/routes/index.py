from pathlib import Path

from fastapi.routing import APIRouter

from src.utils import load_file_to_redis
from .response import Responses


templates_folder = Path(__file__).parent.parent / "templates"

router = APIRouter(tags=['startup'])


def update_all():
    load_file_to_redis('sagemaker_documentation.pkl', '9195173332994997420b3f236e0da21a')


@router.on_event("startup")
def startup_event():
    update_all()


@router.get("/")
async def get():
    return{"data": "Excelente"}


@router.post("/update")
async def update_files():
    update_all()
    return Responses.ok("Vectorstore updated")
