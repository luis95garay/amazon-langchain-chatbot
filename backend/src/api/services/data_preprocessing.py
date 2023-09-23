from typing import Optional
from src.api.exceptions.pre_processing import (
    NotProcessingException, StillProcessingException
    )
from src.data_processing.data_processing_pipeline import (
    UnstructuredProcessingPipeline, StructuredProcessingPipeline
)
import os
from pathlib import Path
import pandas as pd

PROCESSING = {}
RESULT: dict[str, str] = {}


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
        # time.sleep(30)
        pipe = UnstructuredProcessingPipeline(extractor)
        pipe(path=path, name=name, description=description)
        RESULT[uuid] = "Finished"
        if is_tempfile:
            os.remove(path)
            print("removed temp file")

    @staticmethod
    def structured_processing(
        extractor: str,
        path: str,
        name: str,
        description: str,
        key: tuple,
        uuid: str,
        is_tempfile: bool = False
    ):
        PROCESSING[key] = uuid
        pipe = StructuredProcessingPipeline(extractor)
        pipe(path=path, name=name, description=description)
        RESULT[uuid] = "Finished"
        if is_tempfile:
            os.remove(path)

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

    @staticmethod
    def get_questions(name: str):
        data_path = Path(__file__).parent.parent.parent.parent \
            / "data" / "questions"

        for file in data_path.iterdir():
            if file.stem == name:
                df_questions = pd.read_csv(file)
                return df_questions.to_dict()

        raise NotProcessingException()
