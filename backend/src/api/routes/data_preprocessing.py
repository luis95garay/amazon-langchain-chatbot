import uuid

from fastapi import BackgroundTasks, File, Form, Path, UploadFile
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from src.api.responses.response import Responses
from src.api.services.data_preprocessing import DataPreprocessingService
from src.api.schemas import OnlineSource, LocalSource
from tempfile import NamedTemporaryFile


router = APIRouter(tags=['data_preprocessing'])


@router.post('/unstructured_online_source')
async def unstructured_online_source(
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


@router.post('/unstructured_local_source')
async def unstructured_local_source(
    bg_task: BackgroundTasks,
    file: UploadFile = File(...),
    params: LocalSource = Form(...)
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


@router.post('/structured_local_source')
async def structured_local_source(
    bg_task: BackgroundTasks,
    file: UploadFile = File(...),
    params: LocalSource = Form(...)
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
        DataPreprocessingService.structured_processing, params.extractor,
        temp_file_path, params.name, params.description, key, _uuid, True)
    return Responses.created(_uuid)


@router.get("/dp/get_status/{id}")
def get_status(id: str = Path(...)):
    output = DataPreprocessingService.get_status(id)
    return JSONResponse(output)


@router.get("/get_questions_answers/{name}")
def get_questions_answers(name: str = Path(...)):
    output = DataPreprocessingService.get_questions(name)
    return JSONResponse(output)
