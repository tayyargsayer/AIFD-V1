import sqlite3
import os

def get_db_path():
    # Go up one level from /models to the horror_story_app directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', 'stories.db')

def create_tables():
    """Creates the necessary tables in the SQLite database."""
    db_path = get_db_path()
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL statement for creating the 'users' table
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # SQL statement for creating the 'stories' table
    create_stories_table = """
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        user_request TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """

    try:
        cursor.execute(create_users_table)
        cursor.execute(create_stories_table)
        conn.commit()
        print("Tables 'users' and 'stories' created successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # This allows the script to be run directly to initialize the database
    print("Initializing database...")
    create_tables()
    print("Database initialization complete.") 