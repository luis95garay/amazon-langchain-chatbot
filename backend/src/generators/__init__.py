from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from pathlib import Path


file_path = Path(__file__).resolve()

env_file_path = file_path.parent.parent / "credentials.env"
load_dotenv(env_file_path)

GENERATORS_MAPPING = {
    "openai": {
        "questions": ChatOpenAI(
            max_tokens=750,
            model_name="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
            ),
        "answers": ChatOpenAI(
            max_tokens=250,
            model_name="gpt-3.5-turbo",
            temperature=0.5,
            openai_api_key=os.getenv("OPENAI_API_KEY")
            )
    }
}
