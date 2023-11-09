from pathlib import Path
import json
import requests
import os

from fastapi.testclient import TestClient
from dotenv import load_dotenv

from main import app


client = TestClient(app)
# data_processing_url = "http://52.5.31.54:9003"
data_processing_url = "http://localhost:9003"
load_dotenv("credentials.env")
data_processing_key = os.getenv("DATA_PROCESSING_API_KEY")


def test_web_extraction_ok():
    url = f"{data_processing_url}/text_extractions/online"

    payload = json.dumps({
        "extractor": "web",
        "path": "https://vivo.life/"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': data_processing_key
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    details = json.loads(response.text)

    assert response.status_code == 201
    assert details['status'] == "success"
    assert details['error'] is None


def test_web_extraction_invalidExt():
    url = f"{data_processing_url}/text_extractions/online"

    payload = json.dumps({
        "extractor": "webdf",
        "path": "https://vivo.life/"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': data_processing_key
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    details = json.loads(response.text)

    assert response.status_code == 422
    assert details['detail'][0]['msg'] == \
        "value is not a valid enumeration member; permitted: 'web', 'sharepoint'"
    assert details['detail'][0]['type'] == "type_error.enum"


def test_web_extraction_invalidUrl():
    url = f"{data_processing_url}/text_extractions/online"

    payload = json.dumps({
        "extractor": "web",
        "path": "vivo.life/"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': data_processing_key
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    details = json.loads(response.text)

    assert response.status_code == 422
    assert details['detail'][0]['msg'] == "invalid or missing URL scheme"
    assert details['detail'][0]['type'] == "value_error.url.scheme"


def test_file_extraction():
    url = f"{data_processing_url}/text_extractions/file"
    path = Path(__file__).parent.parent.parent.parent.parent / "bluemeds.docx"

    payload = {"params": json.dumps({"extractor": "docx"})}

    files = {
        'file': (
            'bluemeds.docx',
            open(str(path), 'rb'),
            'application/vnd.openxmlformats-officedocument.\
                wordprocessingml.document'
        )
    }
    headers = {
        'Accept': 'application/json',
        'x-api-key': data_processing_key
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files
    )
    details = json.loads(response.text)

    assert response.status_code == 201
    assert details['status'] == "success"
    assert details['error'] is None


def test_file_extraction_invalidExt():
    url = f"{data_processing_url}/text_extractions/file"
    path = Path(__file__).parent.parent.parent.parent.parent / "bluemeds.docx"

    payload = {"params": json.dumps({"extractor": "docxsdf"})}

    files = {
        'file': (
            'bluemeds.docx',
            open(str(path), 'rb'),
            'application/vnd.openxmlformats-officedocument.\
                wordprocessingml.document'
        )
    }
    headers = {
        'Accept': 'application/json',
        'x-api-key': data_processing_key
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files
    )
    details = json.loads(response.text)

    assert response.status_code == 422
    assert details['detail'][0]['msg'] == \
        "value is not a valid enumeration member; permitted: 'docx', 'pdf', 'txt', 'csv', 'xlsx'"
    assert details['detail'][0]['type'] == "type_error.enum"


def test_web_extraction_status_NotFound():
    url = f"{data_processing_url}/status/get_status/5432332"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'x-api-key': data_processing_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    details = json.loads(response.text)

    assert response.status_code == 404
    assert details['status'] == "failure"
    assert details['error'] == "Not found"
    assert details['data'] is None
