import streamlit as st
from st_pages import add_page_title, get_nav_from_toml
from functions.helper_functions.streamlit_setup import page_config

# page_config()

nav = get_nav_from_toml(".streamlit/pages_sections.toml")
pg = st.navigation(nav)

# add_page_title(pg)
# pg.run()

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
