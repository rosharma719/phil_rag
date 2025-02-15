import os
import json
import psycopg2
import numpy as np
import hashlib
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# PostgreSQL Connection Settings
DB_NAME = "phil_rag"
DB_USER = "rohansharma" 
DB_PASSWORD = "password"  # Ensure it's correct
DB_HOST = "postgres"  # Change to "postgres" if running inside Docker
DB_PORT = "5432"

# Directory containing JSON files
JSON_DIRECTORY = "/Volumes/BigDrive/phil_rag"

# Load Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to PostgreSQL
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cur = conn.cursor()
print("✅ Connected to PostgreSQL")

# Ensure table exists before inserting (prevent errors)
cur.execute("""
    CREATE TABLE IF NOT EXISTS sep_embeddings (
        id SERIAL PRIMARY KEY,
        embedding VECTOR(768),  -- Adjust size if needed
        title TEXT NOT NULL,
        section TEXT NOT NULL,
        content TEXT NOT NULL,
        hash TEXT NOT NULL UNIQUE
    );
""")
conn.commit()

# Get last processed file & section
cur.execute("SELECT title, section FROM sep_embeddings ORDER BY id DESC LIMIT 1;")
last_processed = cur.fetchone()
last_processed_title = last_processed[0] if last_processed else None
last_processed_section = last_processed[1] if last_processed else None

# Delete incomplete data for the last title (ensures clean restart)
if last_processed_title:
    print(f"🗑️ Removing incomplete entries for: {last_processed_title}")
    cur.execute("DELETE FROM sep_embeddings WHERE title = %s;", (last_processed_title,))
    conn.commit()

# Insert function with conflict handling
insert_count = 0
BATCH_SIZE = 100

def insert_into_db(title, section, content, embedding):
    global insert_count
    content_hash = hashlib.md5((title + section + content).encode("utf-8")).hexdigest()

    sql = """
    INSERT INTO sep_embeddings (title, section, content, embedding, hash)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (hash) DO NOTHING;
    """  
    try:
        cur.execute(sql, (title, section, content, embedding, content_hash))
        insert_count += 1

        if insert_count % BATCH_SIZE == 0:
            conn.commit()
            print(f"🔄 Committed {insert_count} inserts so far...")

    except Exception as e:
        print(f"❌ Error inserting {title} - {section}: {e}")

# Get JSON files
json_files = sorted([f for f in os.listdir(JSON_DIRECTORY) if f.endswith(".json")])
total_files = len(json_files)

print(f"📂 Found {total_files} JSON files. Resuming from: {last_processed_title if last_processed_title else 'Start'}")

resume_file = False if last_processed_title else True
resume_section = False if last_processed_section else True

# Process JSON Files
for filename in tqdm(json_files, desc="📊 Processing JSON files", unit="file"):
    file_path = os.path.join(JSON_DIRECTORY, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "Unknown Title")  

    # Skip already processed files
    if not resume_file:
        if title == last_processed_title:
            resume_file = True  # Found last processed file, resume now
        continue  # Skip until we reach the last processed file

    sections = data.get("sections", {})

    print(f"\n📜 Processing Title: {title} with {len(sections)} sections")

    for section_name, section_text in tqdm(sections.items(), desc=f"⚡ Processing Sections ({filename})", leave=False, unit="section"):
        if len(section_text.strip()) > 0:
            if not resume_section:
                if section_name == last_processed_section:
                    resume_section = True
                continue  # Skip until we reach the last processed section
            
            embedding = model.encode(section_text).tolist()
            insert_into_db(title, section_name, section_text, embedding)

# Final commit after last batch
conn.commit()
cur.close()
conn.close()

print(f"🎉 ✅ Vectorization and storage complete! Total inserted: {insert_count}")
