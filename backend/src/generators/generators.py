import openai
import os
import cohere


class OpenAIGenerator:
    """
    A class for generating text using the OpenAI API.

    This class provides a convenient way to generate text by interacting with
    the OpenAI API using the given model. The generated text is based on a
    user-provided prompt.
    """
    def __init__(
          self,
          model: str = "gpt-3.5-turbo",
          temperature: int = 0
          ) -> None:
        """
        Initialize the OpenAIGenerator instance.

        Args:
            model (str, optional): The model to use for text generation.
                    Defaults to "gpt-3.5-turbo".
            temperature (float, optional): The temperature parameter for
                    controlling randomness in text generation. Higher
                    values (e.g., 1.0) make the output more random, while
                    lower values (e.g., 0.2) make it more
                    focused.Defaults to 0.
        """
        self.model = model
        self.temperature = temperature

    def __call__(self, prompt: str) -> str:
        """
        Generate text based on the provided prompt.

        Args:
            prompt (str): The user-provided prompt for text generation.

        Returns:
            str: The generated text.
        """
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        return response.choices[0].message["content"]


class CohereGenerator:
    """
    A class for generating text using the Cohere API.

    This class provides a convenient way to generate text by
    interacting with the Cohere API using the given model.
    The generated text is based on a user-provided prompt.

    """
    def __init__(
          self,
          model: str = "command",
          temperature: int = 0
          ) -> None:
        """
        Initialize the CohereGenerator instance.

        Args:
            model (str, optional): The model to use for text generation.
                    Defaults to "command".
            temperature (float, optional): The temperature parameter for
                    controlling randomness in text generation. Higher
                    values (e.g., 1.0) make the output more random,
                    while lower values (e.g., 0.2) make it more focused.
                    Defaults to 0.
        """
        self.model = model
        self.temperature = temperature
        self.co = cohere.Client(os.getenv("COHERE_API_KEY"))

    def __call__(self, prompt: str) -> str:
        """
        Generate text based on the provided prompt.

        Args:
            prompt (str): The user-provided prompt for text generation.

        Returns:
            str: The generated text.
        """
        response = self.co.generate(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature
            )
        return response.generations[0].text
