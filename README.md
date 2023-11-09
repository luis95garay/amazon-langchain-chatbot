# No One Langchain Chatbot 🦜️🔗

No One Chatbot is a chatbot prototype designed for question-answering with custom information. It works as an API service for creating custom vector stores and answering questions. The architecture follows a microservices design.

## Features ✅

### 1. Chatbot Service

- **Python-based API**: Provides a Python-based API for virtual assistant question-answering using FastAPI.
- **Question Answering (POST Endpoint)**: Utilizes a chain for question and answer.
- **Streaming Response Question Answering (POST Endpoint)**: Uses a chain for streaming answers.
- **RetrievalQAWithSourcesChain**: Currently, it utilizes RetrievalQAWithSourcesChain without memory as the QA chain. This is valuable when users need links to seek more information. There's ongoing exploration with ConversationalRetrievalChain, QARetrievalChain agents, and memory usage.

### 2. Data Processing Service

- **Python-based API**: Offers an API for data processing and the generation of vector stores using FastAPI.
- **Vector Store Creation**: Supports the creation of vector stores from various sources, including:
  - **Online (POST Endpoint)**: Web sources
  - **Unstructured Files (POST Endpoint)**: PDFs, DOCX files, and plain text.
  - **Structured Files (POST Endpoint)**: xlsx and csv. This is primarily for text-based question-answering, not statistical analysis.
- **Consolidation of Vector Stores (POST Endpoint)**: Supports the consolidation of vector stores.
- **Status of the source processing (GET Endpoint)**: for asking the status of the process if necesary

### 3. Redis

- **In-memory data store**: For handling processing keys

### 4. Frontend

- **Chatbot**: example of Chatbot Service Streaming Response usage.

## Running the Containers ✅

To run the chatbot, follow these steps:

1. Obtain an API key from OpenAI "OPENAI_API_KEY" and save it in a `credentials.env` file.
2. Run the following Docker Compose command, specifying the environment file: `docker-compose --env-file credentials.env up`
3. Access the chatbot interface by opening [localhost:3000](http://localhost:3000) in your web browser.

## Question Answering examples

1. What is SageMaker?

![Question 1](frontend/public/img/question1.png)

2. What are all AWS regions where AWS SageMaker is available?

![Question 2](frontend/public/img/question2.png)

3. How to check if an endpoint is KMS encrypted?

![Question 3](frontend/public/img/question3.png)

4. What are SageMaker Geospatial capabilities?

![Question 4](frontend/public/img/question4.png)

## How to update the vectorstore

1. Run the request `/text_extraction/folder`

![Alt text](frontend/public/img/refresh.png)

### Sources of Inspiration

- [ChatGPT AI Frontend Open Source Template](https://github.com/horizon-ui/chatgpt-ai-template)
- [LangChain with Websocket Template](https://github.com/pors/langchain-chat-websockets)
