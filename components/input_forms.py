"""
Input Forms Component - Clean Code Implementation

This module contains all form-related components for the Student Project Generator.
Demonstrates clean code principles:
- No magic strings or numbers
- All constants imported from constants.py
- Single responsibility functions
- Clear documentation

Author: AI Project Generator Team
Date: 2025
"""
from typing import Dict, Any, List, Optional
import streamlit as st

from config.settings import AppConfig
from utils.helpers import validate_file
from config.constants import (
    # Form Labels and Help Text
    DETAILED_INFO_LABEL, DETAILED_INFO_PLACEHOLDER, DETAILED_INFO_HELP,
    CATEGORIES_LABEL, CATEGORIES_HELP,
    DIFFICULTY_LABEL, DIFFICULTY_HELP,
    PROJECT_TYPE_LABEL, PROJECT_TYPE_HELP,
    INTERESTS_LABEL, INTERESTS_HELP,
    KEYWORDS_LABEL, KEYWORDS_PLACEHOLDER, KEYWORDS_HELP,
    TIMELINE_LABEL, TIMELINE_HELP,
    COMPLEXITY_LABEL, COMPLEXITY_HELP,
    FILE_UPLOAD_LABEL, FILE_UPLOAD_HELP,
    
    # Model Configuration Labels
    TEMPERATURE_LABEL, TEMPERATURE_HELP,
    MAX_TOKENS_LABEL, MAX_TOKENS_HELP,
    SAFETY_LEVEL_LABEL, SAFETY_LEVEL_HELP,
    
    # UI Constants
    FORM_KEY, SUBMIT_BUTTON_TEXT, MODEL_SETTINGS_TITLE, SECURITY_SETTINGS_TITLE,
    MARKDOWN_DIVIDER, CSS_SUB_HEADER, SECTION_CATEGORY, SECTION_SCOPE,
    
    # Numeric Constants
    TEMPERATURE_MIN, TEMPERATURE_MAX, TEMPERATURE_DEFAULT, TEMPERATURE_STEP,
    MAX_TOKENS_MIN, MAX_TOKENS_MAX, MAX_TOKENS_STEP,
    TIMELINE_MIN, TIMELINE_MAX, TIMELINE_DEFAULT, TIMELINE_STEP,
    COMPLEXITY_MIN, COMPLEXITY_MAX, COMPLEXITY_DEFAULT, COMPLEXITY_STEP,
    
    # Safety Levels
    SAFETY_LEVELS,
    
    # Default Values
    DEFAULT_ZERO
)

def create_header() -> None:
    """
    Create the main application header.
    
    Following clean code principles:
    - Single responsibility
    - No magic strings
    """
    st.title("🚀 Proje Öneriniz")

def create_detailed_info_input() -> str:
    """
    Create a text area for detailed project information input.
    
    Returns:
        str: User's detailed project information
        
    Following clean code principles:
    - Descriptive function name
    - Constants for all UI text
    - Clear return type annotation
    """
    return st.text_area(
        label=DETAILED_INFO_LABEL,
        placeholder=DETAILED_INFO_PLACEHOLDER,
        height=120,
        help=DETAILED_INFO_HELP
    )

def create_category_selector() -> List[str]:
    """
    Create a dropdown menu for selecting project categories.
    
    Returns:
        List[str]: Selected categories
        
    Following clean code principles:
    - Single responsibility
    - Clear return type
    - Constants for labels
    """
    return st.multiselect(
        label=CATEGORIES_LABEL,
        options=AppConfig.PROJECT_CATEGORIES,
        help=CATEGORIES_HELP
    )

def create_difficulty_selector() -> str:
    """
    Create a radio button group for selecting difficulty level.
    
    Returns:
        str: Selected difficulty level
        
    Following clean code principles:
    - Descriptive function name
    - Constants for configuration
    """
    return st.radio(
        label=DIFFICULTY_LABEL,
        options=AppConfig.DIFFICULTY_LEVELS,
        horizontal=True,
        help=DIFFICULTY_HELP
    )

def create_project_type_selector() -> str:
    """
    Create a radio button group for selecting project type.
    
    Returns:
        str: Selected project type
    """
    return st.radio(
        label=PROJECT_TYPE_LABEL,
        options=AppConfig.PROJECT_TYPES,
        horizontal=True,
        help=PROJECT_TYPE_HELP
    )

def create_interests_selector() -> List[str]:
    """
    Create a multi-select for selecting areas of interest.
    
    Returns:
        List[str]: Selected areas of interest
    """
    return st.multiselect(
        label=INTERESTS_LABEL,
        options=AppConfig.AREAS_OF_INTEREST,
        help=INTERESTS_HELP
    )

def create_keywords_input() -> str:
    """
    Create a text input for entering keywords.
    
    Returns:
        str: Entered keywords
    """
    return st.text_input(
        label=KEYWORDS_LABEL,
        placeholder=KEYWORDS_PLACEHOLDER,
        help=KEYWORDS_HELP
    )

def create_timeline_slider() -> int:
    """
    Create a slider for selecting project timeline.
    
    Returns:
        int: Selected timeline in weeks
        
    Following clean code principles:
    - All numeric values as constants
    - No magic numbers
    """
    return st.slider(
        label=TIMELINE_LABEL,
        min_value=TIMELINE_MIN,
        max_value=TIMELINE_MAX,
        value=TIMELINE_DEFAULT,
        step=TIMELINE_STEP,
        help=TIMELINE_HELP
    )

def create_complexity_slider() -> int:
    """
    Create a slider for selecting project complexity.
    
    Returns:
        int: Selected complexity level (1-10)
        
    Following clean code principles:
    - Constants for all numeric values
    - Clear documentation
    """
    return st.slider(
        label=COMPLEXITY_LABEL,
        min_value=COMPLEXITY_MIN,
        max_value=COMPLEXITY_MAX,
        value=COMPLEXITY_DEFAULT,
        step=COMPLEXITY_STEP,
        help=COMPLEXITY_HELP
    )

def create_file_uploader() -> Optional[bytes]:
    """
    Create a file uploader for inspiration images or documents.
    
    Returns:
        Optional[bytes]: Uploaded file bytes or None
        
    Following clean code principles:
    - Clear error handling
    - Constants for help text
    - Proper validation
    """
    uploaded_file = st.file_uploader(
        label=FILE_UPLOAD_LABEL,
        type=AppConfig.ALLOWED_EXTENSIONS,
        help=FILE_UPLOAD_HELP.format(
            allowed_types=', '.join(AppConfig.ALLOWED_EXTENSIONS)
        )
    )
    
    if uploaded_file is not None:
        is_valid, error_message = validate_file(uploaded_file)
        if not is_valid:
            st.error(error_message)
            return None
        
        return uploaded_file.getvalue()
    
    return None

def create_input_form() -> Dict[str, Any]:
    """
    Create the complete input form with all input components.
    
    Returns:
        Dict[str, Any]: Dictionary with all user inputs
        
    Following clean code principles:
    - Single responsibility for form creation
    - Constants for all UI elements
    - Clear structure and organization
    """
    with st.form(key=FORM_KEY):
        st.markdown(f'<h2 class="{CSS_SUB_HEADER}">📝 Proje Tercihleri</h2>', unsafe_allow_html=True)
        
        detailed_info = create_detailed_info_input()
        
        st.markdown(MARKDOWN_DIVIDER)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"##### **{SECTION_CATEGORY}**")
            categories = create_category_selector()
            interests = create_interests_selector()
            keywords = create_keywords_input()
        
        with col2:
            st.markdown(f"##### **{SECTION_SCOPE}**")
            project_type = create_project_type_selector()
            difficulty = create_difficulty_selector()
            timeline = create_timeline_slider()
            complexity = create_complexity_slider()
        
        st.markdown(MARKDOWN_DIVIDER)
        file_bytes = create_file_uploader()
        
        submit_button = st.form_submit_button(
            label=SUBMIT_BUTTON_TEXT,
            type="primary",
            use_container_width=True
        )
        
        # Return structured data following clean code principles
        return _create_user_inputs_dict(
            categories=categories,
            difficulty=difficulty,
            project_type=project_type,
            interests=interests,
            keywords=keywords,
            timeline=timeline,
            complexity=complexity,
            detailed_info=detailed_info,
            file_bytes=file_bytes,
            submitted=submit_button
        )

def _create_user_inputs_dict(
    categories: List[str],
    difficulty: str,
    project_type: str,
    interests: List[str],
    keywords: str,
    timeline: int,
    complexity: int,
    detailed_info: str,
    file_bytes: Optional[bytes],
    submitted: bool
) -> Dict[str, Any]:
    """
    Create a structured dictionary of user inputs.
    
    Args:
        categories: Selected project categories
        difficulty: Selected difficulty level
        project_type: Selected project type
        interests: Selected areas of interest
        keywords: Entered keywords
        timeline: Selected timeline in weeks
        complexity: Selected complexity level
        detailed_info: Detailed project information
        file_bytes: Uploaded file bytes
        submitted: Whether form was submitted
        
    Returns:
        Dict[str, Any]: Structured user inputs
        
    Following clean code principles:
    - Explicit parameter names
    - Clear structure
    - Type annotations
    """
    return {
        "categories": categories,
        "difficulty": difficulty,
        "project_type": project_type,
        "interests": interests,
        "keywords": keywords,
        "timeline": timeline,
        "complexity": complexity,
        "detailed_info": detailed_info,
        "file_bytes": file_bytes,
        "submitted": submitted
    }

def create_model_config_sidebar() -> Dict[str, Any]:
    """
    Create a sidebar for model configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with model configuration
        
    Following clean code principles:
    - Constants for all UI elements
    - No magic numbers
    - Clear structure
    """
    with st.sidebar:
        st.title(MODEL_SETTINGS_TITLE)
        
        temperature = st.slider(
            label=TEMPERATURE_LABEL,
            min_value=TEMPERATURE_MIN,
            max_value=TEMPERATURE_MAX,
            value=TEMPERATURE_DEFAULT,
            step=TEMPERATURE_STEP,
            help=TEMPERATURE_HELP
        )
        
        max_tokens = st.slider(
            label=MAX_TOKENS_LABEL,
            min_value=MAX_TOKENS_MIN,
            max_value=MAX_TOKENS_MAX,
            value=AppConfig.DEFAULT_MAX_TOKENS,
            step=MAX_TOKENS_STEP,
            help=MAX_TOKENS_HELP
        )
        
        st.markdown(MARKDOWN_DIVIDER)
        st.markdown(f"##### {SECURITY_SETTINGS_TITLE}")
        
        safety_level = st.selectbox(
            label=SAFETY_LEVEL_LABEL,
            options=SAFETY_LEVELS,
            index=DEFAULT_ZERO,  # Default to minimum (first option)
            help=SAFETY_LEVEL_HELP
        )
        
        return _create_model_config_dict(
            temperature=temperature,
            max_tokens=max_tokens,
            safety_level=safety_level
        )

def _create_model_config_dict(
    temperature: float,
    max_tokens: int,
    safety_level: str
) -> Dict[str, Any]:
    """
    Create a structured dictionary of model configuration.
    
    Args:
        temperature: Model temperature setting
        max_tokens: Maximum tokens for response
        safety_level: Safety level setting
        
    Returns:
        Dict[str, Any]: Structured model configuration
        
    Following clean code principles:
    - Explicit parameters
    - Clear structure
    - Type annotations
    """
    return {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "safety_level": safety_level
    } 