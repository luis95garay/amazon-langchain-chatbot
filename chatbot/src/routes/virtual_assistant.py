"""Main entrypoint for the app."""
import asyncio
import logging
from typing import AsyncIterable

# import pandas as pd
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler

from src.callback import (
    StreamingLLMCallbackHandler, QuestionGenCallbackHandler
    )
from src.chains.assistants import (
    get_chain_v0, get_chain_v0_simple, get_chain_stream, get_chain_RetrievalQASources_v1
)
from src.schemas import InputRequest
from src.db.vectorstoredb import VectorstoreDB


router = APIRouter(tags=['virtual_assistant'])


def get_vectorstore():
    return VectorstoreDB()


class QAImplementation:
    def __init__(self, vecstore: VectorstoreDB):
        self.ask = get_chain_v0_simple(vecstore.vectorstore)


def get_qa(vecstore: VectorstoreDB = Depends(get_vectorstore)):
    return QAImplementation(vecstore)


async def send_message(content: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    vecstore = VectorstoreDB()

    # qa = get_chain_stream(vecstore.vectorstore, callback)
    qa = get_chain_RetrievalQASources_v1(vecstore.vectorstore, callback)

    task = asyncio.create_task(
        qa.acall({"question": content})
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
    params: InputRequest,
    qa1: QAImplementation = Depends(get_qa)
):
    """Handle a POST request to ask a question and return a response."""
    try:
        # Use a more descriptive variable name for the result
        qa_result = qa1.ask({"question": params.input})

        return qa_result
    except Exception:
        # Handle any exceptions that may occur
        error_message = "Sorry, something went wrong. Try again"
        return {'text': error_message, 'source': None}


# Stream request
@router.post("/stream_chat/")
async def stream_chat(message: InputRequest):
    generator = send_message(message.input)
    return StreamingResponse(generator, media_type="text/event-stream")


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
#     # Use the below line instead of the above line to enable tracing
#     # Ensure `langchain-server` is running
#     # qa_chain = get_chain(
#     # vectorstore, question_handler, stream_handler, tracing=True
#     # )
#     # count = 0
#     while True:
#         try:
#             # Receive and send back the client message
#             question = await websocket.receive_text()
#             is_query, clean_question = servicesdb.run_query(question)
#             usage = UsageDB()
#             if is_query:
#                 message = question
#                 usage.insert("shortcut", message)
#             else:
#                 message = clean_question
#                 usage.insert("openai", message)

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


# @router.websocket("/chat")
# async def websocket_endpoint(
#         websocket: WebSocket,
#         vectorstore: VectorStore = Depends(get_file_content),
#         df_prices: pd.DataFrame = Depends(get_prices_content)
#         ):
#     """
#     WebSocket endpoint for real-time chat with a bot.

#     Args:
#         websocket (WebSocket): The WebSocket connection.
#         vectorstore (VectorStore): A vector store used for chat processing.
#         df_prices (pd.DataFrame): prices csv file

#     """
#     await websocket.accept()
#     question_handler = QuestionGenCallbackHandler(websocket)
#     stream_handler = StreamingLLMCallbackHandler(websocket)
#     # qa_chain = get_router_assistant(
#     #     vectorstore,
#     #     df_prices,
#     #     question_handler,
#     #     stream_handler
#     #     )
#     qa_chain = get_chainCustom(
#         vectorstore,
#         question_handler,
#         stream_handler
#         )
#     while True:
#         try:
#             # Receive and send back the client message
#             question = await websocket.receive_text()
#             is_query, clean_question = run_query(question)

#             if is_query:
#                 message = question
#             else:
#                 message = clean_question

#             resp = ChatResponse(
#                       sender="you", message=message, type="stream"
#                       )
#             await websocket.send_json(resp.dict())

#             # Construct a response
#             start_resp = ChatResponse(sender="bot", message="", type="start")
#             await websocket.send_json(start_resp.dict())

#             if is_query:
#                 # Opción 1: reescribir la tabla con openai
#                 # messages = [
#                 #     SystemMessage(content="Eres un asistente amable de la \
#                                               empresa blue medical"),
#                 #     HumanMessage(content=f"Re escribe lo siguiente tabla \
#                                    en lenguaje natural y muestra los \
#                                    precios en quetzales \
#                                    (Q): \n\n{clean_question}")
#                 # ]
#                 # result = qa_chain_simple(messages)
#                 # resp = ChatResponse(
#                 #           sender="bot",
#                             message=result.content,
#                             type="stream"
#                 #           )
#                 # await websocket.send_json(resp.dict())

#                 # Opción 2: mandar asincrónico palabra por palabra
#                 # for row in clean_question.split("\n"):
#                 #     resp = ChatResponse(
#                 #             sender="bot", message=row + "\n", type="stream"
#                 #             )
#                 #     await asyncio.sleep(0.5)
#                 #     await websocket.send_json(resp.dict())

#                 # Opción 3: mandar literal el texto
#                 resp = ChatResponse(
#                           sender="bot", message=clean_question, type="stream"
#                           )
#                 await websocket.send_json(resp.dict())
#             else:
#                 await qa_chain.acall(
#                     {"input": clean_question}
#                 )

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
