import json
import pandas as pd
from .prompt_templates import question_template, answer_template
from . import GENERATORS_MAPPING
from langchain.chains.llm import LLMChain


class QAgenerator:
    """
    A class for generating and answering questions using language models.

    This class provides a pipeline for generating questions and answers
    using language models. It takes a generator name as input and uses
    predefined templates for generating and answering questions.

    """
    def __init__(
            self,
            generator: str = "openai"
            ) -> None:
        """
        Initialize the QApipeline instance.

        Args:
            generator (str, optional): The name of the generator to use.
            Defaults to "openai".
        """
        llm_questions = GENERATORS_MAPPING[generator]["questions"]
        llm_answers = GENERATORS_MAPPING[generator]["answers"]
        self.llm_chain_questions = LLMChain(
            prompt=question_template, llm=llm_questions
            )
        self.llm_chain_answers = LLMChain(
            prompt=answer_template, llm=llm_answers
            )

    def generate_questions(self) -> str:
        """
        Generate questions based on the provided document.

        Returns:
            str: The generated questions.
        """
        kwards = {"document": self.document, "context": self.context}
        return self.llm_chain_questions.run(**kwards)

    def answer(self, row) -> str:
        """
        Answer a question based on the provided row data.

        Args:
            row: The question to answer

        Returns:
            str: The generated answer.
        """
        kwards = {"row": row, "document": self.document}
        return self.llm_chain_answers.run(**kwards)

    def __call__(
            self,
            document: str,
            context: str
            ) -> pd.DataFrame:
        """
        Generate questions and answers for the provided document.

        Args:
            document (str): The document for which to generate
            questions and answers.
            context (str): Explanation of the source to extract

        Returns:
            pd.DataFrame: A DataFrame containing generated
            questions and their answers.
        """
        self.document = document
        self.context = context

        # Generate questions:
        response = self.generate_questions()
        print("preguntas generadas")
        # Convertir la cadena de texto en un objeto JSON
        objeto_json = json.loads(response)

        # Create a DataFrame from the dictionary
        df_questions = pd.DataFrame(objeto_json)
        print("dataframe creado")
        # Answer questions
        df_questions["answer"] = df_questions.question.apply(self.answer)
        print("preguntas respondidas")
        return df_questions
