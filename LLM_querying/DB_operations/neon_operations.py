import os
import psycopg2
import logging
from dotenv import load_dotenv
from pinecone_operations import get_metadata  # Import Pinecone operations

# Load environment variables
load_dotenv()

# Get Neon PostgreSQL URL
DATABASE_URL = os.getenv("NEON_URL")

# Ensure the URL is set
if not DATABASE_URL:
    raise ValueError("NEON_URL is not set in environment variables")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Establish database connection
def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


### **🔍 Generic Document Metadata Retrieval Methods**
def get_mistral_output(sep_id):
    """Retrieves the full `mistral_output` JSON for a given `sep_id`."""
    query = "SELECT mistral_output FROM sep_embeddings WHERE id = %s"

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (sep_id,))
        result = cur.fetchone()
    
    return result[0] if result else None


def get_title(sep_id):
    """Retrieves the title of the document for a given `sep_id`."""
    query = "SELECT title FROM sep_embeddings WHERE id = %s"

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (sep_id,))
        result = cur.fetchone()

    return result[0] if result else None


def get_section(sep_id):
    """Retrieves the section name of the document for a given `sep_id`."""
    query = "SELECT section FROM sep_embeddings WHERE id = %s"

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (sep_id,))
        result = cur.fetchone()

    return result[0] if result else None


def get_content(sep_id):
    """Retrieves the main content of the document for a given `sep_id`."""
    query = "SELECT content FROM sep_embeddings WHERE id = %s"

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (sep_id,))
        result = cur.fetchone()

    return result[0] if result else None


### **🔍 Belief & Concept Retrieval Methods Using Pinecone**
def get_beliefs_in_document(belief_id):
    """
    Given a belief ID, fetches the SEP ID from Pinecone metadata and retrieves associated beliefs.
    """
    # **Step 1: Fetch `sep_id` from Pinecone**
    metadata = get_metadata(belief_id)
    if not metadata or "sep_id" not in metadata:
        logger.error(f"❌ No SEP ID found for belief {belief_id}")
        return []

    sep_id = metadata["sep_id"]

    # **Step 2: Retrieve `mistral_output` JSON from Neon**
    mistral_json = get_mistral_output(sep_id)
    if not mistral_json:
        logger.error(f"❌ No document found for SEP ID {sep_id}")
        return []

    # **Step 3: Extract Beliefs from JSON**
    if "key_beliefs" in mistral_json:
        beliefs = [belief["belief"] for belief in mistral_json["key_beliefs"]]
        return beliefs

    logger.info(f"🔍 No beliefs found in document {sep_id}")
    return []


def get_concepts_in_document(belief_id):
    """
    Given a belief ID, fetches the SEP ID from Pinecone metadata and retrieves associated concepts.
    """
    # **Step 1: Fetch `sep_id` from Pinecone**
    metadata = get_metadata(belief_id)
    if not metadata or "sep_id" not in metadata:
        logger.error(f"❌ No SEP ID found for belief {belief_id}")
        return []

    sep_id = metadata["sep_id"]

    # **Step 2: Retrieve `mistral_output` JSON from Neon**
    mistral_json = get_mistral_output(sep_id)
    if not mistral_json:
        logger.error(f"❌ No document found for SEP ID {sep_id}")
        return []

    # **Step 3: Extract Concepts from JSON**
    if "key_concepts" in mistral_json:
        concepts = [concept["name"] for concept in mistral_json["key_concepts"]]
        return concepts

    logger.info(f"🔍 No concepts found in document {sep_id}")
    return []


def get_associated_thinkers(belief_id):
    """
    Given a belief ID, fetches the SEP ID from Pinecone metadata and retrieves associated thinkers.
    """
    # **Step 1: Fetch `sep_id` from Pinecone**
    metadata = get_metadata(belief_id)
    if not metadata or "sep_id" not in metadata:
        logger.error(f"❌ No SEP ID found for belief {belief_id}")
        return []

    sep_id = metadata["sep_id"]

    # **Step 2: Retrieve `mistral_output` JSON from Neon**
    mistral_json = get_mistral_output(sep_id)
    if not mistral_json:
        logger.error(f"❌ No document found for SEP ID {sep_id}")
        return []

    # **Step 3: Extract Thinkers from JSON**
    if "associated_thinkers" in mistral_json:
        return mistral_json["associated_thinkers"]

    logger.info(f"🔍 No associated thinkers found in document {sep_id}")
    return []


def get_associated_eras(belief_id):
    """
    Given a belief ID, fetches the SEP ID from Pinecone metadata and retrieves associated eras.
    """
    # **Step 1: Fetch `sep_id` from Pinecone**
    metadata = get_metadata(belief_id)
    if not metadata or "sep_id" not in metadata:
        logger.error(f"❌ No SEP ID found for belief {belief_id}")
        return []

    sep_id = metadata["sep_id"]

    # **Step 2: Retrieve `mistral_output` JSON from Neon**
    mistral_json = get_mistral_output(sep_id)
    if not mistral_json:
        logger.error(f"❌ No document found for SEP ID {sep_id}")
        return []

    # **Step 3: Extract Eras from JSON**
    if "associated_eras" in mistral_json:
        return mistral_json["associated_eras"]

    logger.info(f"🔍 No associated eras found in document {sep_id}")
    return []
