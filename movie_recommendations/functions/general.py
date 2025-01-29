from functions.connections import NEO4J_DRIVER
from functions.helper_functions.cypher import run_cypher
import os
from dotenv import load_dotenv

print(load_dotenv(".env"))

import logging

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

log_file_path = os.getenv("GENERAL_QUERY_LOG_FILE_PATH", "app.log")
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)


def list_all_genres():
    """
    Listing all genres in the database
    """
    query = """
    MATCH (g:Genre)
    RETURN PROPERTIES(g) as Genre, elementID(g) as GenreID
    ORDER BY Genre.name
    """
    parameters = {}
    data = run_cypher(NEO4J_DRIVER, query, parameters)
    return data


def list_all_movies():
    """
    Listing all movies in the database
    """
    query = """
    MATCH (m:Movie)
    RETURN apoc.map.removeKeys(m, ["plotEmbedding", "posterEmbedding", "tmdbId", "movieId", "countries", "budget", "revenue"]) as Movie, elementID(m) as MovieID, ID(m) as MovieNeo4jID
    ORDER BY m.title, m.released
    """
    parameters = {}
    data = run_cypher(NEO4J_DRIVER, query, parameters)
    return data


def search_movies_based_genres(genres):
    """
    Listing all movies based on genres
    """
    logger.debug(f"Searching Movies based on Genres: {genres}")
    query = """
    MATCH (m:Movie)-[:IN_GENRE]->(g:Genre)
    WHERE g.name IN $genres
    RETURN apoc.map.removeKeys(m, ["plotEmbedding", "posterEmbedding", "tmdbId", "movieId", "countries", "budget", "revenue"]) as Movie, elementID(m) as MovieID, ID(m) as MovieNeo4jID, g.name as Genre, elementID(g) as GenreID, ID(g) as GenreNeo4jID
    ORDER BY m.title, m.released
    """
    parameters = {"genres": genres}
    data = run_cypher(NEO4J_DRIVER, query, parameters)
    logger.info("Search Movies based on Genres Completed")
    # logger.debug(f"Results from the query based on genres: {data}")
    return data


def display_movie_metadata(movie_id):
    logger.debug(f"Displaying Movie Metadata for Movie ID: {movie_id}")
    query = """
    MATCH (m:Movie)-[IN_GENRE]->(g:Genre)
    WHERE elementID(m) = $movie_id
    RETURN apoc.map.removeKeys(m, ["plotEmbedding", "posterEmbedding", "tmdbId", "movieId", "countries", "budget", "revenue"]) as Movie, elementID(m) as MovieID, ID(m) as MovieNeo4jID, g.name as Genre, elementID(g) as GenreID, ID(g) as GenreNeo4jID
    """
    parameters = {"movie_id": movie_id}
    data = run_cypher(NEO4J_DRIVER, query, parameters)
    logger.info("Displaying Movie Metadata Completed")
    # logger.debug(f"Results from the query of movie metadata: {data}")
    return data
