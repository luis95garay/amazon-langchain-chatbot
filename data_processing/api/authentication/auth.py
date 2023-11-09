import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader


file_path = Path(__file__).resolve()

# Construct the path to the .env file in the grandparent folder
env_file_path = file_path.parent.parent.parent / "credentials.env"
load_dotenv(env_file_path)

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def get_api_key(
        api_key_header: str = Security(api_key_header),
) -> str:
    if api_key_header == os.getenv("DATA_PROCESSING_API_KEY"):
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
