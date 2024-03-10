# NoONE Langchain Chatbot 🦜️🔗

NoONE Chatbot is a chatbot prototype designed for question-answering with custom information. It works as an API service for creating custom vector stores and answering questions. The architecture follows a microservices design.

## Features ✅

### 1. Chatbot Service

- **Python-based API**: Provides a Python-based API for virtual assistant question-answering using FastAPI.
- **Question Answering (POST Endpoint)**: Utilizes a chain for question and answer
- **Vectorstore creation (GET Endpoint)**: Update and creation of the vectorstore

### 2. Redis

- **In-memory data store**: For vectorstore and mamory data store

### 3. Frontend

- **Chatbot**: example of Chatbot Service Streaming Response usage with streamlit

## Question Answering examples

1. What is SageMaker?

![Question 1](frontend/public/question1.png)

2. What are all AWS regions where AWS SageMaker is available?

![Question 2](frontend/public/question2.png)

3. How to check if an endpoint is KMS encrypted?

![Question 3](frontend/public/question3.png)

4. What are SageMaker Geospatial capabilities?

![Question 4](frontend/public/question4.png)

## How to update the vectorstore

In this case, we must upload all the updated .md files
![Alt text](frontend/public/updatedoc.png)

## Running the Containers locally ✅

To run the chatbot, follow these steps:

1. Obtain an API key from OpenAI "OPENAI_API_KEY" and save it in a `credentials.env` file.
2. Run the following Docker Compose command, specifying the environment file: `docker-compose --env-file credentials.env up`
3. Access the chatbot interface by opening [localhost:8501](http://localhost:8501) in your web browser.
