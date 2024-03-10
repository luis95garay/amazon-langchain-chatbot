from typing import Optional
from datetime import date
import pickle

import redis

from api.text_extractors \
    .pipelines.loaders_pipeline import (
        TextExtractorPipeline
        )
import os


r = redis.Redis(host='redis', port=6382, db=0)


class TextExtractionService:
    @staticmethod
    def online_processing(
        extractor: str,
        path: str,
        mode: str,
        from_date: date,
        key: tuple,
        uuid: str
    ):
        r.hset('PROCESSING', key, uuid)
        try:
            loader = TextExtractorPipeline(extractor)
            data = loader(path, mode=mode, from_date=from_date)
            r.hset('RESULT', uuid, pickle.dumps(
                [("chunk", f"Chunk{idx}", val.page_content, path)
                 for idx, val in enumerate(data)]
                )
            )
        except Exception as e:
            r.hset('RESULT', uuid, pickle.dumps(e))

    @staticmethod
    def file_processing(
        extractor: str,
        path: str,
        name: str,
        key: tuple,
        uuid: str,
    ):
        r.hset('PROCESSING', key, uuid)
        try:
            loader = TextExtractorPipeline(extractor)
            data = loader(path)
            r.hset('RESULT', uuid, pickle.dumps(
                [("chunk", f"Chunk{idx}",
                  val.page_content, name + "." + extractor)
                 for idx, val in enumerate(data)]
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