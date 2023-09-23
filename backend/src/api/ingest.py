"""Load html from files, clean up, split, ingest into Weaviate."""
from langchain.vectorstores.faiss import FAISS
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
import pickle
from pathlib import Path
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownTextSplitter


def ingest_docs():
    """Get documents from web pages."""
    markdown_path = Path('C:/Users/luisg/Documents/projects/LOKA/langchain_virtual_assistant/data/sagemaker_documentation')

    data = []
    for idx, file in enumerate(markdown_path.glob('*.md')):
        print(idx)
        loader = UnstructuredMarkdownLoader(str(file), mode='single')
        data += loader.load()

    text_splitter = MarkdownTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    data = text_splitter.split_documents(data)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(data, embeddings)

    # Save vectorstore
    with open("C:/Users/luisg/Documents/projects/LOKA/langchain_virtual_assistant/data/vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    load_dotenv("./credentials.env")
    ingest_docs()
