# **Philosophy RAG!**

- Be careful about overwriting the database. The scripts don't have built-in checks for that, so uhhh just don't.
- Ensure document modification scripts resume correctly instead of starting from scratch.
- Otherwise, do your thing. Run wild. <3

---

# **Running the Project with Docker**

## **🚀 Starting the Containers**
To launch the project and run everything in the background:

docker-compose up -d
source /app/venv/bin/activate


## **🛠 Accessing the Databases**

### **PostgreSQL**
To enter the database CLI:

docker exec -it phil_rag_postgres psql -U postgres

### **Neo4j**
To open Cypher shell:

docker exec -it phil_rag_neo4j cypher-shell -u neo4j -p <your-password>

If you forgot the password, check `docker-compose.yml` under `NEO4J_AUTH`.

## **🛑 Stopping Everything**
To stop containers while **keeping database data intact**:

docker-compose down

## **.env file**

POSTGRES_USER=POSTGRES_USER
POSTGRES_PASSWORD=POSTGRES_PASSWORD
POSTGRES_DB=POSTGRES_DB
NEON_URL = NEON_URL

NEO4J_USER=NEO4J_USER
NEO4J_PASSWORD=NEO4J_PASSWORD
MISTRAL_API_KEY=MISTRAL_API_KEY
MISTRAL_API_KEY_2=MISTRAL_API_KEY_2
MISTRAL_API_KEY_3 =MISTRAL_API_KEY_3
