"""Schemas for the chat app."""
from enum import Enum
from collections import OrderedDict
from typing import List

import json
from pydantic import BaseModel


class FileExtractorEnum(str, Enum):
    docx = "docx"
    pdf = "pdf"
    txt = "txt"
    md = "md"


class OnlineExtractorEnum(str, Enum):
    web = "web"


class OnlineSourceText(BaseModel):
    extractor: OnlineExtractorEnum
    path: str


class FolderSource(BaseModel):
    extractor: FileExtractorEnum
    path: str


class LocalSourceText(BaseModel):
    extractor: FileExtractorEnum

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class OnlineSource(BaseModel):
    extractor: OnlineExtractorEnum
    path: str
    name: str
    description: str


class UnstructuredLocalSource(BaseModel):
    extractor: FileExtractorEnum
    name: str
    description: str

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class Dataset(BaseModel):
    name: str
    method: str


class LimitedDict(OrderedDict):
    def __init__(self, max_size):
        super().__init__()
        self.max_size = max_size

    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            # Remove the oldest item (the first inserted item)
            self.popitem(last=False)
        super().__setitem__(key, value)
