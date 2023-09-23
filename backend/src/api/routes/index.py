from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi import Request
from src.api.utils import load_file_content
from fastapi.routing import APIRouter


templates_folder = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_folder))

router = APIRouter(tags=['startup'])


@router.on_event("startup")
async def startup_event():
    load_file_content()


@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
