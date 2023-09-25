import uuid
from tempfile import NamedTemporaryFile
import datetime

from fastapi import BackgroundTasks, File, Form, Path, UploadFile
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from data_processing_api.responses.response import Responses
from data_processing_api.services.text_extraction import TextExtractionService
from data_processing_api.schemas import (
    OnlineSourceText, LocalSourceText, FolderSource
)
from data_processing_api.text_extractors.utils import search_folder


router = APIRouter(tags=['text_extractions'])


@router.post('/text_extractions/online')
async def unstructured_online_source(
    bg_task: BackgroundTasks,
    task_info: OnlineSourceText
):
    # Get the current time
    current_time = datetime.datetime.now()

    # Convert the current time to a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    key = current_time_str + "-" + task_info.extractor
    if (_uuid := TextExtractionService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        TextExtractionService.unstructured_processing, task_info.extractor,
        task_info.path, key, _uuid)
    return Responses.created(_uuid)


@router.post('/text_extractions/file')
async def unstructured_file_source(
    bg_task: BackgroundTasks,
    file: UploadFile = File(...),
    params: LocalSourceText = Form(...)
):
    file_contents = await file.read()
    # Create a temporary file to save the content
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_contents)
        temp_file_path = temp_file.name

    # Get the current time
    current_time = datetime.datetime.now()

    # Convert the current time to a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    key = current_time_str + "-" + params.extractor
    if (_uuid := TextExtractionService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        TextExtractionService.unstructured_processing, params.extractor,
        temp_file_path, key, _uuid, True)
    return Responses.created(_uuid)


@router.post('/text_extractions/folder')
async def unstructured_folder_source(
    bg_task: BackgroundTasks,
    task_info: FolderSource
):
    # Get the current time
    current_time = datetime.datetime.now()

    folder = search_folder(task_info.path)
    if not folder:
        return Responses.not_found("Folder not found")

    # Convert the current time to a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    key = current_time_str + "-" + task_info.extractor
    if (_uuid := TextExtractionService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        TextExtractionService.unstructured_processing, task_info.extractor,
        folder, key, _uuid, False, True)
    return Responses.created(_uuid)


@router.get("/text_extractions/get_status/{id}")
def get_status(
    id: str = Path(...)
):
    output = TextExtractionService.get_status(id)
    return JSONResponse(output)
