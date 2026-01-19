import sqlite3
import os

DB_NAME = "library.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            genre TEXT,
            year INTEGER,
            publisher TEXT,
            location TEXT,
            language TEXT,
            is_loaned INTEGER DEFAULT 0,
            loaned_to TEXT
        )
    ''')
    # Migration for existing DBs
    try:
        c.execute('ALTER TABLE books ADD COLUMN loaned_to TEXT')
    except sqlite3.OperationalError:
        pass # Column already exists
    
    conn.commit()
    conn.close()

def add_book(title, author, genre, year, publisher, location, language, is_loaned=0, loaned_to=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO books (title, author, genre, year, publisher, location, language, is_loaned, loaned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, genre, year, publisher, location, language, is_loaned, loaned_to))
    conn.commit()
    conn.close()

def get_all_books(limit=50, offset=0):
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY title COLLATE NOCASE LIMIT ? OFFSET ?', (limit, offset)).fetchall()
    conn.close()
    return books

def search_books(query, limit=50, offset=0):
    conn = get_db_connection()
    query_param = f"%{query}%"
    books = conn.execute('''
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR publisher LIKE ?
        ORDER BY title COLLATE NOCASE
        LIMIT ? OFFSET ?
    ''', (query_param, query_param, query_param, query_param, limit, offset)).fetchall()
    conn.close()
    return books

def update_book(book_id, title, author, genre, year, publisher, location, language, is_loaned, loaned_to=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE books 
        SET title = ?, author = ?, genre = ?, year = ?, publisher = ?, location = ?, language = ?, is_loaned = ?, loaned_to = ?
        WHERE id = ?
    ''', (title, author, genre, year, publisher, location, language, is_loaned, loaned_to, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

def toggle_loan_status(book_id, current_status, loaned_to=None):
    new_status = 0 if current_status == 1 else 1
    if new_status == 0:
        loaned_to = None # Clear when returned
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE books SET is_loaned = ?, loaned_to = ? WHERE id = ?', (new_status, loaned_to, book_id))
    conn.commit()
    conn.close()
    return new_status

def get_unique_values(column_name):
    """Returns a list of unique values for a given column, used for autocomplete."""
    valid_columns = ["author", "genre", "publisher", "location", "language"]
    if column_name not in valid_columns:
        return []
    
    conn = get_db_connection()
    # Using ORDER BY for better UI presentation
    rows = conn.execute(f'SELECT DISTINCT {column_name} FROM books WHERE {column_name} IS NOT NULL AND {column_name} != "" ORDER BY {column_name} COLLATE NOCASE').fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_all_books_sorted():
    """Returns all books sorted by title for export."""
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY title COLLATE NOCASE').fetchall()
    conn.close()
    return [dict(b) for b in books]

# Initialize DB on import
create_table()
