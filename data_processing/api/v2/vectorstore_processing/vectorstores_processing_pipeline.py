import pickle
# from pathlib import Path
from typing import List, Dict
import os

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import CSVLoader
# from dotenv import load_dotenv
import boto3

from constants import (
    BUCKET_NAME, RAW_FOLDER, INTERMEDIATE_FOLDER, FINAL_FOLDER
)


class VectorstoreProcessingPipeline:
    """
    A pipeline for creating, updating, and managing vector stores.

    Attributes:
        embeddings (OpenAIEmbeddings): The embeddings used for creating
            vector stores.
        questions_folder (Path): The path to the folder containing question
            data in CSV format.
        intermediate_vectorstores_folder (Path): The path to the folder for
            storing intermediate vector stores.
        final_vectorstore (Path): The path to the final consolidated vector
            store.

    Methods:
        create(name: str) -> None:
            Create a vector store for the specified name from CSV data.
        update() -> None:
            Update the consolidated vector store with data from intermediate
                vector stores.
        add(name: str) -> None:
            Add data from an intermediate vector store to the consolidated
                vector store.
    """
    def __init__(
            self,
            bucket_name: str = BUCKET_NAME,
            raw_folder: str = RAW_FOLDER,
            partial_folder: str = INTERMEDIATE_FOLDER,
            final_folder: str = FINAL_FOLDER
            ) -> None:
        """
        Initialize the VectorstoreProcessingPipeline.
        """
        # file_path = Path(__file__).resolve()
        # env_file_path = file_path.parent.parent.parent / "credentials.env"
        # load_dotenv(env_file_path)

        self.embeddings = OpenAIEmbeddings()
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("REGION_NAME")
        )
        self.bucket_name = bucket_name
        self.raw_folder = raw_folder
        self.partial_folder = partial_folder
        self.final_folder = final_folder

    def create_from_dict(
            self,
            name: str,
            data: Dict,
            key: str
            ) -> None:
        """
        Create a marginal vectorstore.

        Args:
            file_path (str): The path of the vector store to create.
        """
        questions = [val for val in data['question'].values()]
        answers = [val for val in data['answer'].values()]
        data = [f"Pregunta: {questions[idx]}\nRespuesta: \
                {answers[idx]}" for idx in range(len(questions))]
        current_vectorstore = FAISS.from_texts(data, self.embeddings)

        return self.upload_vectorstore(
                current_vectorstore,
                self.partial_folder,
                name,
                key
            )

    def create_from_list(
            self,
            name: str,
            data: List,
            key: str
            ) -> None:
        """
        Create a marginal vectorstore.

        Args:
            file_path (str): The path of the vector store to create.
        """
        data_final = []
        metadata_list = []
        for val in data:
            tipo, pregunta, respuesta, origen = val
            if tipo in ['pregunta']:
                data_final.append(
                    f"Pregunta: {pregunta}\nRespuesta: {respuesta}"
                )
            elif tipo in ['chunk']:
                data_final.append(respuesta)
            metadata_list.append({"source": origen})

        current_vectorstore = FAISS.from_texts(
            data_final, self.embeddings, metadatas=metadata_list
        )

        return self.upload_vectorstore(
                current_vectorstore,
                self.final_folder,
                name,
                key
            )

    def consolidate(
            self,
            files_paths: List[str],
            key: str
            ):
        """
        Update the consolidated vector store with data from intermediate
        vector stores.
        """
        for idx, vs in enumerate(files_paths):
            # Download the file
            self.s3.download_file(
                self.bucket_name,
                f"{self.partial_folder}/{vs}",
                vs
            )
            if idx == 0:
                with open(vs, "rb") as f:
                    consolidated_vectorstore = pickle.load(f)
            else:
                with open(vs, "rb") as f:
                    current_vectorstore = pickle.load(f)
                consolidated_vectorstore.merge_from(current_vectorstore)

            os.remove(vs)

        return self.upload_vectorstore(
                current_vectorstore,
                self.final_folder,
                "vectorstore",
                key
            )

    def upload_vectorstore(
            self,
            current_vectorstore,
            folder: str,
            name: str,
            key: str
            ) -> str:
        temp_file = f"{name} - {key}.pkl"
        with open(temp_file, 'wb') as pickle_file:
            pickle.dump(current_vectorstore, pickle_file)

        # object_key = f"{folder}/{name} - {key}.pkl"
        object_key = f"{folder}/vectorstore.pkl"
        self.s3.upload_file(
            temp_file,
            self.bucket_name,
            object_key
        )

        os.remove(temp_file)

        return object_key
