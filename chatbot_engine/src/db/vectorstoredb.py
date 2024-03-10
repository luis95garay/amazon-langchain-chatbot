import logging
import pickle

import redis

from constants import REDIS_HOST, REDIS_PORT


redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


class VectorstoreDB:
    """
    A class for managing a vector store database.

    This class loads a pre-trained vector store from a pickle file.

    Attributes:
        vectorstore: The loaded vector store.

    """
    def __init__(self, vectorstore_hash: str) -> None:
        logging.info("loading vectorstore")
        vectorstore_b = redis_client.get(vectorstore_hash)

        if not vectorstore_b:
            raise ValueError(
                f"vectorstore with hash {vectorstore_hash} does not exist"
                )
        self.vectorstore = pickle.loads(vectorstore_b)
