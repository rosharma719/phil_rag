# **Philosophy RAG!**

A structured way to explore philosophy by mapping the logical and semantic connections between ideas. Users enter ideas they want to explore more, and the system cross-references them to synthesize insights and suggest related ideas to prompt further discussion. Over time, this builds an interactive belief graph, enabling deeper philosophical exploration.

I wrote this in Python 3.12.2 because psycopg2 doesn't support 3.13 yet, and this project uses it for Neon access. 

This project uses Neon for full-document storage, Pinecone for vector search, and Neo4j for graph traversal and relationship storage.


To run: 

python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt

