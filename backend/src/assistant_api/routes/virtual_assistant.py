"""Main entrypoint for the app."""
import logging

from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from langchain.vectorstores import VectorStore

from assistant_api.callback import (
    StreamingLLMCallbackHandler, QuestionGenCallbackHandler
    )
from assistant_api.chains.assistants import (
    get_chain_v0, get_chain_RetrievalQASources_v0
)
from assistant_api.schemas import ChatResponse, InputRequest
from assistant_api.utils import get_file_content, load_file_content


router = APIRouter(tags=['virtual_assistant'])

# Load chain
load_file_content()
# qa1 = get_chain_v1(get_file_content())
qa1 = get_chain_RetrievalQASources_v0(get_file_content())


# Simple request
@router.post("/request/chat")
def ask_question(
    params: InputRequest
):
    """Handle a POST request to ask a question and return a response."""
    try:
        # Use a more descriptive variable name for the result
        qa_result = qa1(params.input, return_only_outputs=True)

        # Extract answer and sources from the result
        answer = qa_result.get('answer', 'No answer found')
        sources = qa_result.get('sources', 'No sources found')

        # Create a formatted response text
        response_text = f"{answer}\n\n\n\nLook for more information in:\n\n{sources}"

        return {'text': response_text}
    except Exception:
        # Handle any exceptions that may occur
        error_message = "Sorry, something went wrong. Try again"
        return {'text': error_message}


# Option with websocket
@router.websocket("/chat")
async def websocket_endpoint(
        websocket: WebSocket,
        vectorstore: VectorStore = Depends(get_file_content)
        ):
    """
    WebSocket endpoint for real-time chat with a bot.

    Args:
        websocket (WebSocket): The WebSocket connection.
        vectorstore (VectorStore): A vector store used for chat processing.

    """
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    qa_chain = get_chain_v0(vectorstore, question_handler, stream_handler)

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
