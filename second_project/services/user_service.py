import sqlite3
from typing import Optional

from horror_story_app.config.database import get_db_connection
from horror_story_app.models.user import User, UserInDB

class UserService:
    """
    Handles all business logic related to users.
    """

    def create_user(self, first_name: str, last_name: str, age: int) -> Optional[int]:
        """
        Validates user data and saves a new user to the database.

        Args:
            first_name: The user's first name.
            last_name: The user's last name.
            age: The user's age.

        Returns:
            The ID of the newly created user, or None if creation fails.
        """
        try:
            # 1. Validate data using the Pydantic model
            user_data = User(first_name=first_name, last_name=last_name, age=age)
            
            # 2. Save to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = "INSERT INTO users (first_name, last_name, age) VALUES (?, ?, ?)"
            cursor.execute(sql, (user_data.first_name, user_data.last_name, user_data.age))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return user_id
        except ValueError as e:
            # Pydantic validation error
            print(f"User data validation error: {e}")
            return None
        except sqlite3.Error as e:
            print(f"Database error while creating user: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        """
        Retrieves a single user from the database by their ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A UserInDB object if the user is found, otherwise None.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = "SELECT * FROM users WHERE id = ?"
            cursor.execute(sql, (user_id,))
            
            user_row = cursor.fetchone()
            conn.close()
            
            if user_row:
                return UserInDB(**dict(user_row))
            return None
        except sqlite3.Error as e:
            print(f"Database error while fetching user: {e}")
            return None

# Example of how to use it
if __name__ == '__main__':
    # Note: This requires the database to be initialized first.
    # Run `python -m horror_story_app.models.database_models` from the project root.
    
    service = UserService()
    
    print("--- Creating a new user ---")
    new_user_id = service.create_user(first_name="Test", last_name="User", age=25)
    
    if new_user_id:
        print(f"User created successfully with ID: {new_user_id}")
        
        print("\n--- Fetching the user ---")
        fetched_user = service.get_user_by_id(new_user_id)
        if fetched_user:
            print("Found user:")
            print(fetched_user.model_dump_json(indent=2))
        else:
            print("Could not find the user.")
            
    else:
        print("Failed to create user.")

    print("\n--- Creating a user with invalid data ---")
    invalid_user_id = service.create_user(first_name="Invalid123", last_name="User", age=100)
    if not invalid_user_id:
        print("Correctly failed to create user with invalid data.") 