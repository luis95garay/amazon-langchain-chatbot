from pathlib import Path

from fastapi.routing import APIRouter


templates_folder = Path(__file__).parent.parent / "templates"

router = APIRouter(tags=['startup'])


@router.get("/")
async def get():
    return{"data": "Excelente"}
