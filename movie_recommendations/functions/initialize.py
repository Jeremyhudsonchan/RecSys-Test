import os
from dotenv import load_dotenv
import logging
from functions.data_preprocess import pre_created_embeddings_load, drop_missing


# Load environment variables
load_dotenv(".env")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create file handler
log_file_path = os.getenv("INITIALIZE_LOG_FILE_PATH", "app.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def start():
    logger.info("Initializing the application")
    logger.info("Loading pre-created embeddings")
    pre_created_embeddings_load()
    logger.info("Dropping missing data")
    drop_missing()
