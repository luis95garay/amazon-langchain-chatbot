import uuid
from tempfile import NamedTemporaryFile
import datetime

from fastapi import BackgroundTasks, File, Form, UploadFile, Security
from fastapi.routing import APIRouter

from api.responses.response import Responses
from api.v2.services.data_preprocessing import (
    DataPreprocessingService
)
from api.v2.services.vectorstore_processing import (
    VectorstoreService
)
from api.schemas import (
    OnlineSourceQuestions, LocalSourceQuestions, OnlineSourceVS, LocalSourceVS
)
from api.authentication.auth import get_api_key


router = APIRouter(tags=['vectorstore_preprocessing'])


@router.post('/v2/vectorstore_preprocessing/online')
async def dp_online_source_v2(
    bg_task: BackgroundTasks,
    task_info: OnlineSourceVS,
    api_key: str = Security(get_api_key)
):
    """
    Endpoint to process unstructured text data from online source.
    This includes text extraction and question generations

    Args:
        bg_task (BackgroundTasks): A background task manager.
        task_info (OnlineSourceVS): Parameters for data processing.

    Returns:
        dict: A response dictionary indicating the acceptance of the job
    """
    # Get the current time
    current_time = datetime.datetime.now()

    # Convert the current time to a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    key = current_time_str + "-" + task_info.extractor
    if (_uuid := VectorstoreService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        VectorstoreService.online_processing,
        task_info.extractor, task_info.path, task_info.name,
        task_info.mode, key, _uuid
    )
    return Responses.created(_uuid)


@router.post('/v2/vectorstore_preprocessing/file')
async def dp_local_source_v2(
    bg_task: BackgroundTasks,
    file: UploadFile = File(...),
    params: LocalSourceVS = Form(...),
    api_key: str = Security(get_api_key)
):
    """
    Endpoint to process unstructured text data from upload file.
    This includes text extraction and question generations

    Args:
        bg_task (BackgroundTasks): A background task manager.
        file (UploadFile): file to process
        params (LocalSourceVS): Parameters for data processing.

    Returns:
        dict: A response dictionary indicating the acceptance of the job
    """
    file_contents = await file.read()
    # Create a temporary file to save the content
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_contents)
        temp_file_path = temp_file.name

    current_time = datetime.datetime.now()

    # Convert the current time to a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    key = current_time_str + "-" + params.extractor
    if (_uuid := VectorstoreService.is_processing(key)):
        return Responses.accepted(_uuid)
    _uuid = str(uuid.uuid4())
    bg_task.add_task(
        VectorstoreService.file_processing,
        params.extractor, temp_file_path, params.name,
        key, _uuid
    )
    return Responses.created(_uuid)
