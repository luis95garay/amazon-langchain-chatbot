from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from langchain.vectorstores import VectorStore
import logging
import pickle


vectorstore: Optional[VectorStore] = None


def load_file_content():
    # Get the absolute path of the current Python script
    file_path = Path(__file__).resolve()

    # Construct the path to the .env file in the grandparent folder
    env_file_path = file_path.parent.parent / "credentials.env"
    vectorstores_path = file_path.parent \
        .parent.parent / "data" / "final_vectorstores" / "vectorstore.pkl"
    # Load environment variables from the .env file
    load_dotenv(env_file_path)
    logging.info("loading vectorstore")
    if not Path(vectorstores_path).exists():
        raise ValueError(
            "vectorstore.pkl does not exist"
            )
    with open(vectorstores_path, "rb") as f:
        global vectorstore
        vectorstore = pickle.load(f)


# Create a dependency to provide the loaded file content
def get_file_content():
    return vectorstore
