from typing import Optional
from src.api.exceptions.pre_processing import (
    NotProcessingException, StillProcessingException
    )
from src.data_processing.data_processing_pipeline import (
    VectorstoreProcessingPipeline
    )


PROCESSING = {}
RESULT: dict[str, str] = {}


class VectorstoreProcessingService:
    @staticmethod
    def process_vectorstore(
        name: str,
        method: str,
        key: tuple,
        uuid: str
    ):
        PROCESSING[key] = uuid
        pipe = VectorstoreProcessingPipeline()
        if method == "add":
            pipe.create(name)
            pipe.add(name)
        elif method == "remove":
            pipe.remove(name)

        RESULT[uuid] = "Finished"

    @staticmethod
    def is_processing(key: tuple) -> Optional[str]:
        return PROCESSING.get(key)

    @staticmethod
    def get_status(pid: str):

        if pid not in PROCESSING.values():
            raise NotProcessingException()

        if pid in RESULT:
            status = RESULT[pid]
            return {"task_id": pid, "status": status}
        else:
            raise StillProcessingException()
