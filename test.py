import json

import requests

# url = "http://localhost:9001/stream_chat"

message = "What is AWS sagemaker?"
# data = {"input": message}

# headers = {"Content-type": "application/json"}

# with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
#     for chunk in r.iter_content(1024):
#         print(chunk)

url = "http://localhost:9001/chat"
# payload = json.dumps({"input": message})
# headers = {"Content-type": "application/json"}

# payload = {"input": message}
# headers = {"Content-type": "application/json"}

# response = requests.request("POST", url, headers=headers, params={'input': message})
# if response.status_code == 200:
#     response_data = response.json()
#     print("Response data:", response_data)
# else:
#     None
# response = requests.request("POST", url, headers=headers, data=payload)
# details = json.loads(response.text)
# print(details)
# print(details['data'])


def parse_response(response:dict):
    print("Raw Response: ", response)
    text = response["data"]
    text = text.replace("\n", "").replace("```", "").replace("json","")
    # text = eval(text)
    # print("data ", text["assistant"])
    return text

def get_response(url:str, body:any):
    headers = {"Content-type": "application/json"}
    response = requests.request("POST", url, headers=headers, params={'input': message})
    if response.status_code == 200:
        response_data = response.json()
        print("Response data:", response_data)
        return parse_response(response=response_data)
        
    else:
        print("Request failed:", response.status_code)
        return None
    
get_response(url, message)