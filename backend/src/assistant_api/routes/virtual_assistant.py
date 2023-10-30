"""Main entrypoint for the app."""
# import logging
from typing import AsyncIterable
# from pathlib import Path

# from dotenv import load_dotenv
import asyncio
# from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler

# from assistant_api.callback import (
#     StreamingLLMCallbackHandler, QuestionGenCallbackHandler
#     )
from assistant_api.chains.assistants import (
    get_chain_RetrievalQASources_v0, get_chain_RetrievalQASources_v1
)
from assistant_api.schemas import InputRequest
from assistant_api.db.vectorstoredb import VectorstoreDB

# Get the absolute path of the current Python script
# file_path = Path(__file__).resolve()

# Construct the path to the .env file in the grandparent folder
# env_file_path = file_path.parent.parent.parent / "credentials.env"

# Load environment variables from the .env file
# load_dotenv(env_file_path)
router = APIRouter(tags=['virtual_assistant'])


async def send_message(content: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    vecstore = VectorstoreDB()

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


@router.post("/stream_chat/")
async def stream_chat(message: InputRequest):
    generator = send_message(message.input)
    return StreamingResponse(generator, media_type="text/event-stream")


# Simple request
@router.post("/chat")
async def ask_question(
    params: InputRequest
):
    """Handle a POST request to ask a question and return a response."""
    vecstore = VectorstoreDB()
    qa1 = get_chain_RetrievalQASources_v0(vecstore.vectorstore)
    try:
        # Use a more descriptive variable name for the result
        qa_result = qa1(params.input, return_only_outputs=True)

        # Extract answer and sources from the result
        answer = qa_result.get('answer', 'No answer found')
        sources = qa_result.get('sources', 'No sources found')

        # Create a formatted response text
        response_text = f"{answer}\n\n\n\nLook for more information in:\n\n{sources}"

        return {'text': response_text, 'source': sources}
    except Exception:
        # Handle any exceptions that may occur
        error_message = "Sorry, something went wrong. Try again"
        return {'text': error_message, 'source': None}


# # Option with websocket
# @router.websocket("/chat")
# async def websocket_endpoint(
#         websocket: WebSocket,
#         vectorstore: VectorStore = Depends(get_file_content)
#         ):
#     """
#     WebSocket endpoint for real-time chat with a bot.

#     Args:
#         websocket (WebSocket): The WebSocket connection.
#         vectorstore (VectorStore): A vector store used for chat processing.

#     """
#     await websocket.accept()
#     question_handler = QuestionGenCallbackHandler(websocket)
#     stream_handler = StreamingLLMCallbackHandler(websocket)
#     qa_chain = get_chain_v0(vectorstore, question_handler, stream_handler)

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

#             await qa_chain.acall(
#                 {"question": question}
#             )

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
