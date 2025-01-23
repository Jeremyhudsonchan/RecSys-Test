from functions.connections import NEO4J_DRIVER
from functions.helper_functions.cypher import run_cypher
import os
from dotenv import load_dotenv
import neo4j

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

log_file_path = os.getenv("CONTENT_FILTERING_QUERY_LOG_FILE_PATH", "app.log")
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)


def movie_user_recommendations_singular(id, rating):
    """
    id: movie node id
    Idea is, if a user has rated a movie highly (5.0), then find similar users who have rated the same movie highly, and recommend movies that they have rated highly
    If a user has rated a movie poorly (0.5), then find similar users who have rated the same movie poorly, and recommend movies that they have rated highly
    """
    query = """
    MATCH (m:Movie)
    WHERE elementId(m) = $id
    WITH m
    MATCH (m)<-[r:RATED]-(u:User)
    WHERE r.rating = $rating
    WITH DISTINCT u
    MATCH (u)-[r:RATED]->(rec:Movie)
    WHERE r.rating = 5.0
    WITH DISTINCT rec, COUNT(u) AS user_count
    RETURN elementID(rec) as rec_id, rec as recommendation, user_count
    ORDER BY rec.imdbVotes DESC LIMIT 5
    """
    result = run_cypher(NEO4J_DRIVER, query, {"id": id, "rating": rating})
    return result
