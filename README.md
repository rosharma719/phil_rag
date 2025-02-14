## **To Navaneeth "Savant" Unnikrishnan**
- Be careful about overwriting the database. The scripts don't have built-in checks for that, so uhhh just don't.
- Ensure document modification scripts resume correctly instead of starting from scratch.
- Otherwise, do your thing. Run wild. <3

---

# **Running the Project with Docker**

## **🚀 Starting the Containers**
To launch the project and run everything in the background:

docker-compose up -d

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