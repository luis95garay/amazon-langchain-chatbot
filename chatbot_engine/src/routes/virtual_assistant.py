"""Main entrypoint for the app."""
import asyncio
import logging
from typing import AsyncIterable
import json
from fastapi.encoders import jsonable_encoder
from time import time
from collections import deque
import pickle

# import pandas as pd
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
import redis

from src.callback import StreamingLLMCallbackHandler
from src.chains.assistants import (
    get_chain_v0_simple, get_chain_stream, get_chain_scratch_v1, get_chain_scratch_v2
)
from src.schemas import ChatResponse, InputRequest
from src.db.vectorstoredb import VectorstoreDB
from src.utils import format_conversation, format_docs
from constants import REDIS_HOST, REDIS_PORT


router = APIRouter(tags=['virtual_assistant'])
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
# logging.basicConfig(level=logging.WARNING)


def get_vectorstore():
    return VectorstoreDB()


class QAImplementation:
    def __init__(self, vecstore: VectorstoreDB):
        vecstore = VectorstoreDB('9195173332994997420b3f236e0da21a')
        self.ask = get_chain_v0_simple(vecstore.vectorstore)


def get_qa(vecstore: VectorstoreDB = Depends(get_vectorstore)):
    return QAImplementation(vecstore)


async def send_message(question: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    vecstore = VectorstoreDB('9195173332994997420b3f236e0da21a')
    qa = get_chain_stream(vecstore.vectorstore, callback)

    task = asyncio.create_task(
        qa.acall({"question": question})
    )

    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f"Caught exception: {e}")
    finally:
        callback.done.set()

    await task


# Simple request
@router.post("/chat")
async def ask_question(
    # params: InputRequest
    input: str,
    user_id: str
):
    """Handle a POST request to ask a question and return a response."""
    try:
        memory_chain, question_chain = get_chain_scratch_v2()
        # question = params.input
        question = input

        # Retrieve the pickled data from Redis
        memory = redis_client.get(user_id)

        # Filter memory by date
        if memory:
            # Unpickle the data
            memory = pickle.loads(memory)
            memory = \
                deque(
                    [
                        conv for conv in memory
                        if (time() - conv["datetime"]) <= 120
                    ],
                    maxlen=4
                )
            # logging.warning(len(memory))
        else:
            memory = []

        # logging.info(len(memory))
        if memory:
            new_question = memory_chain.run(
                {
                    "chat_history": format_conversation(memory),
                    "question": question
                }
            )
        else:
            new_question = question
        vecstore = VectorstoreDB('9195173332994997420b3f236e0da21a')
        docs = vecstore.vectorstore.similarity_search(
            new_question, k=4
        )
        result = question_chain.run(
            {
                "context": format_docs(docs),
                "new_question": new_question
            }
        )
        end_time = time()
        memory.append(
            {
                "Agent": "Human",
                "text": new_question,
                "datetime": end_time
            }
        )
        memory.append(
            {
                "Agent": "Assistant",
                "text": result,
                "datetime": end_time
            }
        )
        pickled_data = pickle.dumps(memory)

        # Store the pickled data in Redis
        redis_client.set(user_id, pickled_data)
    
        return {'data': result}
    
    except Exception:
        # Handle any exceptions that may occur
        error_message = "Sorry, something went wrong. Try again"
        return {'text': error_message, 'source': None}


# Stream request
@router.post("/stream_chat/")
async def stream_chat(message: InputRequest):
    generator = send_message(message.input)
    return StreamingResponse(generator, media_type="text/event-stream")


@router.websocket("/chat")
async def websocket_endpoint(
        websocket: WebSocket
        ):
    await websocket.accept()
    stream_handler = StreamingLLMCallbackHandler(websocket)
    memory_chain, question_chain = get_chain_scratch_v1(stream_handler)

    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()
            start_time = time()
            question = f'{{"message": "{question.strip()}", "user": "operador@mibluemedical.com", "name": "LuisG", "skill": "CAS", "area": "Vivolife", "hash": "9195173332994997420b3f236e0da21a"}}'
            question_dict = json.loads(question)
            question = question_dict['message']


            resp = ChatResponse(
                      sender="you", message=question, type="stream"
                      )
            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            # Retrieve the pickled data from Redis
            memory = redis_client.get(question_dict['user'])

            # Filter memory by date
            if memory:
                # Unpickle the data
                memory = pickle.loads(memory)
                memory = \
                    deque(
                        [
                            conv for conv in memory
                            if (time() - conv["datetime"]) <= 120
                        ],
                        maxlen=4
                    )
                # logging.warning(len(memory))
            else:
                memory = []

            # logging.info(len(memory))
            if memory:
                new_question = memory_chain.run(
                    {
                        "chat_history": format_conversation(memory),
                        "question": question
                    }
                )
            else:
                new_question = question
            vecstore = VectorstoreDB(question_dict['hash'])
            docs = await vecstore.vectorstore.asimilarity_search(
                new_question, k=4
            )
            result = await question_chain.acall(
                {
                    "context": format_docs(docs),
                    "new_question": new_question
                }
            )
            end_time = time()
            memory.append(
                {
                    "Agent": "Human",
                    "text": new_question,
                    "datetime": end_time
                }
            )
            memory.append(
                {
                    "Agent": "Assistant",
                    "text": result['answer'],
                    "datetime": end_time
                }
            )
            pickled_data = pickle.dumps(memory)

            # Store the pickled data in Redis
            redis_client.set(question_dict['user'], pickled_data)

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


# @router.websocket("/chat")
# async def websocket_endpoint(
#         websocket: WebSocket
#         ):
#     await websocket.accept()
#     question_handler = QuestionGenCallbackHandler(websocket)
#     stream_handler = StreamingLLMCallbackHandler(websocket)
#     servicesdb = ServicesDB()
#     vecstore = VectorstoreDB()
#     qa_chain = get_chain_v0(
#         vecstore.vectorstore, question_handler, stream_handler
#     )

#     while True:
#         try:
#             # Receive and send back the client message
#             question = await websocket.receive_text()
#             start_time = time()
#             question_dict = json.loads(question)
#             question = question_dict['message']

#             is_query, clean_question = servicesdb.run_query(question)

#             if is_query:
#                 message = question
#                 tipo = "shortcut"
#             else:
#                 message = clean_question
#                 tipo = "openai"

#             resp = ChatResponse(
#                       sender="you", message=message, type="stream"
#                       )
#             await websocket.send_json(resp.dict())

#             # Construct a response
#             start_resp = ChatResponse(sender="bot", message="", type="start")
#             await websocket.send_json(start_resp.dict())

#             if is_query:
#                 # Opción 3: mandar literal el texto
#                 resp = ChatResponse(
#                           sender="bot",
#                           message="\n" + clean_question,
#                           type="stream"
#                           )
#                 await websocket.send_json(resp.dict())
#             else:
#                 await qa_chain.acall(
#                     {"question": clean_question}
#                 )
#             # Record the end time
#             end_time = time()

#             # Calculate the elapsed time
#             elapsed_time = end_time - start_time

#             usage = UsageDB()
#             usage.insert(
#                 question_dict['user'], question_dict['name'],
#                 question_dict['skill'], question_dict['area'], tipo, message,
#                 servicesdb.categoria, servicesdb.nombre,
#                 servicesdb.subcategoria, servicesdb.servicio,
#                 elapsed_time
#                 )
#             servicesdb.clear_attributes()

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
