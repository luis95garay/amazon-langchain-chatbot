from src.generators.qa_generators import QAgenerator
from src.text_extractors.pipelines.loaders_pipeline import (
    TextExtractorPipeline
    )
import pickle
from pathlib import Path
import pandas as pd
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import CSVLoader


class BaseProcessingPipeline:
    def __init__(self) -> None:
        data_path = Path(__file__).parent.parent.parent / "data"
        self.questions_folder = data_path / "questions"

    def save_data(self, df: pd.DataFrame, name: str):
        # Save csv
        q_save_path = self.questions_folder / f"{name}.csv"
        df.to_csv(str(q_save_path), index=False, encoding="utf-8")


class UnstructuredProcessingPipeline(BaseProcessingPipeline):
    """
    A pipeline for processing unstructured text documents by extracting
    text and generating questions and answers using a specified extractor
    and question-answer generator.
    """
    def __init__(
            self,
            extractor: str,
            generator: str = "openai"
            ) -> None:
        """
        Initialize the UnstructuredProcessingPipeline.

        Args:
            extractor (str): The type of text extractor to use for document
                processing.
            generator (str, optional): The question-answer generator to use
                (default is "openai").
        """
        super().__init__()
        self.extractor = extractor
        self.loader = TextExtractorPipeline(extractor)
        self.qa_generator = QAgenerator(generator)

    def __call__(
            self,
            path: str,
            name: str,
            description: str
            ) -> None:
        """
        Process documents in the specified path, extract text from them,
        generate questions and answers, and save the results in a CSV file.

        Args:
            path (str): The path to the directory containing the documents
                to process.
            name (str): The name of the CSV file to save the generated
                questions and answers.
            description (str): Introduction about the source to process
        """
        # Extract text in documents
        documents = self.loader(path)

        # Generate questions and answers
        df_list = [self.qa_generator(doc.page_content, description) for doc in documents]
        df_questions = pd.concat(df_list)

        # Save csv
        self.save_data(df_questions, name)


class StructuredProcessingPipeline(BaseProcessingPipeline):
    """
    A pipeline for processing structured data files in various formats and
    saving them in a standardized format.
    """
    def __init__(
            self,
            file_format: str,
            ) -> None:
        """
        Initialize the StructuredProcessingPipeline.

        Args:
            file_format (str): The format of the structured data file
                to process.
        """
        super().__init__()
        self.file_format = file_format

    def __call__(
            self,
            path: str,
            name: str,
            description: str
            ) -> None:
        """
        Process a structured data file, read its content, and save it in
        a standardized format.

        Args:
            path (str): The path to the structured data file to process.
            name (str): The name of the file to save the processed data.
            description (str): Introduction of the data to preprocess
        """
        if self.file_format in ["csv"]:
            df_data = pd.read_csv(path, encoding="utf-8")
        elif self.file_format in ["xlsx"]:
            df_data = pd.read_excel(path)
        
        df_data['CONTEXT'] = description

        # Save csv
        self.save_data(df_data, name)


class VectorstoreProcessingPipeline:
    """
    A pipeline for creating, updating, and managing vector stores.

    Attributes:
        embeddings (OpenAIEmbeddings): The embeddings used for creating
            vector stores.
        questions_folder (Path): The path to the folder containing question
            data in CSV format.
        intermediate_vectorstores_folder (Path): The path to the folder for
            storing intermediate vector stores.
        final_vectorstore (Path): The path to the final consolidated vector
            store.

    Methods:
        create(name: str) -> None:
            Create a vector store for the specified name from CSV data.
        update() -> None:
            Update the consolidated vector store with data from intermediate
                vector stores.
        add(name: str) -> None:
            Add data from an intermediate vector store to the consolidated
                vector store.
    """
    def __init__(
            self
            ) -> None:
        """
        Initialize the VectorstoreProcessingPipeline.
        """
        self.embeddings = OpenAIEmbeddings()
        data_path = Path(__file__).parent.parent.parent / "data"
        self.questions_folder = data_path / "questions"
        self.intermediate_vectorstores_folder = \
            data_path / "intermediate_vectorstores"
        self.final_vectorstore = \
            data_path / "final_vectorstores" / "vectorstore.pkl"

    def create(
            self,
            name: str
            ) -> None:
        """
        Create a vector store for the specified name from CSV data.

        Args:
            name (str): The name of the vector store to create.
        """
        # Create current vectorstore
        csv_file_path = self.questions_folder / f"{name}.csv"
        loader = CSVLoader(csv_file_path, encoding="utf-8")
        data = loader.load()
        data = [doc.page_content for doc in data]
        current_vectorstore = FAISS.from_texts(data, self.embeddings)

        # Save vectorstore
        vs_file_path = self.intermediate_vectorstores_folder / f"{name}.pkl"
        with open(str(vs_file_path), "wb") as f:
            pickle.dump(current_vectorstore, f)

    def update(self):
        """
        Update the consolidated vector store with data from intermediate
        vector stores.
        """
        vectorstores_files = \
            self.intermediate_vectorstores_folder.glob("*.pkl")
        for idx, vs in enumerate(vectorstores_files):
            if idx == 0:
                with open(str(vs), "rb") as f:
                    consolidated_vectorstore = pickle.load(f)
            else:
                with open(str(vs), "rb") as f:
                    current_vectorstore = pickle.load(f)
                consolidated_vectorstore.merge_from(current_vectorstore)

        # Save vectorstore
        with open(str(self.final_vectorstore), "wb") as f:
            pickle.dump(consolidated_vectorstore, f)

    def add(self, name: str):
        """
        Add data from an intermediate vector store to the consolidated
        vector store.

        Args:
            name (str): The name of the intermediate vector store to add.
        """
        vs_file_path = self.intermediate_vectorstores_folder / f"{name}.pkl"
        with open(str(vs_file_path), "rb") as f:
            current_vectorstore = pickle.load(f)

        try:
            with open(str(self.final_vectorstore), "rb") as f:
                final_vectorstore = pickle.load(f)
            final_vectorstore.merge_from(current_vectorstore)

        except FileNotFoundError:
            final_vectorstore = current_vectorstore

        # Save vectorstore
        with open(str(self.final_vectorstore), "wb") as f:
            pickle.dump(final_vectorstore, f)

    def remove(self, name: str):
        """
        Remove data from an intermediate vector store and update the
        consolidated one.

        Args:
            name (str): The name of the intermediate vector store to remove.
        """
        vs_file_path = self.intermediate_vectorstores_folder / f"{name}.pkl"
        vs_file_path.unlink()
        self.update()
