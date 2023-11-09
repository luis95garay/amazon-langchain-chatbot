from typing import Optional
from datetime import date
import pickle

import redis

from api.v2.data_processing \
    .data_processing_pipeline import (
        UnstructuredProcessingPipeline
        )
import os


r = redis.Redis(host='redis', port=6382, db=0)


class DataPreprocessingService:
    @staticmethod
    def online_processing(
        extractor: str,
        path: str,
        description: str,
        mode: str,
        from_date: date,
        key: tuple,
        uuid: str
    ):
        r.hset('PROCESSING', key, uuid)
        try:
            pipe = UnstructuredProcessingPipeline(extractor)
            data = pipe(
                path=path, description=description,
                mode=mode, from_date=from_date
            )
            r.hset('RESULT', uuid, pickle.dumps(
                    [(("pregunta",) + x + (path,)) for x in data]
                )
            )
        except Exception as e:
            r.hset('RESULT', uuid, pickle.dumps(e))

    @staticmethod
    def file_processing(
        extractor: str,
        path: str,
        name: str,
        description: str,
        key: tuple,
        uuid: str
    ):
        r.hset('PROCESSING', key, uuid)
        try:
            pipe = UnstructuredProcessingPipeline(extractor)
            data = pipe(
                        path=path, description=description
                    )
            r.hset('RESULT', uuid, pickle.dumps(
                    [(("pregunta",) + x + (name + "." + extractor,))
                     for x in data]
                )
            )

        except Exception as e:
            r.hset('RESULT', uuid, pickle.dumps(e))

        os.remove(path)
        print("removed temp file")

    @staticmethod
    def is_processing(key: tuple) -> Optional[str]:
        """
        Check if a processing task with the specified key is in progress.
        """
        value = r.hget('PROCESSING', key)
        if value:
            return r.hget('PROCESSING', key).decode('utf-8')
        return value
