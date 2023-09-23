"""Main entrypoint for the app."""
import logging
from fastapi import WebSocket, WebSocketDisconnect, Depends
from langchain.vectorstores import VectorStore

from src.api.callback import (
    StreamingLLMCallbackHandler, QuestionGenCallbackHandler
    )
from src.api.query_data import get_chainM, get_chainM1
from src.api.schemas import ChatResponse
from fastapi.routing import APIRouter
from src.api.utils import get_file_content


router = APIRouter(tags=['virtual_assistant'])


# @router.websocket("/chat")
# async def websocket_endpoint(
#         websocket: WebSocket,
#         vectorstore: VectorStore = Depends(get_file_content)
#         ):
#     await websocket.accept()
#     stream_handler = StreamingLLMCallbackHandler(websocket)
#     chat_history = []
#     qa_chain = get_chain_RetrievalQA(vectorstore, stream_handler)
#     # Use the below line instead of the above line to enable tracing
#     # Ensure `langchain-server` is running
#     # qa_chain = get_chain(
#     # vectorstore, question_handler, stream_handler, tracing=True
#     # )

#     while True:
#         try:
#             # Receive and send back the client message
#             question = await websocket.receive_text()
#             resp = ChatResponse(
#                       sender="you", message=question, type="stream"
#                     )

#             await websocket.send_json(resp.dict())

#             # Construct a response
#             start_resp = ChatResponse(sender="bot", message="", type="start")
#             await websocket.send_json(start_resp.dict())

#             result = await qa_chain.acall(
#                 {"query": question, "chat_history": chat_history}
#             )

#             chat_history.append((question, result["result"]))

#             end_resp = ChatResponse(sender="bot", message="", type="end")
#             await websocket.send_json(end_resp.dict())
#         except WebSocketDisconnect:
#             logging.info("websocket disconnect")
#             break
#         except Exception as e:
#             logging.error(e)
#             resp = ChatResponse(
#                 sender="bot",
#                 message="Sorry, something went wrong. Try again.",
#                 type="error",
#             )
#             await websocket.send_json(resp.dict())

# @router.websocket("/chat")
# async def websocket_endpoint(
#         websocket: WebSocket,
#         vectorstore: VectorStore = Depends(get_file_content)
#         ):
#     await websocket.accept()
#     question_handler = QuestionGenCallbackHandler(websocket)
#     stream_handler = StreamingLLMCallbackHandler(websocket)
#     chat_history = []
#     qa_chain = get_chain(vectorstore, question_handler, stream_handler)
#     # Use the below line instead of the above line to enable tracing
#     # Ensure `langchain-server` is running
#     # qa_chain = get_chain(
#     # vectorstore, question_handler, stream_handler, tracing=True
#     # )

#     while True:
#         try:
#             # Receive and send back the client message
#             question = await websocket.receive_text()
#             resp = ChatResponse(
#                       sender="you", message=question, type="stream"
#                       )
#             await websocket.send_json(resp.dict())

#             # Construct a response
#             start_resp = ChatResponse(sender="bot", message="", type="start")
#             await websocket.send_json(start_resp.dict())

#             result = await qa_chain.acall(
#                 {"question": question, "chat_history": chat_history}
#             )

#             chat_history.append((question, result["answer"]))

#             end_resp = ChatResponse(sender="bot", message="", type="end")
#             await websocket.send_json(end_resp.dict())
#         except WebSocketDisconnect:
#             logging.info("websocket disconnect")
#             break
#         except Exception as e:
#             logging.error(e)
#             resp = ChatResponse(
#                 sender="bot",
#                 message="Sorry, something went wrong. Try again.",
#                 type="error",
#             )
#             await websocket.send_json(resp.dict())

@router.websocket("/chat")
async def websocket_endpoint(
        websocket: WebSocket,
        vectorstore: VectorStore = Depends(get_file_content)
        ):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    qa_chain = get_chainM(vectorstore, question_handler, stream_handler)
    # Use the below line instead of the above line to enable tracing
    # Ensure `langchain-server` is running
    # qa_chain = get_chain(
    # vectorstore, question_handler, stream_handler, tracing=True
    # )

    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()
            resp = ChatResponse(
                      sender="you", message=question, type="stream"
                      )
            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            await qa_chain.acall(
                {"question": question}
            )

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            await websocket.send_json(resp.dict())

from pydantic import BaseModel
from fastapi import Form
from src.api.responses.response import Responses
from pathlib import Path
from dotenv import load_dotenv
import pickle

class Input(BaseModel):
    input: str

file_path = Path(__file__).resolve()

# Construct the path to the .env file in the grandparent folder
env_file_path = file_path.parent.parent.parent / "credentials.env"
vectorstores_path = file_path.parent.parent \
        .parent.parent / "data" / "final_vectorstores" / "vectorstore.pkl"
# Load environment variables from the .env file
load_dotenv(env_file_path)
with open(vectorstores_path, "rb") as f:
    global vectorstore
    vectorstore = pickle.load(f)
qa1 = get_chainM1(vectorstore)

@router.post("/request/chat")
async def ask_question(
    params: Input,
):
    data = qa1.run({"question": params.input})
    return data
