from typing import Optional
from pathlib import Path
import logging
import pickle

from langchain.vectorstores import VectorStore


vectorstore: Optional[VectorStore] = None


def load_file_content():
    # Get the absolute path of the current Python script
    file_path = Path(__file__).resolve()

    vectorstores_path = file_path.parent \
        .parent.parent / "data" / "final_vectorstores" / "vectorstore3000.pkl"

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
