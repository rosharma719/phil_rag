import os
import logging
import sys
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Pinecone Config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
PINECONE_INDEX_NAME = "belief-embeddings"

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Logging setup
LOG_FILE = "concept_processing.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)
logger.info("✅ Logging initialized.")

# Load the SAME model used in PostgreSQL embeddings
MODEL_NAME = "BAAI/bge-base-en"  # Ensure consistency in embeddings
model = SentenceTransformer(MODEL_NAME)


def vector_search_beliefs(query_text, top_k=5):
    """
    Searches Pinecone for the closest belief matches to the query text.
    Returns ONLY belief IDs.
    """
    logger.info(f"🔍 Searching for beliefs related to: {query_text}")

    # Generate embedding using the model
    query_embedding = model.encode(query_text).tolist()

    if len(query_embedding) != 768:
        logger.error(f"❌ Query vector is {len(query_embedding)}D but should be 768D!")
        return []

    # Search Pinecone with filter for 'belief' type
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"type": {"$eq": "belief"}}
    )

    belief_ids = [match["id"] for match in results.get("matches", [])]

    if belief_ids:
        logger.info(f"✅ Found {len(belief_ids)} belief matches.")
    else:
        logger.info("❌ No belief matches found.")

    return belief_ids


def vector_search_concepts(query_text, top_k=5):
    """
    Searches Pinecone for the closest concept or overloaded concept matches to the query text.
    Returns ONLY concept or overloaded concept IDs.
    """
    logger.info(f"🔍 Searching for concepts related to: {query_text}")

    query_embedding = model.encode(query_text).tolist()

    if len(query_embedding) != 768:
        logger.error(f"❌ Query vector is {len(query_embedding)}D but should be 768D!")
        return []

    # Search Pinecone with filter for concepts and overloaded concepts
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"type": {"$in": ["concept", "overloaded_concept"]}}
    )

    concept_ids = [match["id"] for match in results.get("matches", [])]

    if concept_ids:
        logger.info(f"✅ Found {len(concept_ids)} concept matches.")
    else:
        logger.info("❌ No concept matches found.")

    return concept_ids


def vector_search_all(query_text, top_k=5):
    """
    Searches Pinecone for the closest matches to the query text across ALL types (beliefs, concepts, overloaded concepts).
    Returns a dictionary containing lists of IDs.
    """
    logger.info(f"🔍 Searching across ALL types for: {query_text}")

    query_embedding = model.encode(query_text).tolist()

    if len(query_embedding) != 768:
        logger.error(f"❌ Query vector is {len(query_embedding)}D but should be 768D!")
        return {"beliefs": [], "concepts": []}

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    beliefs = []
    concepts = []

    for match in results.get("matches", []):
        match_type = match.get("metadata", {}).get("type", "unknown")
        if match_type == "belief":
            beliefs.append(match["id"])
        elif match_type in ["concept", "overloaded_concept"]:
            concepts.append(match["id"])

    if beliefs or concepts:
        logger.info(f"✅ Found {len(beliefs)} beliefs and {len(concepts)} concepts.")
    else:
        logger.info("❌ No matches found.")

    return {"beliefs": beliefs, "concepts": concepts}


def print_metadata(item_id):
    """
    Retrieves metadata from Pinecone for a given ID and logs it.
    """
    logger.info(f"🔍 Retrieving metadata for ID: {item_id}")

    # Query Pinecone for the specific ID
    result = index.fetch(ids=[item_id])

    # Access metadata correctly
    if result and item_id in result.vectors:
        metadata = result.vectors[item_id].metadata
        logger.info(f"\n📌 Metadata for {item_id}:")
        for key, value in metadata.items():
            logger.info(f"   ➤ {key}: {value}")
    else:
        logger.info(f"❌ No metadata found for ID: {item_id}")

def get_metadata(item_id):
    """
    Retrieves metadata from Pinecone for a given ID and returns it as a dictionary.
    """
    logger.info(f"🔍 Retrieving metadata for ID: {item_id}")

    # Query Pinecone for the specific ID
    result = index.fetch(ids=[item_id])

    # Access metadata correctly
    if result and item_id in result.vectors:
        return result.vectors[item_id].metadata
    else:
        logger.info(f"❌ No metadata found for ID: {item_id}")
        return None
