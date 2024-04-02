from pathlib import Path
import os

from dotenv import load_dotenv
import boto3
import redis

from src.exceptions.pre_processing import NotFoundException


redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0)


def load_credentials():
    file_path = Path(__file__).resolve()

    # Construct the path to the .env file in the grandparent folder
    env_file_path = file_path.parent.parent / "credentials.env"
    load_dotenv(env_file_path)


def load_file_to_redis(s3_file_path: str, file_hash: str):
    """
    This function retrieves a vector store from a predefined file path
    and stores it in a global variable.
    """

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    try:
        file_name = Path(s3_file_path).name
        s3.download_file(
            os.getenv('BUCKET_NAME'), s3_file_path, str(file_name)
        )
    except Exception:
        raise NotFoundException(
                f"There is no file with name {s3_file_path}"
            )

    with open(file_name, 'rb') as file:
        file_object = file.read()

    redis_client.set(file_hash, file_object)

    os.remove(file_name)


def format_conversation(conversation):
    formatted_conv = []
    for conv in conversation:
        if conv["Agent"] == "Human":
            formatted_doc = f"- Human: '{conv['text']}'"
        elif conv["Agent"] == "Assistant":
            formatted_doc = f"- AI assistant: '{conv['text']}'"
        formatted_conv.append(formatted_doc)
    return '\n'.join(formatted_conv)


def format_docs(docs):
    formatted_docs = []
    for doc in docs:
        formatted_doc = f"'{doc.page_content}'"
        source = doc.metadata.get('source', None)
        if source:
            formatted_doc += f"\n fuente: '{source}'"
        formatted_docs.append(formatted_doc)
    return '\n\n'.join(formatted_docs)


def load_vectorstore_to_s3(local_file_path):

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )


    file = Path(local_file_path)
    # Upload the file to S3
    s3.upload_file(file, os.getenv("BUCKET_NAME"), str(file.name))

def save_files_locally():

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    local_path = Path(__file__).parent
    local_path = local_path / 'chatbot_data'
    if not os.path.exists(str(local_path)):
        os.mkdir(str(local_path))

    response = s3.list_objects_v2(Bucket=os.getenv("BUCKET_NAME"), Prefix="chatbot_data") 

    if 'Contents' in response:
        for obj in response['Contents']:
            current_path = local_path / obj['Key'].split('/')[-1]
            s3.download_file(
                os.getenv('BUCKET_NAME'), obj['Key'], str(current_path)
            )
    
    
