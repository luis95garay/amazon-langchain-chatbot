from typing import Optional
from data_processing_api.exceptions.pre_processing import (
    NotProcessingException, StillProcessingException
    )
from data_processing_api.text_extractors.pipelines.loaders_pipeline import (
    TextExtractorPipeline
)
import os
from data_processing_api.schemas import LimitedDict


PROCESSING = LimitedDict(3)
RESULT = LimitedDict(3)


class TextExtractionService:
    @staticmethod
    def unstructured_processing(
        extractor: str,
        path: str,
        name: str,
        key: tuple,
        uuid: str,
        is_tempfile: bool = False,
        is_folder: bool = False
    ):
        PROCESSING[key] = uuid
        loader = TextExtractorPipeline(extractor)
        data = loader.get_documents(path, is_folder=is_folder)
        loader.create_vectorstore(data, name)
        RESULT[uuid] = "Completed"
        if is_tempfile:
            os.remove(path)
            print("removed temp file")

    @staticmethod
    def is_processing(key: tuple) -> Optional[str]:
        """
        Check if a processing task with the specified key is in progress.
        """
        return PROCESSING.get(key)

    @staticmethod
    def get_status(pid: str):
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
        if pid not in PROCESSING.values():
            raise NotProcessingException()

        if pid in RESULT:
            result = RESULT[pid]
            return {"status": "success", "error": None, "data": result}
        else:
            raise StillProcessingException()
