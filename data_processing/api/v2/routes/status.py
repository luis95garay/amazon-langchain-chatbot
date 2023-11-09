import pickle

from fastapi import Path, Security
from fastapi.routing import APIRouter
import redis

from api.responses.response import Responses
from api.authentication.auth import get_api_key
from api.exceptions.pre_processing import (
    NotProcessingException, StillProcessingException,
    Internal_server_errorException
    )


r = redis.Redis(host='redis', port=6382, db=0)
r.hset('PROCESSING', 'init', '')
r.hset('RESULT', 'init', '')
router = APIRouter(tags=['status'])


@router.get("/v2/status/get_status/{id}")
def get_status_v2(
    id: str = Path(...),
    api_key: str = Security(get_api_key)
):
    """
    Get the status of a processing task by its unique identifier (UUID).

    Args:
        pid (str): The unique identifier (UUID) of the processing task.

    Raises:
        NotProcessingException: If the specified task is not found in the
            processing queue.
        StillProcessingException: If the task is still in progress but the
            result is not available yet.
    """
    processing = r.hvals('PROCESSING')
    values = [val.decode('utf-8') for val in processing]

    if id not in values:
        raise NotProcessingException()

    result = r.hget('RESULT', id)

    if result:
        # result = pickle.loads(result)
        if isinstance(result, Exception):
            raise Internal_server_errorException(str(result))
        else:
            return Responses.ok(result.decode('utf-8'))

    raise StillProcessingException()
