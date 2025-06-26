import streamlit as st
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

from config import AppConfig

# Explicitly load the .env file from the app's directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

def create_header():
    """Creates the application header."""
    st.title("💡 AI Project Idea Generator")
    st.markdown("Enter your field of interest, and I will generate a detailed AI project proposal for you.")

def create_text_input_section():
    """Create comprehensive text input interface for user's interest."""
    st.subheader("✍️ What is Your Field of Interest?")
    text_input = st.text_area(
        "Enter a topic, industry, or hobby",
        height=100,
        placeholder="For example: animal husbandry, e-commerce, renewable energy, education...",
        help="Be as specific or general as you like."
    )
    
    return text_input

@st.cache_resource
def configure_gemini_model(temperature, max_tokens):
    """
    Configure Gemini model with optimal settings
    """
    genai.configure(api_key=AppConfig.GEMINI_API_KEY)
    generation_config = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens
    )
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
    return model

def create_project_proposal_prompt(user_interest):
    """Creates a detailed prompt to generate an AI project proposal."""
    return f"""
    Act as an experienced AI consultant and project manager.
    A user has expressed interest in the following field: "{user_interest}".

    Your task is to generate a detailed and practical AI project proposal tailored to this field. The proposal should be clear, well-structured, and provide a solid starting point for development.

    Please structure your response with the following sections, using Markdown for formatting:

    ### 1. Project Title
    A catchy and descriptive title for the project.

    ### 2. Problem Statement
    Describe a specific, real-world problem in the "{user_interest}" field that this project will solve. Be specific about the pain points.

    ### 3. Proposed AI Solution
    Detail how an AI system would address this problem. Describe the core functionality of the application.

    ### 4. Required Data
    What kind of data would be needed to train and run the AI model? Where could this data be sourced? (e.g., public datasets, sensor data, user-generated content).

    ### 5. Potential Benefits
    List the key benefits of implementing this solution (e.g., increased efficiency, cost savings, new insights).

    ### 6. Technical Stack
    Suggest a potential technical stack for building this project.
    - **AI Model/Algorithm:** (e.g., Computer Vision, NLP, Forecasting model, etc.)
    - **Frameworks:** (e.g., TensorFlow, PyTorch, Scikit-learn, Streamlit).
    - **Platform:** (e.g., Web App, Mobile App, Edge Device).

    Please provide a comprehensive and actionable proposal.
    """

def handle_api_error(e):
    """Handle API errors gracefully."""
    st.error(f"An API error occurred: {e}")
    st.info("💡 Please check your API key and network connection. If the issue persists, the service may be temporarily unavailable.")
    return "Error: Could not generate a response."

def display_results_section():
    """Displays the generated project proposal."""
    st.subheader("🚀 Your AI Project Proposal")
    if 'response' in st.session_state:
        st.markdown(st.session_state.response)
    else:
        st.info("Your project proposal will be displayed here once it's generated.")

def process_input(text_input, temperature, max_tokens):
    """
    Process input with visual progress indicators, configure and call the AI model.
    """
    progress_bar = st.progress(0, "Initializing...")
    status_text = st.empty()

    try:
        status_text.text('⚙️ Configuring AI model...')
        progress_bar.progress(25)
        model = configure_gemini_model(temperature, max_tokens)

        status_text.text('📝 Creating a specialized prompt...')
        progress_bar.progress(50)
        prompt = create_project_proposal_prompt(text_input)

        status_text.text('🧠 Generating project idea with AI...')
        progress_bar.progress(75)
        response = model.generate_content(prompt)
        response_text = response.text

        status_text.text('✅ Proposal Ready!')
        progress_bar.progress(100)
        st.session_state.response = response_text
        time.sleep(1)

    except Exception as e:
        handle_api_error(e)
    finally:
        progress_bar.empty()
        status_text.empty()

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="AI Project Idea Generator",
        page_icon="💡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if not AppConfig.GEMINI_API_KEY:
        st.error("⚠️ GEMINI_API_KEY is not configured. Please add it to your .env file.")
        return

    create_header()

    st.sidebar.title("⚙️ Model Configuration")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05, help="Controls creativity. Higher is more creative.")
    max_tokens = st.sidebar.slider("Max Output Tokens", 256, 2048, 1024, 64, help="Maximum length of the proposal.")

    col1, col2 = st.columns([1, 1])

    with col1:
        text_input = create_text_input_section()
        
        if st.button("Generate Project Proposal", type="primary"):
            if not text_input or len(text_input.strip()) < 3:
                 st.warning("⚠️ Please enter your field of interest (at least 3 characters).")
            else:
                process_input(text_input, temperature, max_tokens)
    
    with col2:
        display_results_section()

if __name__ == "__main__":
    main() 