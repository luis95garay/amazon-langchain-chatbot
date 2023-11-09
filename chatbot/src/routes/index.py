from pathlib import Path

from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.routing import APIRouter

from src.utils import (
    load_file_content
)
from .response import Responses
from src.schemas import UpdateFile


templates_folder = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_folder))

router = APIRouter(tags=['startup'])


@router.on_event("startup")
def startup_event():
    load_file_content()


@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/update")
async def update_files(params: UpdateFile):
    load_file_content(params.file_name)
    return Responses.ok("Vectorstore updated")
