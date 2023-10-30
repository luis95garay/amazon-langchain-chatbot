from pathlib import Path


path = Path(__file__)

BUCKET_NAME = "asistente-virtual-bm"
RAW_FOLDER = "raw"
INTERMEDIATE_FOLDER = "intermediate_vectorstores"
FINAL_FOLDER = "final_vectorstores"


BUCKET_VECTORSTORE_PATH = f'{FINAL_FOLDER}/vectorstore.pkl'
LOCAL_VECTORSTORE_PATH = path.parent \
        .parent / "data" / FINAL_FOLDER / "vectorstore.pkl"
