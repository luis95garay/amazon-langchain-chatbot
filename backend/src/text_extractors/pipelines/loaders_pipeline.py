from typing import List, Optional
from src.text_extractors.loaders import MAPPED_LOADERS_METHODS
from langchain.schema.document import Document


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

    def __call__(
        self,
        file_path: str,
        chunk_size: Optional[int] = 5000,
        chunk_overlap: Optional[int] = 200
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
        loader = self.extractor(file_path)
        return loader.clean_load(chunk_size, chunk_overlap)
