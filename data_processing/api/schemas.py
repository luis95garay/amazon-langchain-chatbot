"""Schemas for the chat app."""
from datetime import date
import json
from enum import Enum
from collections import OrderedDict

from pydantic import BaseModel, HttpUrl
from fastapi import Query


class FileExtractorText(str, Enum):
    docx = "docx"
    pdf = "pdf"
    txt = "txt"
    csv = "csv"
    xlsx = "xlsx"


class FileExtractorQuestions(str, Enum):
    docx = "docx"
    pdf = "pdf"
    txt = "txt"


class OnlineExtractorEnum(str, Enum):
    web = "web"
    sharepoint = "sharepoint"


class ModeEnum(str, Enum):
    single = "single"
    consolidated = "consolidated"


class OnlineSourceText(BaseModel):
    extractor: OnlineExtractorEnum = OnlineExtractorEnum.web
    path: HttpUrl
    mode: ModeEnum = ModeEnum.single
    from_date: date = Query(date.today())


class OnlineSource(BaseModel):
    extractor: OnlineExtractorEnum = OnlineExtractorEnum.web
    path: HttpUrl
    description: str
    mode: ModeEnum = ModeEnum.single
    from_date: date = Query(date.today())


class LocalSourceText(BaseModel):
    extractor: FileExtractorText = FileExtractorText.docx

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class LocalSourceTextv2(BaseModel):
    extractor: FileExtractorText = FileExtractorText.docx
    name: str

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class OnlineSourceQuestions(BaseModel):
    extractor: OnlineExtractorEnum = OnlineExtractorEnum.web
    path: HttpUrl
    description: str
    mode: ModeEnum = ModeEnum.single
    from_date: date = Query(date.today())


class OnlineSourceVS(BaseModel):
    extractor: OnlineExtractorEnum = OnlineExtractorEnum.web
    path: HttpUrl
    name: str
    mode: ModeEnum = ModeEnum.single


class LocalSourceVS(BaseModel):
    extractor: FileExtractorQuestions = FileExtractorQuestions.docx
    name: str

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class LocalSourceQuestions(BaseModel):
    extractor: FileExtractorQuestions = FileExtractorQuestions.docx
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


class UnstructuredLocalSource(BaseModel):
    extractor: FileExtractorText = FileExtractorText.docx
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
