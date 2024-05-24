import subprocess

from config import cnf
from logger import get_logger, configure_logger


def run_streamlit():
    subprocess.run(["poetry", "run", "python", "-m", "streamlit", "run", "streamlit_app/stream_app.py"])

configure_logger()
logger = get_logger("MAIN")


if __name__ == '__main__':
    logger.info("Starting Streamlit")
    logger.info(f"Streamlit using device: {cnf.INFERENCE_DEVICE}")
    logger.info(f"Streamlit running workers: {cnf.N_WORKERS}")
    run_streamlit()
