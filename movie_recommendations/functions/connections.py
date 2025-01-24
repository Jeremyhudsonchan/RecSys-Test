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

log_file_path = os.getenv("CONNECTIONS_LOG_FILE_PATH", "app.log")
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)


# Connect to Neo4j
def connect_to_neo4j():
    try:
        # local
        # uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        # user = os.getenv("NEO4J_USER", "neo4j")
        # password = os.getenv("NEO4J_PASSWORD", "password")

        # deployed
        uri = os.getenv("NEO4j_URI_DPLY", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER_DPLY", "neo4j")
        password = os.getenv("NEO4J_PASSWORD_DPLY", "abcd1234")

        URI = "neo4j+s://f1f706ab.databases.neo4j.io"
        AUTH = (user, password)

        logger.info(f"Connecting to Neo4j at {uri} with user {user}")

        with neo4j.GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()

        # driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        return None


NEO4J_DRIVER = connect_to_neo4j()
