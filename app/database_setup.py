import sqlite3
import os

# Get the absolute path to the current directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'jobportal.db')

# Connect to SQLite database (it will create it if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create the 'users' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'job_seeker'
    )
''')

# Commit and close the connection
conn.commit()
conn.close()

print(f"Database created successfully at: {DB_PATH}")
print("Users table created or already exists.")
