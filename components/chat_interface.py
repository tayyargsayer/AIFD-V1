"""
Chat Interface Component - Clean Code Implementation

This module handles chat functionality for the Student Project Generator.
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
from typing import Dict, Any, List, Optional
import streamlit as st
from PIL import Image

from config.settings import AppConfig
from utils.gemini_client import GeminiClient
from utils.helpers import create_chat_prompt, display_info_box, display_error_box
from config.constants import (
    # Chat Status Messages
    STATUS_CHAT_PREPARING, STATUS_CHAT_ANALYZING, STATUS_CHAT_GENERATING,
    STATUS_CHAT_READY, STATUS_CHAT_COMPLETE, STATUS_CHAT_ERROR,
    
    # UI Constants
    CHAT_HEADER, CSS_SUB_HEADER, CHAT_INPUT_PLACEHOLDER,
    
    # Session State Keys
    SESSION_MESSAGES, SESSION_GEMINI_CLIENT,
    
    # Tab Names
    TAB_CHAT, TAB_HELP,
    
    # Chat Help Content
    CHAT_HELP_TITLE, CHAT_HELP_CONTENT,
    
    # Info Messages
    INFO_CHAT_WELCOME,
    
    # Timing Constants
    DELAY_SHORT,
    
    # Default Values
    DEFAULT_NONE,
    
    # User Roles
    USER_ROLE, ASSISTANT_ROLE
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_chat_session() -> None:
    """
    Initialize the chat session state if not already initialized.
    
    Following clean code principles:
    - Single responsibility
    - Constants for session state keys
    - Clear error handling
    """
    if SESSION_MESSAGES not in st.session_state:
        st.session_state[SESSION_MESSAGES] = []
    
    if SESSION_GEMINI_CLIENT not in st.session_state:
        try:
            st.session_state[SESSION_GEMINI_CLIENT] = GeminiClient()
            st.session_state[SESSION_GEMINI_CLIENT].create_chat_session()
        except Exception as e:
            logger.error(f"Error initializing chat client: {e}")
            st.session_state[SESSION_GEMINI_CLIENT] = DEFAULT_NONE

def display_chat_messages() -> None:
    """
    Display all messages in the chat session.
    
    Following clean code principles:
    - Single responsibility
    - Constants for message roles
    - Clear iteration logic
    """
    for message in st.session_state[SESSION_MESSAGES]:
        role = message["role"]
        content = message["content"]
        
        with st.chat_message(role):
            st.markdown(content)

def add_message(role: str, content: str) -> None:
    """
    Add a message to the chat history.
    
    Args:
        role (str): Role of the message sender (user or assistant)
        content (str): Content of the message
        
    Following clean code principles:
    - Clear parameter validation
    - Constants for session state
    - Single responsibility
    """
    st.session_state[SESSION_MESSAGES].append({
        "role": role, 
        "content": content
    })

def handle_user_input(user_input: str, project_context: str = None) -> None:
    """
    Handle user input in the chat interface.
    
    Args:
        user_input (str): User's message
        project_context (str, optional): Context from previously generated project
        
    Following clean code principles:
    - Input validation
    - Constants for all UI text
    - Clear error handling
    - Single responsibility
    """
    if not user_input.strip():
        return
    
    # Add user message to chat
    add_message(USER_ROLE, user_input)
    
    # Display user message
    with st.chat_message(USER_ROLE):
        st.markdown(user_input)
    
    # Check if Gemini client is available
    if not st.session_state[SESSION_GEMINI_CLIENT]:
        display_error_box(AppConfig.ERROR_MESSAGES["api_key_missing"])
        return
    
    # Generate and display response
    _generate_and_display_response(user_input, project_context)

def _generate_and_display_response(user_input: str, project_context: str = None) -> None:
    """
    Generate and display AI response with status tracking.
    
    Args:
        user_input (str): User's message
        project_context (str, optional): Project context
        
    Following clean code principles:
    - Single responsibility
    - Constants for status messages
    - Clear error handling
    """
    with st.chat_message(ASSISTANT_ROLE):
        with st.status(STATUS_CHAT_PREPARING, expanded=False) as status:
            try:
                # Analyze user question
                st.write(STATUS_CHAT_ANALYZING)
                time.sleep(DELAY_SHORT)
                
                # Create prompt
                prompt = create_chat_prompt(user_input, project_context)
                
                # Generate response
                st.write(STATUS_CHAT_GENERATING)
                response = st.session_state[SESSION_GEMINI_CLIENT].chat_message(prompt)
                
                # Mark as complete
                st.write(STATUS_CHAT_READY)
                status.update(label=STATUS_CHAT_COMPLETE, state="complete", expanded=False)
                
            except Exception as e:
                logger.error(f"Error in chat response: {e}")
                response = f"Üzgünüm, bir hata oluştu: {str(e)}"
                status.update(label=STATUS_CHAT_ERROR, state="error", expanded=False)
        
        # Display the response
        st.markdown(response)
        
        # Add assistant message to chat
        add_message(ASSISTANT_ROLE, response)

def create_chat_interface(project_context: str = None) -> None:
    """
    Create the chat interface component.
    
    Args:
        project_context (str, optional): Context from previously generated project
        
    Following clean code principles:
    - Single responsibility
    - Constants for UI elements
    - Clear component organization
    """
    st.markdown(f'<h2 class="{CSS_SUB_HEADER}">{CHAT_HEADER}</h2>', unsafe_allow_html=True)
    
    # Initialize chat session
    initialize_chat_session()
    
    # Display welcome message if no messages yet
    if not st.session_state[SESSION_MESSAGES]:
        display_info_box(INFO_CHAT_WELCOME)
    
    # Display chat messages
    display_chat_messages()
    
    # Chat input
    user_input = st.chat_input(CHAT_INPUT_PLACEHOLDER)
    if user_input:
        handle_user_input(user_input, project_context)

def create_chat_tab(project_context: str = None) -> None:
    """
    Create a tab for the chat interface.
    
    Args:
        project_context (str, optional): Context from previously generated project
        
    Following clean code principles:
    - Constants for tab names
    - Clear separation of chat and help content
    - Single responsibility
    """
    tab1, tab2 = st.tabs([TAB_CHAT, TAB_HELP])
    
    with tab1:
        create_chat_interface(project_context)
    
    with tab2:
        _display_chat_help()

def _display_chat_help() -> None:
    """
    Display chat help content.
    
    Following clean code principles:
    - Single responsibility
    - Constants for help content
    - Clear content organization
    """
    st.markdown(CHAT_HELP_TITLE)
    st.markdown(CHAT_HELP_CONTENT) 