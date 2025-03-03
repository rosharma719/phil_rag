import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

# Neo4j Config
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize Neo4j Driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.info("✅ Neo4j Driver initialized.")

### ✅ Get Nearest Concepts (Includes Overloaded Concepts)
def get_nearest_concept(concept_id, top_k=5):
    """
    Finds the nearest `top_k` concepts or overloaded concepts to a given concept ID.
    Returns a list of concept IDs.
    """
    query = """
    MATCH (c:Concept {id: $concept_id})-[:SIMILAR_TO]-(related)
    WHERE related.type IN ['concept', 'overloaded_concept']
    RETURN related.id AS id
    LIMIT $top_k
    """
    with driver.session() as session:
        results = session.run(query, concept_id=concept_id, top_k=top_k)
        return [record["id"] for record in results]

### ✅ Get Nearest Beliefs
def get_nearest_belief(belief_id, top_k=5):
    """
    Finds the nearest `top_k` beliefs to a given belief ID.
    Returns a list of belief IDs.
    """
    query = """
    MATCH (b:Belief {id: $belief_id})-[:SIMILAR_TO]-(related:Belief)
    RETURN related.id AS id
    LIMIT $top_k
    """
    with driver.session() as session:
        results = session.run(query, belief_id=belief_id, top_k=top_k)
        return [record["id"] for record in results]

### ✅ Get Shortest Path Between Two Nodes
def get_shortest_path(node1_id, node2_id):
    """
    Finds the shortest path (using `SIMILAR_TO`) between two nodes.
    Returns a list of node IDs along the path.
    """
    query = """
    MATCH (start {id: $node1_id}), (end {id: $node2_id}),
    p = shortestPath((start)-[:SIMILAR_TO*]-(end))
    RETURN [node in nodes(p) | node.id] AS path_ids
    """
    with driver.session() as session:
        result = session.run(query, node1_id=node1_id, node2_id=node2_id)
        return result.single()["path_ids"] if result.peek() else []

### ✅ Get All Nodes Within a Certain Distance
def get_nodes_within_distance(node_id, distance):
    """
    Finds all nodes within `distance` edges from the given node.
    Returns a list of node IDs.
    """
    query = f"""
    MATCH (n {{id: $node_id}})-[:SIMILAR_TO*1..{distance}]-(related)
    RETURN DISTINCT related.id AS id
    """
    with driver.session() as session:
        results = session.run(query, node_id=node_id)
        return [record["id"] for record in results]
