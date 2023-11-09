from typing import Optional

import pandas as pd
from langchain.chains.qa_generation.base import QAGenerationChain

from .prompt_templates import CHAT_PROMPT
from . import GENERATORS_MAPPING


class QAgeneratorchain:
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
        self.llm_chain_questions = QAGenerationChain.from_llm(
            llm_questions, prompt=CHAT_PROMPT
        )

    def __call__(
            self,
            document: str,
            context: Optional[str]
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
        if context not in ['']:
            text = context + "\n\n" + document
        else:
            text = document

        qa = self.llm_chain_questions.run(text)

        return pd.DataFrame(qa[0])
