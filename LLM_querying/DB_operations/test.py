from neon_operations import *
from pinecone_operations import *
from neo4j_operations import *


ids = vector_search_beliefs("keynesian economics")
for id in ids:
    print(get_metadata(id))

