"""
Student Project Generator - Main Application

This Streamlit application helps students generate project ideas and provides
implementation guidance using the Gemini API.

This file demonstrates clean code principles:
- No magic strings or numbers
- All constants imported from constants.py
- Clear separation of concerns
- Proper documentation

Author: AI Project Generator Team
Date: 2025
"""
import os
import logging
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components
from components.input_forms import create_header, create_input_form, create_model_config_sidebar
from components.project_generator import generate_project_ideas, display_project_results
from components.chat_interface import create_chat_tab
from utils.helpers import apply_custom_css, display_error_box, display_warning_box
from config.settings import AppConfig
from config.constants import (
    # Page Configuration
    PAGE_TITLE, PAGE_ICON, LAYOUT_WIDE, SIDEBAR_EXPANDED,
    # Session State Keys
    SESSION_SHOW_CHAT, SESSION_PROJECT_DATA, SESSION_PROJECT_CONTEXT, SESSION_MODEL_CONFIG,
    # Button Labels
    BACK_BUTTON_TEXT,
    # Warning Messages
    WARNING_FILL_REQUIRED_FIELDS,
    # Default Values
    DEFAULT_NONE
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_session_state() -> None:
    """
    Initialize session state variables.
    
    Following clean code principles, all session state keys are defined
    as constants to avoid magic strings and improve maintainability.
    """
    if SESSION_SHOW_CHAT not in st.session_state:
        st.session_state[SESSION_SHOW_CHAT] = False
    
    if SESSION_PROJECT_DATA not in st.session_state:
        st.session_state[SESSION_PROJECT_DATA] = DEFAULT_NONE
    
    if SESSION_PROJECT_CONTEXT not in st.session_state:
        st.session_state[SESSION_PROJECT_CONTEXT] = DEFAULT_NONE
    
    if SESSION_MODEL_CONFIG not in st.session_state:
        st.session_state[SESSION_MODEL_CONFIG] = DEFAULT_NONE

def main() -> None:
    """
    Main function to run the Streamlit application.
    
    This function demonstrates clean code principles:
    - Single responsibility principle
    - Clear flow of execution
    - No magic strings or numbers
    - Proper error handling
    """
    # Set page config using constants
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT_WIDE,
        initial_sidebar_state=SIDEBAR_EXPANDED
    )
    
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Check API key
    if not AppConfig.GEMINI_API_KEY:
        display_error_box(AppConfig.ERROR_MESSAGES["api_key_missing"])
        st.stop()
    
    # Create header
    create_header()
    
    # Create sidebar with model configuration
    model_config = create_model_config_sidebar()
    
    # Store model config in session state
    st.session_state[SESSION_MODEL_CONFIG] = model_config
    
    # Main content area - Route based on session state
    if st.session_state[SESSION_SHOW_CHAT] and st.session_state[SESSION_PROJECT_CONTEXT]:
        _handle_chat_interface()
    else:
        _handle_project_generation()

def _handle_chat_interface() -> None:
    """
    Handle the chat interface display and navigation.
    
    Private function following clean code principles:
    - Single responsibility
    - Clear naming convention with underscore prefix
    """
    # Show chat interface if a project has been generated
    create_chat_tab(st.session_state[SESSION_PROJECT_CONTEXT])
    
    # Add button to go back to project generation
    if st.button(BACK_BUTTON_TEXT, type="primary"):
        st.session_state[SESSION_SHOW_CHAT] = False
        st.rerun()

def _handle_project_generation() -> None:
    """
    Handle the project generation form and processing.
    
    Private function following clean code principles:
    - Single responsibility
    - Clear error handling
    - No magic strings
    """
    # Show project generation form
    user_inputs = create_input_form()
    
    # Process form submission
    if user_inputs["submitted"]:
        if _validate_user_inputs(user_inputs):
            _process_project_generation(user_inputs)
        else:
            display_warning_box(WARNING_FILL_REQUIRED_FIELDS)
    
    # Display previously generated project if available
    elif st.session_state[SESSION_PROJECT_DATA]:
        display_project_results(st.session_state[SESSION_PROJECT_DATA])

def _validate_user_inputs(user_inputs: dict) -> bool:
    """
    Validate that at least one key input is provided.
    
    Args:
        user_inputs (dict): User input dictionary
        
    Returns:
        bool: True if inputs are valid, False otherwise
        
    Following clean code principles:
    - Single responsibility
    - Clear validation logic
    - Descriptive function name
    """
    return (
        user_inputs["detailed_info"].strip() or 
        user_inputs["keywords"].strip() or 
        user_inputs["categories"] or 
        user_inputs["interests"]
    )

def _process_project_generation(user_inputs: dict) -> None:
    """
    Process project generation and handle results.
    
    Args:
        user_inputs (dict): Validated user inputs
        
    Following clean code principles:
    - Single responsibility
    - Clear error handling
    - Proper state management
    """
    model_config = st.session_state[SESSION_MODEL_CONFIG]
    success, error_message, project_data = generate_project_ideas(user_inputs, model_config)
    
    if success and project_data:
        # Store project data in session state
        st.session_state[SESSION_PROJECT_DATA] = project_data
        
        # Display results
        display_project_results(project_data)
    elif error_message:
        display_error_box(error_message)

if __name__ == "__main__":
    main() 