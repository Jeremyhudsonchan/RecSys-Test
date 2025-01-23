import streamlit as st
from functions.helper_functions.streamlit_setup import page_config
import os
import logging

try:
    page_config()
except Exception as e:
    print("********")

# create logger for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

# add the console handler to the logger
logger.addHandler(ch)

log_file_path = os.getenv("FRONT_END_LOG_FILE_PATH", "app.log")
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)

# Title
st.title("Movie Recommendations")

# Subheader
st.subheader("Welcome to the Movie Recommendations App!")

# Text
st.write(
    """This app will recommend movies using different methods such as
    graph traversal, embedding similarity, collaborative filtering (to be implemented),
    and content-based filtering (to be implemented)."""
)
