from typing import Optional
from datetime import date
import pickle
import json
import requests
import redis

from api.text_extractors \
    .pipelines.loaders_pipeline import (
        TextExtractorPipeline
        )
from api.v2.vectorstore_processing.vectorstores_processing_pipeline import VectorstoreProcessingPipeline
import os


r = redis.Redis(host='redis', port=6382, db=0)

def update_request(object_key):
    url = f"http://host.docker.internal:9001/update"

    payload = json.dumps({
        "file_name": object_key,
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        # 'x-api-key': data_processing_key
    }

    requests.request("POST", url, headers=headers, data=payload)


class VectorstoreService:
    @staticmethod
    def online_processing(
        extractor: str,
        path: str,
        name: str,
        mode: str,
        key: tuple,
        uuid: str
    ):
        r.hset('PROCESSING', key, uuid)
        try:
            loader = TextExtractorPipeline(extractor)
            vs_procesor = VectorstoreProcessingPipeline()
            data = loader(path, mode=mode)
            data = [("chunk", f"Chunk{idx}", val.page_content, path)
                   for idx, val in enumerate(data)]
            vs_procesor.create_from_list(name, data, key)
            r.hset('RESULT', uuid, "completed")
        except Exception as e:
            r.hset('RESULT', uuid, pickle.dumps(e))

    @staticmethod
    def file_processing(
        extractor: str,
        path: str,
        name: str,
        key: tuple,
        uuid: str
    ):
        r.hset('PROCESSING', key, uuid)
        # try:
        loader = TextExtractorPipeline(extractor)
        vs_procesor = VectorstoreProcessingPipeline()
        data = loader(path)
        data = [("chunk", f"Chunk{idx}", val.page_content, path)
                for idx, val in enumerate(data)]
        object_key = vs_procesor.create_from_list(name, data, key)
        update_request(object_key)

        r.hset('RESULT', uuid, "completed")
        # except Exception as e:
        #     r.hset('RESULT', uuid, pickle.dumps(e))

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
