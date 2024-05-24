import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from api_config import get_api
from config import cnf
from logger import get_logger, configure_logger


app = get_api()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logger()
logger = get_logger("MAIN")


if __name__ == "__main__":

    logger.info("Starting API")
    logger.info(f"API using device: {cnf.INFERENCE_DEVICE}")
    logger.info(f"API running workers: {cnf.N_WORKERS}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        access_log=True,
        workers=cnf.N_WORKERS,
    )
