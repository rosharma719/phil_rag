# **Philosophy RAG!**

A structured way to explore philosophy by mapping the logical and semantic connections between ideas. Users enter ideas they want to explore more, and the system cross-references them to synthesize insights and suggest related ideas to prompt further discussion. 

I wanted to build this project to explore how we can improve multi-step LLM processes by searching pre-established knowledge bases.

I first scraped the Stanford Encyclopedia of Philosophy for the full text, then used Mistral to decompose each body of text into "beliefs" and "concepts". I then uploaded the vectors to Pinecone for efficient search, and Neo4j for graph-based storage and traversal. I then built a hybrid query engine, which would recursively use HyDE, vector search, then graph search to find the most relevant information, and then a series of Mistral calls to synthesize it and prompt further questions. 

I wrote this in Python 3.12.2 because psycopg2 doesn't support 3.13 yet, and this project uses it for Neon access. This project uses Neon for full-document storage, Pinecone for vector search, and Neo4j for graph traversal and relationship storage.


To run: 

python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt

