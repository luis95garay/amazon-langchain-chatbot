from typing import Optional

import redis

from data_processing_api.exceptions.pre_processing import (
    NotProcessingException, StillProcessingException
    )
from data_processing_api.text_extractors.pipelines.loaders_pipeline import (
    TextExtractorPipeline
)
import os


r = redis.Redis(host='redis', port=6379, db=0)
r.hset('PROCESSING', mapping={"prueba": ""})
r.hset('RESULT', mapping={"prueba": ""})


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
        r.hset('PROCESSING', key, uuid)
        # PROCESSING[key] = uuid
        loader = TextExtractorPipeline(extractor)
        data = loader.get_documents(path, is_folder=is_folder)
        loader.create_vectorstore(data, name)
        r.hset('RESULT', uuid, "Completed")
        # RESULT[uuid] = "Completed"
        if is_tempfile:
            os.remove(path)
            print("removed temp file")

    @staticmethod
    def is_processing(key: tuple) -> Optional[str]:
        """
        Check if a processing task with the specified key is in progress.
        """
        # return PROCESSING.get(key)
        return r.hget('PROCESSING', key)

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
        # # if pid not in PROCESSING.values():
        #     raise NotProcessingException()

        processing = r.hgetall('PROCESSING')
        # print(processing)
        values = [val.decode('utf-8') for val in processing.values()]
        if pid not in values:
            raise NotProcessingException()

        # # if pid in RESULT:
        #     result = RESULT[pid]
        #     return {"status": "success", "error": None, "data": result}
        # else:
        #     raise StillProcessingException()
        
        result = r.hget('RESULT', pid)
        if result:
            return {"status": "success", "error": None, "data": result.decode('utf-8')}
        
        raise StillProcessingException()
