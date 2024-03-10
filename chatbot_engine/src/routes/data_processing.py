import os
from pathlib import Path
import pickle
from fastapi import Request
from fastapi.routing import APIRouter
from langchain.document_loaders import TextLoader, S3DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

from .response import Responses
from src.utils import load_vectorstore_to_s3, save_files_locally
from src.routes.index import update_all


router = APIRouter(tags=['data_processing'])


@router.get("/create_vectorstore")
async def create_vectorstore():

    save_files_locally()
    
    markdown_path = Path(__file__).parent.parent
    markdown_path = markdown_path / 'chatbot_data'
    print(print(markdown_path))
    data = []
    for file in markdown_path.glob('*.md'):
        loader = TextLoader(str(file))
        data += loader.load()
        os.remove

    text_splitter = MarkdownTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
    )
    data = text_splitter.split_documents(data)

    embeddings = OpenAIEmbeddings()
    current_vectorstore = FAISS.from_documents(data, embeddings)

    # # Save vectorstore
    vs_name = "sagemaker_documentation.pkl"
    with open(vs_name, "wb") as f:
        pickle.dump(current_vectorstore, f)
    
    load_vectorstore_to_s3(vs_name)
    os.remove(vs_name)
    update_all()
    return Responses.ok("Vectorstore updated")
