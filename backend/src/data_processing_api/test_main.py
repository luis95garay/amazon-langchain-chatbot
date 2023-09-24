from fastapi.testclient import TestClient
from .main import app
import json


client = TestClient(app)

def test_web_extraction():
    url = "http://localhost:9002/text_extractions/file"
    
    # Create a dictionary for your file(s)
    files = {'file': ('bluemeds.docx', open('C:/Users/luisg/Documents/bluemeds.docx', 'rb'))}
    
    # Define your payload as a dictionary
    payload = {'params': json.dumps({"extractor": "docx"})}
    
    headers = {
        'Accept': 'application/json'
    }
    
    # Make the POST request using the test client
    response = client.post(url, headers=headers, data=payload, files=files)
    
    assert response.status_code == 200  # Adjust the expected status code as needed
    # assert "Your expected response text" in response.text  # Add your assertions here