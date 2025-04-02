from LLM_querying.DB_operations.pinecone_operations import vector_search_all, get_metadata, vector_search_beliefs, vector_search_concepts
from LLM_querying.DB_operations.neon_operations import get_content, get_title, get_section, get_mistral_output,get_beliefs_in_document, get_concepts_in_document, get_associated_thinkers, get_associated_eras
from LLM_querying.DB_operations.neo4j_operations import get_nearest_concept, get_shortest_path, get_nearest_belief, get_nodes_within_distance


def search_beliefs(query, top_k=5):
    return vector_search_beliefs(query, top_k=top_k)


def search_concepts(query, top_k=5):
    return vector_search_concepts(query, top_k=top_k)


def get_belief_content(belief_id):
    metadata = get_metadata(belief_id)
    sep_id = metadata.get("sep_id") if metadata else None
    if sep_id:
        title = get_title(sep_id) or "Untitled"
        content = get_content(sep_id)
        if content:
            return f"[SEP {sep_id} - {title}]\n{content[:600]}"
    return None


def get_document_metadata(belief_id):
    metadata = get_metadata(belief_id)
    sep_id = metadata.get("sep_id") if metadata else None
    if not sep_id:
        return {}
    return {
        "title": get_title(sep_id),
        "section": get_section(sep_id),
        "content": get_content(sep_id),
        "mistral_output": get_mistral_output(sep_id)
    }


def get_related_beliefs(belief_id):
    return get_beliefs_in_document(belief_id)


def get_related_concepts(belief_id):
    return get_concepts_in_document(belief_id)


def get_associated_thinkers_from_belief(belief_id):
    return get_associated_thinkers(belief_id)


def get_associated_eras_from_belief(belief_id):
    return get_associated_eras(belief_id)


def expand_concepts(concept_id, top_k=5):
    return get_nearest_concept(concept_id, top_k=top_k)


def expand_beliefs(belief_id, top_k=5):
    return get_nearest_belief(belief_id, top_k=top_k)


def get_concept_path(concept1_id, concept2_id):
    return get_shortest_path(concept1_id, concept2_id)


def get_neighbors_within_distance(node_id, distance):
    return get_nodes_within_distance(node_id, distance)
