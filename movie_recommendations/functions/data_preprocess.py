import os
from dotenv import load_dotenv
import logging
from functions.connections import NEO4J_DRIVER

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
log_file_path = os.getenv("DATA_PREPARATION_LOG_FILE_PATH", "app.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def pre_created_embeddings_load(force=False):
    """
    Loads embeddings from CSV files into the Neo4j database and creates vector indexes.
    """
    if force is False:
        with NEO4J_DRIVER.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]
            if (
                "personBio" in indexes
                and "moviePlots" in indexes
                and "moviePosters" in indexes
            ):
                logger.info("Embeddings already loaded and indexes created.")
                return True
    queries = {
        "bio_embedding": """
        LOAD CSV WITH HEADERS
        FROM 'https://data.neo4j.com/rec-embed/person-bio-embeddings.csv'
        AS row
        MATCH (p:Person {tmdbId: row.tmdbId})
        CALL db.create.setNodeVectorProperty(p, 'bioEmbedding', apoc.convert.fromJsonList(row.bio_embedding))
        """,
        "plot_embedding": """
        LOAD CSV WITH HEADERS
        FROM 'https://data.neo4j.com/rec-embed/movie-plot-embeddings.csv'
        AS row
        MATCH (m:Movie {movieId: row.movieId})
        CALL db.create.setNodeVectorProperty(m, 'plotEmbedding', apoc.convert.fromJsonList(row.embedding))
        """,
        "poster_embedding": """
        LOAD CSV WITH HEADERS
        FROM "https://data.neo4j.com/rec-embed/movie-poster-embeddings.csv" AS row
        MATCH (m:Movie {movieId: row.movieId})
        CALL db.create.setNodeVectorProperty(m, 'posterEmbedding', apoc.convert.fromJsonList(row.posterEmbedding))
        """,
        "person_bio_index": """
        CREATE VECTOR INDEX personBio IF NOT EXISTS
        FOR (p:Person)
        ON p.bioEmbedding
        OPTIONS {indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
        }}
        """,
        "movie_plot_index": """
        CREATE VECTOR INDEX moviePlots IF NOT EXISTS
        FOR (m:Movie)
        ON m.plotEmbedding
        OPTIONS {indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
        }}
        """,
        "movie_poster_index": """
        CREATE VECTOR INDEX moviePosters IF NOT EXISTS
        FOR (m:Movie)
        ON m.posterEmbedding
        OPTIONS {indexConfig: {
        `vector.dimensions`: 512,
        `vector.similarity_function`: 'cosine'
        }}
        """,
        "cleanup": """
        MATCH (mov:Movie)
        REMOVE mov.embedding;
        """,
    }

    try:
        with NEO4J_DRIVER.session() as session:
            for key, query in queries.items():
                logger.debug(f"Running query: {key}")
                session.run(query)
        logger.info("Embeddings loaded and indexes created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error in pre_created_embeddings_load: {e}")
        return False


def drop_missing():
    """
    Drops nodes that do not have embeddings of the correct dimensions.
    """
    queries = {
        "plot_drop": """
        MATCH (m:Movie)
        WHERE m.plotEmbedding IS NULL OR size(m.plotEmbedding) <> 1536
        DETACH DELETE m
        """,
        "bio_drop": """
        MATCH (p:Person)
        WHERE p.bioEmbedding IS NULL OR size(p.bioEmbedding) <> 1536
        DETACH DELETE p
        """,
        "poster_drop": """
        MATCH (m:Movie)
        WHERE m.posterEmbedding IS NULL OR size(m.posterEmbedding) <> 512
        DETACH DELETE m
        """,
    }

    try:
        with NEO4J_DRIVER.session() as session:
            for key, query in queries.items():
                logger.debug(f"Running query: {key}")
                session.run(query)
        logger.info("Nodes with missing or incorrect embeddings dropped successfully.")
        return True
    except Exception as e:
        logger.error(f"Error in drop_missing: {e}")
        return False
