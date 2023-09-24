from assistant_api.utils import load_file_content
from fastapi.routing import APIRouter


router = APIRouter(tags=['startup'])


@router.on_event("startup")
async def startup_event():
    load_file_content()
