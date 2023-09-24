"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle

from langchain.document_loaders import (
    ReadTheDocsLoader, AsyncHtmlLoader, WebBaseLoader, RecursiveUrlLoader
)
from bs4 import BeautifulSoup as Soup
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from dotenv import load_dotenv


def ingest_docs():
    """Get documents from web pages."""
    # loader = WebBaseLoader(["https://mibluemedical.com/blue-medical-ubicaciones/"])
    # loader = ReadTheDocsLoader("rtdocs", features="xml", encoding="utf8")
    loader = RecursiveUrlLoader("https://mibluemedical.com/", extractor=lambda x: Soup(x, "html.parser").text)
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    load_dotenv("credentials.env")
    ingest_docs()
