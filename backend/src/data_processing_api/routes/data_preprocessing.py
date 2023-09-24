import uuid
from tempfile import NamedTemporaryFile

from fastapi import BackgroundTasks, File, Form, Path, UploadFile
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from data_processing_api.responses.response import Responses
from data_processing_api.services.data_preprocessing import (
    DataPreprocessingService
)
from data_processing_api.schemas import (
    OnlineSource, UnstructuredLocalSource
)


router = APIRouter(tags=['data_preprocessing'])


@router.post('/data_preprocessing/online')
async def dp_unstructured_online_source(
    bg_task: BackgroundTasks,
    task_info: OnlineSource
):
    key = task_info.name + "-" + task_info.extractor
    if (_uuid := DataPreprocessingService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        DataPreprocessingService.unstructured_processing, task_info.extractor,
        task_info.path, task_info.name, task_info.description, key, _uuid)
    return Responses.created(_uuid)


@router.post('/data_preprocessing/file')
async def dp_unstructured_local_source(
    bg_task: BackgroundTasks,
    file: UploadFile = File(...),
    params: UnstructuredLocalSource = Form(...)
):
    file_contents = await file.read()
    # Create a temporary file to save the content
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_contents)
        temp_file_path = temp_file.name

    key = params.name + "-" + params.extractor
    if (_uuid := DataPreprocessingService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        DataPreprocessingService.unstructured_processing, params.extractor,
        temp_file_path, params.name, params.description, key, _uuid, True)
    return Responses.created(_uuid)


@router.get("/data_preprocessing/get_status/{id}")
def get_status(
    id: str = Path(...)
):
    output = DataPreprocessingService.get_status(id)
    return JSONResponse(output)
