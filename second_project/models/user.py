from pydantic import BaseModel, Field, validator

class User(BaseModel):
    """
    Pydantic model for user data validation.
    Represents the data required to create a new user.
    """
    first_name: str = Field(..., min_length=2, description="User's first name")
    last_name: str = Field(..., min_length=2, description="User's last name")
    age: int = Field(..., ge=13, le=99, description="User's age (must be between 13 and 99)")

    @validator('first_name', 'last_name')
    def name_must_be_alpha(cls, v):
        """Validates that the name contains only alphabetic characters."""
        if not v.isalpha():
            raise ValueError('must contain only alphabetic characters')
        return v

class UserInDB(User):
    """
    Pydantic model representing a user as stored in the database.
    Includes database-generated fields like id and created_at.
    """
    id: int
    created_at: str # Stored as string from TIMESTAMP

# Example of how to use it
if __name__ == '__main__':
    # --- Valid Data ---
    try:
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 30
        }
        user = User(**user_data)
        print("User validation successful:")
        print(user.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Validation failed as expected: {e}")

    # --- Invalid Data (Age) ---
    try:
        invalid_user_data_age = {
            "first_name": "Jane",
            "last_name": "Doe",
            "age": 12
        }
        user = User(**invalid_user_data_age)
    except ValueError as e:
        print("\nCaught expected validation error for age:")
        print(e)

    # --- Invalid Data (Name) ---
    try:
        invalid_user_data_name = {
            "first_name": "Agent",
            "last_name": "47",
            "age": 35
        }
        user = User(**invalid_user_data_name)
    except ValueError as e:
        print("\nCaught expected validation error for name:")
        print(e) 