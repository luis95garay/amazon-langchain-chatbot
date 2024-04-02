import os
import requests
import boto3
from pathlib import Path


def parse_response(response:dict):
    print("Raw Response: ", response)
    text = response["data"]
    text = text.replace("\n", "").replace("```", "").replace("json","")
    return text

def get_response(body: any, user_id: any):
    url = "http://" + os.getenv("CHATBOT_HOST") + ":" + os.getenv("CHATBOT_PORT") + "/chat"
    headers = {"Content-type": "application/json"}
    response = requests.request("POST", url, headers=headers, params={'input': body, 'user_id': user_id})
    if response.status_code == 200:
        response_data = response.json()
        print("Response data:", response_data)
        return parse_response(response=response_data)
        
    else:
        print("Request failed:", response.status_code)
        return None

def update_vectorstore():
    url = "http://" + os.getenv("CHATBOT_HOST") + ":" + os.getenv("CHATBOT_PORT") + "/create_vectorstore"
    headers = {"Content-type": "application/json"}
    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        return {'data': 'Updated ok'}
        
    else:
        print("Request failed:", response.status_code)
        return None


def load_files_to_s3(uploaded_files):

    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    # Clean folder
    response = s3.list_objects_v2(Bucket=os.getenv("BUCKET_NAME"), Prefix="chatbot_data") 

    if 'Contents' in response:
        for obj in response['Contents']:
            s3.delete_object(Bucket=os.getenv("BUCKET_NAME"), Key=obj['Key'])

    # Upload files
    for file in uploaded_files:
        local_file_path = f"{file.name}"
        with open(local_file_path, "wb") as f:
            f.write(file.getvalue())

        file = Path(local_file_path)
        # Upload the file to S3
        s3.upload_file(file, os.getenv("BUCKET_NAME"), "chatbot_data/" + str(file.name))

        os.remove(str(file.name))
