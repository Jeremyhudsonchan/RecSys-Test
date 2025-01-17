import streamlit as st
from functions.helper_functions.streamlit_setup import page_config

page_config()

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
