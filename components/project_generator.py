"""
Project Generator Component - Clean Code Implementation

This module handles project generation logic for the Student Project Generator.
Demonstrates clean code principles:
- No magic strings or numbers
- All constants imported from constants.py
- Single responsibility functions
- Clear error handling and logging

Author: AI Project Generator Team
Date: 2025
"""
import time
import logging
from typing import Dict, Any, Optional, Tuple
import streamlit as st
from PIL import Image
import io

from config.settings import AppConfig
from utils.gemini_client import GeminiClient
from utils.helpers import (
    create_project_prompt, 
    extract_title_from_content,
    save_project,
    get_download_link,
    display_success_box,
    display_error_box
)
from config.constants import (
    # Status Messages
    STATUS_GENERATING, STATUS_PROCESSING_INPUTS, STATUS_PROCESSING_IMAGE,
    STATUS_CREATING_PROMPT, STATUS_CONNECTING_API, STATUS_GENERATING_IDEAS,
    STATUS_PREPARING_RESULTS, STATUS_PROJECT_COMPLETE, STATUS_PROJECT_READY,
    
    # UI Constants
    MAIN_HEADER, CSS_SUB_HEADER, SAVE_PROJECT_BUTTON, 
    DOWNLOAD_MARKDOWN_BUTTON, START_CHAT_BUTTON,
    
    # Session State Keys
    SESSION_SHOW_CHAT, SESSION_PROJECT_CONTEXT,
    
    # Success and Error Messages
    SUCCESS_PROJECT_SAVED, ERROR_PROJECT_SAVE,
    
    # Timing Constants
    DELAY_SHORT, DELAY_MEDIUM,
    
    # Safety Levels
    SAFETY_MINIMUM,
    
    # File Extensions
    MARKDOWN_EXTENSION,
    
    # Default Values
    DEFAULT_EMPTY_STRING
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_uploaded_image(file_bytes: bytes) -> Optional[Image.Image]:
    """
    Process an uploaded image file.
    
    Args:
        file_bytes (bytes): Raw image file bytes
        
    Returns:
        Optional[Image.Image]: Processed PIL Image or None if processing fails
        
    Following clean code principles:
    - Single responsibility
    - Clear error handling
    - Descriptive function name
    """
    try:
        if not file_bytes:
            return None
            
        image = Image.open(io.BytesIO(file_bytes))
        return image
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None

def generate_project_ideas(
    user_inputs: Dict[str, Any], 
    model_config: Dict[str, Any]
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Generate project ideas based on user inputs.
    
    Args:
        user_inputs (Dict[str, Any]): User input values
        model_config (Dict[str, Any]): Model configuration
        
    Returns:
        Tuple[bool, Optional[str], Optional[Dict[str, Any]]]: 
            (success, error_message, project_data)
            
    Following clean code principles:
    - Clear function signature
    - Proper error handling
    - Constants for all UI text
    - Single responsibility
    """
    try:
        # Use status widget with constants for all text
        with st.status(STATUS_GENERATING, expanded=True) as status:
            
            # Process inputs
            st.write(STATUS_PROCESSING_INPUTS)
            time.sleep(DELAY_MEDIUM)
            
            # Process image if provided
            image = _process_image_input(user_inputs)
            
            # Create prompt
            st.write(STATUS_CREATING_PROMPT)
            prompt = create_project_prompt(user_inputs)
            time.sleep(DELAY_SHORT)
            
            # Initialize Gemini client
            st.write(STATUS_CONNECTING_API)
            client = GeminiClient()
            time.sleep(DELAY_SHORT)
            
            # Generate content
            st.write(STATUS_GENERATING_IDEAS)
            response_text = _generate_ai_response(client, prompt, model_config, image)
            
            # Process response
            st.write(STATUS_PREPARING_RESULTS)
            time.sleep(DELAY_SHORT)
            
            # Create project data
            project_data = _create_project_data(response_text, user_inputs)
            
            # Complete
            st.write(STATUS_PROJECT_COMPLETE)
            status.update(label=STATUS_PROJECT_READY, state="complete", expanded=False)
        
        return True, None, project_data
        
    except Exception as e:
        logger.error(f"Error generating project ideas: {e}")
        error_message = AppConfig.ERROR_MESSAGES["api_error"].format(error=str(e))
        return False, error_message, None

def _process_image_input(user_inputs: Dict[str, Any]) -> Optional[Image.Image]:
    """
    Process image input if provided by user.
    
    Args:
        user_inputs (Dict[str, Any]): User input dictionary
        
    Returns:
        Optional[Image.Image]: Processed image or None
        
    Following clean code principles:
    - Single responsibility
    - Clear function name with underscore prefix for private function
    - Constants for status messages
    """
    image = None
    if user_inputs.get("file_bytes"):
        st.write(STATUS_PROCESSING_IMAGE)
        image = process_uploaded_image(user_inputs["file_bytes"])
        time.sleep(DELAY_SHORT)
    return image

def _generate_ai_response(
    client: GeminiClient, 
    prompt: str, 
    model_config: Dict[str, Any], 
    image: Optional[Image.Image]
) -> str:
    """
    Generate AI response using Gemini client.
    
    Args:
        client (GeminiClient): Initialized Gemini client
        prompt (str): Generated prompt
        model_config (Dict[str, Any]): Model configuration
        image (Optional[Image.Image]): Processed image if any
        
    Returns:
        str: Generated response text
        
    Following clean code principles:
    - Single responsibility
    - Clear parameter extraction
    - Constants for default values
    """
    temperature = model_config.get("temperature", AppConfig.DEFAULT_TEMPERATURE)
    max_tokens = model_config.get("max_tokens", AppConfig.DEFAULT_MAX_TOKENS)
    safety_level = model_config.get("safety_level", SAFETY_MINIMUM)
    
    images = [image] if image else None
    return client.generate_project_ideas(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        images=images,
        safety_level=safety_level
    )

def _create_project_data(response_text: str, user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create structured project data dictionary.
    
    Args:
        response_text (str): Generated response from AI
        user_inputs (Dict[str, Any]): Original user inputs
        
    Returns:
        Dict[str, Any]: Structured project data
        
    Following clean code principles:
    - Single responsibility
    - Clear data structure
    - Consistent naming
    """
    title = extract_title_from_content(response_text)
    
    return {
        "title": title,
        "content": response_text,
        "user_inputs": _extract_user_input_summary(user_inputs)
    }

def _extract_user_input_summary(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and structure user input summary.
    
    Args:
        user_inputs (Dict[str, Any]): Raw user inputs
        
    Returns:
        Dict[str, Any]: Structured user input summary
        
    Following clean code principles:
    - Single responsibility
    - Clear data extraction
    - Default values for missing data
    """
    return {
        "categories": user_inputs.get("categories", []),
        "difficulty": user_inputs.get("difficulty", DEFAULT_EMPTY_STRING),
        "project_type": user_inputs.get("project_type", DEFAULT_EMPTY_STRING),
        "interests": user_inputs.get("interests", []),
        "keywords": user_inputs.get("keywords", DEFAULT_EMPTY_STRING),
        "timeline": user_inputs.get("timeline", 0),
        "complexity": user_inputs.get("complexity", 0)
    }

def display_project_results(project_data: Dict[str, Any]) -> None:
    """
    Display the generated project results with action buttons.
    
    Args:
        project_data (Dict[str, Any]): Generated project data
        
    Following clean code principles:
    - Single responsibility
    - Constants for all UI text
    - Clear separation of concerns
    """
    st.markdown(f'<h2 class="{CSS_SUB_HEADER}">{MAIN_HEADER}</h2>', unsafe_allow_html=True)
    
    # Display the content
    st.markdown(project_data["content"])
    
    # Add action buttons
    _display_action_buttons(project_data)

def _display_action_buttons(project_data: Dict[str, Any]) -> None:
    """
    Display action buttons for the generated project.
    
    Args:
        project_data (Dict[str, Any]): Generated project data
        
    Following clean code principles:
    - Single responsibility
    - Constants for button labels
    - Clear button organization
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        _handle_save_button(project_data)
    
    with col2:
        _handle_download_button(project_data)
    
    with col3:
        _handle_chat_button(project_data)

def _handle_save_button(project_data: Dict[str, Any]) -> None:
    """
    Handle the save project button.
    
    Args:
        project_data (Dict[str, Any]): Project data to save
        
    Following clean code principles:
    - Single responsibility
    - Constants for messages
    - Clear success/error handling
    """
    if st.button(SAVE_PROJECT_BUTTON, use_container_width=True):
        if save_project(project_data):
            display_success_box(SUCCESS_PROJECT_SAVED)
        else:
            display_error_box(ERROR_PROJECT_SAVE)

def _handle_download_button(project_data: Dict[str, Any]) -> None:
    """
    Handle the download markdown button.
    
    Args:
        project_data (Dict[str, Any]): Project data to download
        
    Following clean code principles:
    - Single responsibility
    - Constants for file naming
    - Clear file name generation
    """
    markdown_content = project_data["content"]
    title = project_data["title"].replace(" ", "_")
    download_filename = f"{title}{MARKDOWN_EXTENSION}"
    
    st.markdown(
        get_download_link(markdown_content, download_filename, DOWNLOAD_MARKDOWN_BUTTON),
        unsafe_allow_html=True
    )

def _handle_chat_button(project_data: Dict[str, Any]) -> None:
    """
    Handle the start chat button.
    
    Args:
        project_data (Dict[str, Any]): Project data for chat context
        
    Following clean code principles:
    - Single responsibility
    - Constants for session state keys
    - Clear state management
    """
    if st.button(START_CHAT_BUTTON, use_container_width=True):
        st.session_state[SESSION_SHOW_CHAT] = True
        st.session_state[SESSION_PROJECT_CONTEXT] = project_data["content"] 