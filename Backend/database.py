import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import closing

# Database connection parameters
DB_PARAMS = {
    "dbname": "box_labels_db",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

# Function to establish a database connection
def get_db_connection():
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)

# Function to ensure the table exists
def initialize_db():
    with closing(get_db_connection()) as conn:
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS generated_pdfs (
                id SERIAL PRIMARY KEY,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )''')
            conn.commit()

# Initialize the database on startup
initialize_db()
