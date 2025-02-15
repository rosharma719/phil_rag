import os
import time
import json
import psycopg2
import requests
import threading
from queue import Queue, Empty
from tqdm import tqdm

# ✅ PostgreSQL Connection
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user="rohansharma",
    password=os.getenv("POSTGRES_PASSWORD"),
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

BATCH_SIZE = 10  # Upload every 10 processed entries
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MAX_CONCURRENT_REQUESTS = 5  # 🚀 Limit on simultaneous requests

# ✅ Fetch unprocessed rows
cursor.execute("SELECT id, content FROM sep_embeddings WHERE mistral_output IS NULL ORDER BY id;")
rows = cursor.fetchall()
total_entries = len(rows)

# ✅ Initialize Progress Bar
progress_bar = tqdm(total=total_entries, desc="🔄 Starting...", unit="entry", dynamic_ncols=True)

# ✅ Queues for request management
request_queue = Queue()
response_queue = Queue()
pending_requests = {}  # 🚀 Track oldest unfulfilled request


def call_mistral_api(entry_id, content):
    """ Sends an API request and returns the response """
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": "Extract structured philosophical knowledge. Your response should always be a single valid JSON object."},
        {"role": "user", "content": f"""
        You are an AI tasked with extracting structured philosophical knowledge from a given text.
        Your goal is to **categorize the entry and extract key information in a structured format.**  
        Be **as detailed as possible while remaining concise.**  
        **Always return a single JSON object, never multiple JSON objects.**

        ## **Input:**
        {content}

        ## **Output Format (JSON):**
        {{
            "category": "thinker" | "concept" | "era",
            "metadata": {{
                "name": "...", 
                "description": "...",
                "time_period": "..."  
            }},
            "key_beliefs": [  
                {{ "belief": "...", "justification": "...", "related_concepts": ["...", "..."] }}
            ],
            "key_concepts": [  
                {{ "name": "...", "definition": "...", "related_fields": ["...", "..."] }}
            ],
            "associated_thinkers": ["...", "..."],
            "associated_eras": ["...", "..."]
        }}
        **Never return multiple JSON objects.**
        """}
    ]

    data = {
        "model": "mistral-medium-2312",
        "messages": messages,
        "temperature": 0.4
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"\n❌ API request failed for entry ID {entry_id}: {response.status_code} {response.text}")

    try:
        parsed_response = response.json()
        return entry_id, json.loads(parsed_response["choices"][0]["message"]["content"])  # ✅ Ensure Valid JSON
    except json.JSONDecodeError:
        raise Exception(f"\n❌ Failed to parse API response for entry ID {entry_id}.")


def send_requests():
    """ Enqueues API requests at a controlled rate. """
    for i, (entry_id, content) in enumerate(rows, start=1):
        request_queue.put((entry_id, content))
        pending_requests[entry_id] = i  # ✅ Track this request as pending
        time.sleep(2)  # ✅ Maintain rate limit


def api_worker():
    """ Worker that fetches requests from the queue, calls the API, and puts results into the response queue. """
    while True:
        try:
            entry_id, content = request_queue.get(timeout=10)
            response = call_mistral_api(entry_id, content)
            response_queue.put(response)
            request_queue.task_done()  # ✅ Mark request as processed

        except Empty:
            break  # ✅ Exit if there are no more requests


def process_responses():
    """ Processes API responses and updates the database. """
    batch_updates = []
    
    while True:
        try:
            entry_id, mistral_output_json = response_queue.get(timeout=10)  # ✅ Wait for a response
            batch_updates.append((json.dumps(mistral_output_json), entry_id))
            progress_bar.update(1)

            # ✅ Remove from pending requests
            if entry_id in pending_requests:
                del pending_requests[entry_id]

            # ✅ Track the oldest unfulfilled request
            oldest_unfulfilled = min(pending_requests.values(), default="None")
            progress_bar.set_description(f"🔄 Oldest unfulfilled: Entry {oldest_unfulfilled}/{total_entries}")

            # ✅ Upload batch every 10 responses
            if len(batch_updates) >= BATCH_SIZE:
                cursor.executemany("""
                    UPDATE sep_embeddings 
                    SET mistral_output = %s 
                    WHERE id = %s;
                """, batch_updates)
                conn.commit()
                batch_updates = []  # ✅ Reset batch
                tqdm.write(f"\r✅ Uploaded {BATCH_SIZE} entries to the database.", end="")

        except Empty:
            if request_queue.empty() and response_queue.empty():
                break  # ✅ Stop if everything is processed

    # ✅ Upload remaining entries
    if batch_updates:
        cursor.executemany("""
            UPDATE sep_embeddings 
            SET mistral_output = %s 
            WHERE id = %s;
        """, batch_updates)
        conn.commit()
        tqdm.write("\r✅ Final batch uploaded successfully.", end="")

    progress_bar.close()
    print("\n🎉 Processing complete!")
    cursor.close()
    conn.close()


# ✅ Start threads
request_thread = threading.Thread(target=send_requests)
api_threads = [threading.Thread(target=api_worker) for _ in range(MAX_CONCURRENT_REQUESTS)]
response_thread = threading.Thread(target=process_responses)

# ✅ Start threads
request_thread.start()
for thread in api_threads:
    thread.start()
response_thread.start()

# ✅ Join threads
request_thread.join()
for thread in api_threads:
    thread.join()
response_thread.join()
