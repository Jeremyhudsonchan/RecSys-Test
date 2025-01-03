import streamlit as st
from functions.general import (
    list_all_movies,
    list_all_genres,
    search_movies_based_genres,
    display_movie_metadata,
)
from functions.helper_functions.streamlit_setup import page_config
import pandas as pd
import os
from dotenv import load_dotenv
import logging


page_config()

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
st.title("Movie Recommendations Using Basic Cypher Queries/Graph Traversal")

# Subheader
st.subheader("Select your favorite movies to get recommendations!")

available_genres = pd.DataFrame(list_all_genres())
available_genres = pd.json_normalize(available_genres["Genre"])

# for the row that (no genres listed), we will display it as "Other"
available_genres["name"] = available_genres["name"].apply(
    lambda x: "Other" if x == "(no genres listed)" else x
)
available_genres_list = available_genres["name"].tolist()
available_genres_list.sort()

selected_genres = st.multiselect(
    "Select Genres to filter for movies",
    available_genres_list,
)

if selected_genres:
    selected_genres = [genre for genre in selected_genres if genre != "Other"]
    if "Other" in selected_genres:
        selected_genres.append("(no genres listed)")

    selected_genres = list(set(selected_genres))
    movies_genre_based = search_movies_based_genres(selected_genres)
    # each item in list movies_genre_based containts a json with keys "Movie". "MovieID", "Genre", and "GenreID"
    # For the Movie key, it is another json and I want to display all the properties of the movie in its own columns
    # And lastly display the Genre
    movies_genre_based = pd.json_normalize(movies_genre_based)
    movies_genre_based = movies_genre_based.drop(columns=["GenreID", "MovieID"])
    movies_genre_based = movies_genre_based.drop(
        columns=[
            "Movie.year",
            "Movie.imdbId",
        ]
    )
    # movies might appear in multiple genres, so we will drop duplicates based on the title after we will append all genres the movie is in and display it in the Genre column
    # group by title and aggregate the genres
    # Also we need to keep the Movie Title
    movies_genre_based = movies_genre_based.groupby("Movie.title").agg(
        {
            "Genre": lambda x: ", ".join(x),
            "Movie.released": "first",
            "Movie.imdbRating": "first",
            "Movie.imdbVotes": "first",
            "Movie.plot": "first",
            "Movie.runtime": "first",
            "Movie.languages": "first",
            "Movie.poster": "first",
            "Movie.url": "first",
        }
    )
    movies_genre_based = movies_genre_based.reset_index()

    # orderby Movie.imdbVotes
    movies_genre_based = movies_genre_based.sort_values(
        by=["Movie.imdbVotes"], ascending=False
    )

    # reorder columns to: ['Genre', 'Movie.title', 'Movie.released', 'Movie.imdbRating', 'Movie.imdbVotes', 'Movie.plot',
    # 'Movie.runtime', 'Movie.languages', 'Movie.poster','Movie.url']
    movies_genre_based = movies_genre_based[
        [
            "Genre",
            "Movie.title",
            "Movie.released",
            "Movie.imdbRating",
            "Movie.imdbVotes",
            "Movie.plot",
            "Movie.runtime",
            "Movie.languages",
            "Movie.poster",
            "Movie.url",
        ]
    ]
    st.write(
        f"Movies based on selected genres {selected_genres}, ordered by IMDb Votes"
    )
    st.dataframe(movies_genre_based, use_container_width=True, hide_index=True)

    st.header("Select Movies to get Recommendations")
    all_movies = list_all_movies()
    # sort all_movies by imdbVotes
    all_movies = pd.json_normalize(all_movies)
    all_movies = all_movies.drop(
        columns=[
            "Movie.year",
            "Movie.imdbId",
        ]
    )
    all_movies = all_movies.sort_values(by=["Movie.imdbVotes"], ascending=False)

    selected_movies = st.multiselect(
        "Select up to 10 Movies to get Recommendations",
        all_movies["Movie.title"].tolist(),
        max_selections=10,
    )

    if selected_movies:
        st.success("You have selected the following movies:")
        count = 1
        for movie in selected_movies:
            # look up the movie_id based off the title
            movie_id = all_movies[all_movies["Movie.title"] == movie]["MovieID"].values[
                0
            ]
            # Using that movie_id, display the movie's metadata + genre
            movie_metadata = display_movie_metadata(movie_id)
            display_data = pd.json_normalize(movie_metadata)
            display_data = display_data.drop(columns=["GenreID", "MovieID"])
            # group by title and aggregate the genres
            # Also we need to keep the Movie Title
            display_data = display_data.groupby("Movie.title").agg(
                {
                    "Genre": lambda x: ", ".join(x),
                    "Movie.released": "first",
                    "Movie.imdbRating": "first",
                    "Movie.imdbVotes": "first",
                    "Movie.plot": "first",
                    "Movie.runtime": "first",
                    "Movie.languages": "first",
                    "Movie.poster": "first",
                    "Movie.url": "first",
                }
            )
            display_data = display_data.reset_index()

            st.write(f"{count}. {movie}")
            st.markdown(
                f"![{display_data['Movie.title'].values[0]}]({display_data['Movie.poster'].values[0]})"
            )
            st.write(f"Plot: {display_data['Movie.plot'].values[0]}")
            st.dataframe(display_data, use_container_width=True, hide_index=True)
            count += 1
        # st.session_state.generate_recs_button = st.button("Generate Recommendations")
        generate_recs_button = st.button("Generate Recommendations")
        if generate_recs_button:
            st.write("Recommendations will be displayed here")