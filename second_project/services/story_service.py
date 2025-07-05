import sqlite3
from typing import List, Optional, Dict, Any

from horror_story_app.config.database import get_db_connection
from horror_story_app.models.story import Story, StoryInDB
from horror_story_app.services.gemini_service import GeminiService

class StoryService:
    """
    Handles all business logic related to stories, including generation and storage.
    """

    def __init__(self):
        self.gemini_service = GeminiService()

    def _create_story_prompt(self, user_request: str, preferences: Dict[str, Any]) -> str:
        """
        Constructs a detailed prompt for the AI based on user input.
        """
        # Unpack preferences with defaults
        story_type = preferences.get('type', 'classic gothic')
        length = preferences.get('length', 'short (about 300 words)')
        elements = preferences.get('elements', [])

        prompt = (
            f"Please write a compelling horror story based on the following user request.\n"
            f"User Request: '{user_request}'\n\n"
            f"The story should be in the style of: {story_type}.\n"
            f"It should be a {length} story.\n"
        )
        if elements:
            prompt += f"It must include the following horror elements: {', '.join(elements)}.\n\n"
        
        prompt += (
            "The story needs a clear title. Format the output as follows:\n"
            "Title: [Your Story Title Here]\n\n"
            "[The full text of the story begins here...]"
        )
        return prompt
    
    def _parse_story_and_title(self, generated_text: str) -> (str, str):
        """
        Parses the AI's output to separate the title from the content.
        """
        if "Title:" in generated_text:
            parts = generated_text.split("Title:", 1)[1].split('\n', 1)
            title = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else "No content was generated."
            return title, content
        return "Untitled Story", generated_text # Fallback

    def generate_and_save_story(self, user_id: int, user_request: str, preferences: Dict[str, Any]) -> Optional[StoryInDB]:
        """
        Generates a new story, saves it, and returns the stored story object.
        """
        prompt = self._create_story_prompt(user_request, preferences)
        generated_text = self.gemini_service.generate_story(prompt)

        if not generated_text or "Error:" in generated_text or "blocked" in generated_text:
            print(f"Failed to generate story from AI: {generated_text}")
            # Optionally, you could raise an exception here to be handled by the UI
            return None

        title, content = self._parse_story_and_title(generated_text)

        try:
            story_data = Story(user_id=user_id, title=title, content=content, user_request=user_request)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO stories (user_id, title, content, user_request) VALUES (?, ?, ?, ?)"
            cursor.execute(sql, (story_data.user_id, story_data.title, story_data.content, story_data.user_request))
            conn.commit()
            story_id = cursor.lastrowid
            conn.close()

            return self.get_story_by_id(story_id)
        except ValueError as e:
            print(f"Story data validation error: {e}")
            return None
        except sqlite3.Error as e:
            print(f"Database error while saving story: {e}")
            return None

    def get_user_stories(self, user_id: int) -> List[StoryInDB]:
        """
        Retrieves all stories created by a specific user.
        """
        stories = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT * FROM stories WHERE user_id = ? ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                stories.append(StoryInDB(**dict(row)))
        except sqlite3.Error as e:
            print(f"Database error while fetching user stories: {e}")
        return stories

    def get_story_by_id(self, story_id: int) -> Optional[StoryInDB]:
        """
        Retrieves a single story by its ID.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT * FROM stories WHERE id = ?"
            cursor.execute(sql, (story_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return StoryInDB(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"Database error while fetching story: {e}")
            return None 