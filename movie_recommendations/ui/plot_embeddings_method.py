import streamlit as st
from functions.general import (
    list_all_movies,
    list_all_genres,
    search_movies_based_genres,
    display_movie_metadata,
)
from functions.content_filtering_methods import plot_embedding_similarity_genre
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
st.title("Movie Recommendations Content-Based Filtering (Plot Embeddings)")

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
            # st.write("Recommendations will be displayed here")
            # get list of ids for each movie
            movie_ids = []
            for movie in selected_movies:
                movie_id = all_movies[all_movies["Movie.title"] == movie][
                    "MovieID"
                ].values[0]
                movie_ids.append(movie_id)
                # print(movie_id)

            movie_recs = {}

            for movie_id in movie_ids:
                # get the recommendations for each movie
                movie_recs[movie_id] = plot_embedding_similarity_genre(movie_id)

            # movie_recs is a dictionary of dictionaries, each dictionary contains 'source_id', 'source', 'target_id', 'target', 'similarity'
            # we want to show the target movie and the node's properties, plus the similarity score
            # do not need to show the source_id and source properties
            movie_recs_df = pd.DataFrame()
            for key, value in movie_recs.items():
                movie_rec_df = pd.json_normalize(value)
                # st.write(movie_rec_df)
                # # drop all columns containing the word source
                # movie_rec_df = movie_rec_df[
                #     movie_rec_df.columns.drop(list(movie_rec_df.filter(regex="source")))
                # ]
                movie_recs_df = pd.concat(
                    [movie_recs_df, movie_rec_df], axis=0, ignore_index=True
                )
            movie_recs_df = movie_recs_df.sort_values(
                by=["similarity"], ascending=False
            )
            movie_recs_df = movie_recs_df.drop(columns=["target_id"])
            st.success("Recommendations based on selected movies")

            # get the unique source_id and titles
            source_id_title_unique = movie_recs_df[
                ["source_id", "source.title"]
            ].drop_duplicates()
            # save to a dict
            source_id_title_dict = dict(
                zip(
                    source_id_title_unique["source_id"],
                    source_id_title_unique["source.title"],
                )
            )

            # for each source_id, find all rows that have the same source_id and display the recommendations in the descending order of the similarity score
            for source_id, group in movie_recs_df.groupby("source_id"):
                # display the title of the source movie in bold header
                st.header(f"Recommendations for {source_id_title_dict[source_id]}")
                # drop all columns containing the word source
                group = group[group.columns.drop(list(group.filter(regex="source")))]
                # display the title, movie poster, and plot of the movie first, then display the rest of the metadata in a dataframe
                for index, row in group.iterrows():
                    # st.write(row)
                    st.write(row["target.title"])
                    st.markdown(
                        f"![{row['target.title']}](https://image.tmdb.org/t/p/w500{row['target.poster']})"
                    )
                    st.write(f"Plot: {row['target.plot']}")
                    # for each row, remove the plotembedding, posterembedding, tmdbId, movieid, plot, and poster
                    row = row.drop(
                        [
                            "target.plot",
                            "target.poster",
                            "target.plotEmbedding",
                            "target.posterEmbedding",
                            "target.tmdbId",
                            "target.movieId",
                        ]
                    )
                    # display the row in one row, with the column names as the column headers
                    st.dataframe(
                        row.to_frame().T, use_container_width=True, hide_index=True
                    )

else:
    st.warning("Please select at least one genre to filter movies")
    st.stop()
