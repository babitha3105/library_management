import sqlite3

conn = sqlite3.connect("library.db")

cur = conn.cursor()

# books table
cur.execute("""
CREATE TABLE IF NOT EXISTS books(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER

)
""")

# issued table
cur.execute("""
CREATE TABLE IF NOT EXISTS issued(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_name TEXT NOT NULL,

    book_id INTEGER NOT NULL,

    issue_date DATE,

    return_date DATE,

    FOREIGN KEY(book_id) REFERENCES books(id)

)
""")

conn.commit()
conn.close()

print("Database and tables created")