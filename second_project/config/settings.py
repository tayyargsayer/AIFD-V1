import os
from dotenv import load_dotenv

def load_environment_variables():
    """
    Loads environment variables from a .env file.

    The .env file should be located in the parent directory of this script's location
    (i.e., in the 'horror_story_app' directory).
    """
    # Determine the path to the .env file
    # The script is in horror_story_app/config/, so we go up one level.
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(project_dir, '.env')
    
    # Load the .env file
    load_dotenv(dotenv_path)

# Load environment variables when this module is imported
load_environment_variables()

# --- Application Settings ---
# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Get the secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# --- Validation ---
# You can add checks here to ensure critical variables are set
if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY is not set. AI features will not work.")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. The application cannot start without a database.") 