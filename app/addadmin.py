import sqlite3
from werkzeug.security import generate_password_hash

# Adjust path to your database file
DB_PATH = "jobportal.db"  # Use your actual path

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Admin credentials
name = "Admin"
email = "admin@example.com"
password = generate_password_hash("admin123")  # Change password if needed
role = "admin"

# Insert admin
cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", (name, email, password, role))

conn.commit()
conn.close()

print("Admin user added.")
