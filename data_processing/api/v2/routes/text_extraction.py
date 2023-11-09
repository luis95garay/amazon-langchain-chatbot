import uuid
from tempfile import NamedTemporaryFile
import datetime

from fastapi import BackgroundTasks, File, Form, UploadFile, Security
from fastapi.routing import APIRouter

from api.responses.response import Responses
from api.v2.services.text_extraction import TextExtractionService
from api.schemas import OnlineSourceText, LocalSourceTextv2
from api.authentication.auth import get_api_key


router = APIRouter(tags=['text_extractions'])


@router.post('/v2/text_extractions/online')
async def online_source_v2(
    bg_task: BackgroundTasks,
    task_info: OnlineSourceText,
    api_key: str = Security(get_api_key)
):
    """
    Endpoint to process unstructured text data from online source.

    Args:
        bg_task (BackgroundTasks): A background task manager.
        task_info (OnlineSourceText): Parameters for text extraction.

    Returns:
        dict: A response dictionary indicating the acceptance of the job
    """
    # Get the current time
    current_time = datetime.datetime.now()

    # Convert the current time to a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    key = current_time_str + "-" + task_info.extractor
    if (_uuid := TextExtractionService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        TextExtractionService.online_processing,
        task_info.extractor, task_info.path, task_info.mode,
        task_info.from_date, key, _uuid
    )
    return Responses.created(_uuid)


@router.post('/v2/text_extractions/file')
async def file_source_v2(
    bg_task: BackgroundTasks,
    file: UploadFile = File(...),
    params: LocalSourceTextv2 = Form(...),
    api_key: str = Security(get_api_key)
):
    """
    Endpoint to process unstructured text data from an uploaded file.

    Args:
        bg_task (BackgroundTasks): A background task manager.
        file (UploadFile): The uploaded file containing unstructured
            text data.
        params (LocalSourceText): Parameters for text extraction.

    Returns:
        dict: A response dictionary indicating the status of the
        text extraction job.
    """
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
        TextExtractionService.file_processing,
        params.extractor, temp_file_path, params.name, key, _uuid
    )
    return Responses.created(_uuid)
