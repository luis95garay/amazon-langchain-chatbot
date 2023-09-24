from typing import Optional
from data_processing_api.exceptions.pre_processing import (
    NotProcessingException, StillProcessingException
    )
from data_processing_api.data_processing.data_processing_pipeline import (
    UnstructuredProcessingPipeline
)
import os
from data_processing_api.schemas import LimitedDict


PROCESSING = LimitedDict(3)
RESULT = LimitedDict(3)


class DataPreprocessingService:
    @staticmethod
    def unstructured_processing(
        extractor: str,
        path: str,
        name: str,
        description: str,
        key: tuple,
        uuid: str,
        is_tempfile: bool = False
    ):
        PROCESSING[key] = uuid
        pipe = UnstructuredProcessingPipeline(extractor)
        RESULT[uuid] = pipe(path=path, name=name, description=description)
        if is_tempfile:
            os.remove(path)
            print("removed temp file")

    # @staticmethod
    # def structured_processing(
    #     extractor: str,
    #     path: str,
    #     name: str,
    #     description: str,
    #     key: tuple,
    #     uuid: str,
    #     is_tempfile: bool = False
    # ):
    #     PROCESSING[key] = uuid
    #     pipe = StructuredProcessingPipeline(extractor)
    #     pipe(path=path, name=name, description=description)
    #     RESULT[uuid] = "Finished"
    #     if is_tempfile:
    #         os.remove(path)

    @staticmethod
    def is_processing(key: tuple) -> Optional[str]:
        return PROCESSING.get(key)

    @staticmethod
    def get_status(pid: str):

        if pid not in PROCESSING.values():
            raise NotProcessingException()

        if pid in RESULT:
            result = RESULT[pid]
            return {"status": "success", "error": None, "data": result}
        else:
            raise StillProcessingException()
