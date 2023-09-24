from typing import List, Optional
from pathlib import Path
import pickle

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.schema.document import Document

from data_processing_api.text_extractors.loaders import MAPPED_LOADERS_METHODS


class TextExtractorPipeline:
    """
    A class that represents a pipeline for extracting text documents
    using different loaders.

    Args:
        loader_name (str): The name of the loader to be used for text
        extraction.

    Attributes:
        extractor (callable): The loader method chosen based on the
        provided loader_name.

    """
    def __init__(self, loader_name: str):
        try:
            self.extractor = MAPPED_LOADERS_METHODS[loader_name]
        except IndexError:
            raise ValueError(f"{loader_name} loader is not mapped")

    def get_documents(
        self,
        file_path: str,
        chunk_size: Optional[int] = 5000,
        chunk_overlap: Optional[int] = 200,
        is_folder: bool = False
    ) -> List[Document]:
        """
        Extract text from a file using the chosen loader and split
        them in smaller chunks

        Args:
            file_path (str): The path to the file to be loaded.
            chunk_size (int, optional): The size of each chunk for
              loading. Default is 5000.
            chunk_overlap (int, optional): The overlap between
              consecutive chunks. Default is 200.

        Returns:
            List[Document]: A list of Document objects representing
              the extracted text chunks.

        """
        path = Path(file_path)

        if is_folder:
            documents = []
            for file in path.iterdir():
                loader = self.extractor(file)
                documents += loader.load()
        else:
            loader = self.extractor(path)
            documents = loader.load()

        return loader.clean_load(documents, chunk_size, chunk_overlap)
    
    def create_vectorstore(
        self,
        documents: List[Document],
    ) -> None:
        """
        Extract text from a file using the chosen loader and split
        them in smaller chunks

        Args:
            file_path (str): The path to the file to be loaded.
            chunk_size (int, optional): The size of each chunk for
              loading. Default is 5000.
            chunk_overlap (int, optional): The overlap between
              consecutive chunks. Default is 200.

        Returns:
            List[Document]: A list of Document objects representing
              the extracted text chunks.

        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        embeddings = OpenAIEmbeddings()
        current_vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

        file_path = Path(__file__).resolve()

        vectorstores_path = file_path.parent.parent.parent \
            .parent.parent / "data" / "final_vectorstores" / "vectorstore.pkl"
        with open(vectorstores_path, "wb") as f:
            pickle.dump(current_vectorstore, f)
