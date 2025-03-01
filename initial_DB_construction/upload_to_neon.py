import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Neon PostgreSQL URL from environment variable
DATABASE_URL = os.getenv("NEON_URL")

# Ensure the URL is set
if not DATABASE_URL:
    raise ValueError("NEON_URL is not set in environment variables")

# Connect to Neon PostgreSQL
def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Run a test query to check DB version
def check_db_version():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT version();")
        print("PostgreSQL Version:", cur.fetchone()[0])

# Monitor database storage usage
def check_db_size():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
        print("Database Size:", cur.fetchone()[0])

# Bulk insert using batch processing
def batch_insert(table_name, columns, data, batch_size=10000):
    """
    Inserts data into a table in batches.
    
    Args:
        table_name (str): Name of the table.
        columns (tuple): Column names (e.g., ("col1", "col2")).
        data (list of tuples): Data to insert.
        batch_size (int): Number of rows per batch (default: 10,000).
    """
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"

    with get_connection() as conn, conn.cursor() as cur:
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            execute_values(cur, query, batch)
            conn.commit()
            print(f"Inserted batch {i // batch_size + 1} of {len(data) // batch_size + 1}")

if __name__ == "__main__":
    check_db_version()
    check_db_size()

    # Example data insert (uncomment & customize as needed)
    # sample_data = [("value1", "value2"), ("value3", "value4"), ...]
    # batch_insert("your_table_name", ("col1", "col2"), sample_data)
