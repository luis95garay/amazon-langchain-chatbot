from datetime import date
from pathlib import Path
from json import JSONDecodeError

import pandas as pd

from api.generators.qa_generators import QAgeneratorchain
from api.text_extractors.pipelines.loaders_pipeline import (
    TextExtractorPipeline
    )


class BaseProcessingPipeline:
    def __init__(self) -> None:
        data_path = Path(__file__).parent.parent.parent / "data"
        self.questions_folder = data_path / "questions"

    def save_data(self, df: pd.DataFrame, name: str):
        # Save csv
        q_save_path = self.questions_folder / f"{name}.csv"
        df.to_csv(str(q_save_path), index=False, encoding="utf-8")


class UnstructuredProcessingPipeline:
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
        self.qa_generator = QAgeneratorchain(generator)

    def __call__(
            self,
            path: str,
            description: str,
            mode: str = None,
            from_date: date = None,
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
        documents = self.loader(path, mode=mode, from_date=from_date)

        # Generate questions and answers
        df_list = []
        for doc in documents:
            try:
                df = self.qa_generator(doc.page_content, description)
                df_list.append(df)
            except JSONDecodeError:
                continue

        df_questions = pd.concat(df_list)

        return [tuple(x) for x in df_questions.to_records(index=False)]


class StructuredProcessingPipeline:
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
            path: str
            ) -> None:
        """
        Process a structured data file, read its content, and save it in
        a standardized format.

        Args:
            path (str): The path to the structured data file to process.
        """
        if self.file_format in ["csv"]:
            df_data = pd.read_csv(path, encoding="utf-8")
        elif self.file_format in ["xlsx"]:
            df_data = pd.read_excel(path)

        old_names = df_data.columns.tolist()[:2]
        new_names = {old_names[0]: "question", old_names[1]: "answer"}
        df_data.rename(columns=new_names, inplace=True)
        return df_data.to_dict()
