import logging
import pickle
from pathlib import Path

from constants import LOCAL_VECTORSTORE_PATH


class VectorstoreDB:
    """
    A class for managing a vector store database.

    This class loads a pre-trained vector store from a pickle file.

    Attributes:
        vectorstore: The loaded vector store.

    """
    def __init__(self) -> None:
        logging.info("loading vectorstore")
        if not Path(LOCAL_VECTORSTORE_PATH).exists():
            raise ValueError(
                "vectorstore.pkl does not exist"
                )
        with open(LOCAL_VECTORSTORE_PATH, "rb") as f:
            self.vectorstore = pickle.load(f)
