from pydantic import BaseModel, Field

class Story(BaseModel):
    """
    Pydantic model for story data validation.
    Represents the data required to create a new story.
    """
    user_id: int = Field(..., description="The ID of the user who created the story")
    title: str = Field(..., min_length=1, description="The title of the story")
    content: str = Field(..., min_length=1, description="The full generated content of the story")
    user_request: str = Field(..., max_length=500, description="The user's original request for the story (max 500 chars)")

class StoryInDB(Story):
    """
    Pydantic model representing a story as stored in the database.
    Includes database-generated fields like id and created_at.
    """
    id: int
    created_at: str # Stored as string from TIMESTAMP

# Example of how to use it
if __name__ == '__main__':
    # --- Valid Data ---
    try:
        story_data = {
            "user_id": 1,
            "title": "The Shadow in the Attic",
            "content": "It was a dark and stormy night...",
            "user_request": "A story about a haunted house."
        }
        story = Story(**story_data)
        print("Story validation successful:")
        print(story.model_dump_json(indent=2))
    except ValueError as e:
        print(f"Validation failed as expected: {e}")

    # --- Invalid Data (Request too long) ---
    try:
        long_request = "a" * 501
        invalid_story_data = {
            "user_id": 1,
            "title": "The Never-ending Request",
            "content": "This story could not be generated.",
            "user_request": long_request
        }
        story = Story(**invalid_story_data)
    except ValueError as e:
        print("\nCaught expected validation error for user_request length:")
        print(e) 