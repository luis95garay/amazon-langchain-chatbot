import os
from pathlib import Path
from fastapi.routing import APIRouter
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters.markdown import MarkdownTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from .response import Responses
from src.utils import save_files_locally


router = APIRouter(tags=['data_processing'])


@router.get("/create_vectorstore")
async def create_vectorstore():

    save_files_locally()

    markdown_path = Path(__file__).parent.parent
    markdown_path = markdown_path / 'chatbot_data'
    data = []
    for file in markdown_path.glob('*.md'):
        loader = TextLoader(str(file))
        data += loader.load()
        os.remove(str(file))

    text_splitter = MarkdownTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    data = text_splitter.split_documents(data)

    embeddings = OpenAIEmbeddings()

    Qdrant.from_documents(
        data,
        embeddings,
        url=os.getenv("QDRANT_URL"),
        prefer_grpc=True,
        api_key=os.getenv("QDRANT_KEY"),
        collection_name="myvectorstore",
        force_recreate=True,
    )

    return Responses.ok("Vectorstore updated")
