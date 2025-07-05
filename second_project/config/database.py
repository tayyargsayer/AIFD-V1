import sqlite3
from horror_story_app.config import settings

def get_db_connection():
    """
    Establishes a connection to the SQLite database.

    The connection object is configured to return rows that behave like dictionaries,
    which makes accessing columns by name easier.

    Returns:
        sqlite3.Connection: A connection object to the database.
    
    Raises:
        sqlite3.Error: If a connection to the database cannot be established.
    """
    try:
        # The DATABASE_URL is expected to be in the format "sqlite:///path/to/db.file"
        # We need to strip the "sqlite:///" prefix to get the raw file path.
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        # Depending on the application's needs, you might want to handle this more gracefully
        # or re-raise the exception to be caught by a higher-level handler.
        raise

# Example of how to use it (optional, for testing)
if __name__ == '__main__':
    try:
        print("Attempting to connect to the database...")
        connection = get_db_connection()
        print("Database connection successful.")
        
        # You can perform a simple query to test
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in the database:", [table['name'] for table in tables])
        
        connection.close()
    except Exception as e:
        print(f"Failed to connect or query the database. Error: {e}") 