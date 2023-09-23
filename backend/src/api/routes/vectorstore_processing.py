import uuid

from fastapi import BackgroundTasks, Path
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.responses.response import Responses
from src.api.services.vectorstore_processing import (
    VectorstoreProcessingService
    )
from src.api.schemas import Dataset


router = APIRouter(tags=['vectorstore_processing'])


@router.post('/process_vectorstore')
async def process_vectorstore(
    bg_task: BackgroundTasks,
    dataset: Dataset
):
    key = dataset.name + "-" + dataset.method
    if (_uuid := VectorstoreProcessingService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        VectorstoreProcessingService.process_vectorstore,
        dataset.name, dataset.method, key, _uuid)
    return Responses.created(_uuid)


@router.get("/vs/get_status/{id}")
def result(id: str = Path(...)):
    output = VectorstoreProcessingService.get_status(id)
    return JSONResponse(output)
