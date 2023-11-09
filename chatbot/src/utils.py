from pathlib import Path
import os
from dotenv import load_dotenv
import boto3

from constants import (
    LOCAL_VECTORSTORE_PATH, BUCKET_NAME,
    BUCKET_VECTORSTORE_PATH,
)


def load_credentials():
    file_path = Path(__file__).resolve()

    # Construct the path to the .env file in the grandparent folder
    env_file_path = file_path.parent.parent.parent / "credentials.env"
    load_dotenv(env_file_path)


def load_file_content(file_name: str = "vectorstore3000.pkl"):
    """
    This function retrieves a vector store from a predefined file path
    and stores it in a global variable.
    """
    # load_credentials()

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    s3.download_file(
        BUCKET_NAME,
        BUCKET_VECTORSTORE_PATH + file_name,
        str(LOCAL_VECTORSTORE_PATH)
    )
