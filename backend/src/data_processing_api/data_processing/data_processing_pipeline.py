from data_processing_api.generators.qa_generators import QAgenerator
from data_processing_api.text_extractors.pipelines.loaders_pipeline import (
    TextExtractorPipeline
    )
from pathlib import Path
import pandas as pd


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
        df_list = [self.qa_generator(doc.page_content, description)
                   for doc in documents]
        df_questions = pd.concat(df_list)

        # Save csv
        # self.save_data(df_questions, name)
        return df_questions.to_dict()


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

        # df_data['CONTEXT'] = description

        # Save csv
        self.save_data(df_data, name)
