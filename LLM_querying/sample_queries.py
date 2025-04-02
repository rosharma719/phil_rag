from LLM_querying.DB_operations.pinecone_operations import *

ids = vector_search_beliefs("Marxism and blockchain")
for id in ids:
    print(get_metadata(id))

