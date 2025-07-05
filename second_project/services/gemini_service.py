import google.generativeai as genai
from typing import Optional, Dict

from horror_story_app.config import settings

class GeminiService:
    """
    Handles all interactions with the Google Gemini AI.
    """

    def __init__(self):
        """
        Configures the Gemini API with the key from settings.
        """
        self.api_key = settings.GOOGLE_API_KEY
        if not self.api_key:
            # The app should still run, but AI features will be disabled.
            print("Warning: GOOGLE_API_KEY is not configured. GeminiService will be disabled.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Using the latest Flash model for speed and cost-effectiveness
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                print("Gemini Service configured successfully.")
            except Exception as e:
                print(f"Error configuring Gemini Service: {e}")
                self.model = None

    def generate_story(self, prompt: str) -> Optional[str]:
        """
        Generates a story using the Gemini model based on a given prompt.

        Args:
            prompt: The detailed prompt for the story generation.

        Returns:
            The generated story as a string, or None if generation fails.
        """
        if not self.model:
            print("Cannot generate story, Gemini model is not available.")
            return "Error: The AI story generation service is not configured."

        try:
            # Generate content using the configured model
            response = self.model.generate_content(prompt)
            
            # Basic content validation: check if the response has text
            if response.text:
                return response.text
            else:
                # This can happen if the content is blocked due to safety settings
                print("Warning: Gemini API returned an empty response. This might be due to safety filters.")
                return "The generated story was blocked. This may be due to the content of the request or safety settings. Please try again with a different request."

        except Exception as e:
            # Handle various potential API errors
            print(f"An error occurred during story generation: {e}")
            return f"An error occurred while generating the story. Please check the logs. Error: {e}"

# Example of how to use it
if __name__ == '__main__':
    # Make sure you have a .env file with your GOOGLE_API_KEY in the `horror_story_app` directory
    print("--- Initializing Gemini Service ---")
    gemini_service = GeminiService()

    if gemini_service.model:
        print("\n--- Generating a test story ---")
        test_prompt = "Write a short, two-paragraph horror story about a mysterious old book found in a library."
        story_content = gemini_service.generate_story(test_prompt)
        
        print("\n--- Generated Story ---")
        if story_content:
            print(story_content)
        else:
            print("Failed to generate a story.")
    else:
        print("\nSkipping story generation test because Gemini Service is not configured.") 