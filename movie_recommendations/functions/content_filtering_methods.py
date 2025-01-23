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


def plot_embedding_similarity_genre(id):
    """
    Leveraging plot embeddings to find similar movies in the same genre, ranking using cosine similarity score
    Uses the moviePlots index to find similar movies
    """
    query = """
    MATCH (source:Movie)
    WHERE elementId(source) = $id
    WITH source, source.plotEmbedding AS sourceVec
    MATCH (target:Movie)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(source)
    WHERE target.plotEmbedding IS NOT NULL
    WITH source, target, g, gds.similarity.cosine(sourceVec, target.plotEmbedding) AS similarity
    RETURN DISTINCT elementId(source) as source_id, source, elementId(target) as target_id, target, similarity
    ORDER BY similarity DESC
    LIMIT 5
    """
    result = run_cypher(NEO4J_DRIVER, query, {"id": id})
    return result
