import pandas as pd
import sqlite3
import os
from database import create_table, get_db_connection

EXCEL_FILE = "excel_file.xlsx"
DB_NAME = "library.db"

# Mapping from Excel headers to DB columns
# Adjust 'possible_names' lists based on your actual Excel file
COLUMN_MAPPING = {
    'title': ['Titolo', 'Title', 'Nome'],
    'author': ['Autore', 'Author', 'Scrittore'],
    'genre': ['Genere', 'Genre', 'Categoria'],
    'year': ['Anno', 'Year', 'Anno Pubblicazione'],
    'publisher': ['Editore', 'Publisher', 'Casa Editrice'],
    'location': ['Posizione', 'Location', 'Scaffale', 'Collocazione'],
    # 'language' and 'is_loaned' are new, so we won't look for them in Excel usually,
    # unless they already exist.
}

def import_data():
    if not os.path.exists(EXCEL_FILE):
        print(f"Errore: File '{EXCEL_FILE}' non trovato.")
        return

    print("Lettura file Excel...")
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"Errore lettura Excel: {e}")
        return

    print(f"Colonne trovate: {df.columns.tolist()}")

    # Normalize columns
    df_clean = pd.DataFrame()

    for db_col, possible_names in COLUMN_MAPPING.items():
        found = False
        for name in possible_names:
            # Case insensitive search
            match = next((col for col in df.columns if col.lower() == name.lower()), None)
            if match:
                df_clean[db_col] = df[match]
                found = True
                print(f"Mappato '{match}' -> '{db_col}'")
                break
        
        if not found:
            print(f"Attenzione: Colonna per '{db_col}' non trovata. Sarà vuota.")
            df_clean[db_col] = None

    # Handle new columns
    # Language: default empty or 'Italiano'? User didn't specify default, leave None or ask?
    # Let's set default language to 'Italiano' if missing, just a guess, or empty string.
    if 'language' not in df_clean.columns:
         df_clean['language'] = 'Italiano' # Default assumption
    
    # is_loaned: default 0
    df_clean['is_loaned'] = 0

    # Ensure table exists
    create_table()

    # Insert into DB
    conn = get_db_connection()
    
    # Convert DataFrame to list of tuples for sqlite3
    # Schema: title, author, genre, year, publisher, location, language, is_loaned
    # Ensure order matches
    
    records = df_clean[['title', 'author', 'genre', 'year', 'publisher', 'location', 'language', 'is_loaned']].values.tolist()
    
    print(f"Importazione di {len(records)} libri...")
    
    c = conn.cursor()
    c.executemany('''
        INSERT INTO books (title, author, genre, year, publisher, location, language, is_loaned)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    
    conn.commit()
    conn.close()
    print("Importazione completata con successo!")

if __name__ == "__main__":
    import_data()
