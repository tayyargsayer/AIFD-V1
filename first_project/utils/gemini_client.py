"""
Gemini API client utility for the Student Project Generator application.
"""
import time
import logging
from typing import Dict, Optional, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
import io

from first_project.config.settings import AppConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
QUOTA_ERROR_CODE = 429
RETRY_ATTEMPTS = 3
RETRY_DELAY_BASE = 2  # seconds
DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-1.5-flash"

class GeminiClient:
    """
    Client for interacting with the Gemini API.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key (Optional[str]): Gemini API key. If None, uses the one from environment variables.
        """
        self.api_key = api_key or AppConfig.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(AppConfig.ERROR_MESSAGES["api_key_missing"])
        
        genai.configure(api_key=self.api_key)
        self._model = None
        self._chat_session = None
        self._retry_attempts = RETRY_ATTEMPTS
        self._retry_delay = RETRY_DELAY_BASE  # seconds
        self._current_model_name = DEFAULT_MODEL  # Start with Gemini 2.5 Flash
        self._fallback_used = False
    
    def _configure_model(self, model_name: str = None, temperature: float = None, 
                         max_tokens: int = None, safety_level: str = None) -> None:
        """
        Configure the Gemini model with specified parameters.
        
        Args:
            model_name (str, optional): Name of the model to use.
            temperature (float, optional): Temperature parameter for generation.
            max_tokens (int, optional): Maximum number of tokens to generate.
            safety_level (str, optional): Safety level for content filtering.
        """
        model_name = model_name or self._current_model_name
        temperature = temperature or AppConfig.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or AppConfig.DEFAULT_MAX_TOKENS
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.95,
            top_k=40
        )
        
        # Map safety level to threshold
        safety_mapping = {
            "Minimum (BLOCK_NONE)": HarmBlockThreshold.BLOCK_NONE,
            "Düşük (BLOCK_ONLY_HIGH)": HarmBlockThreshold.BLOCK_ONLY_HIGH,
            "Orta (BLOCK_MEDIUM_AND_ABOVE)": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            "Yüksek (BLOCK_LOW_AND_ABOVE)": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
        
        safety_threshold = safety_mapping.get(safety_level, HarmBlockThreshold.BLOCK_NONE)
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: safety_threshold,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: safety_threshold,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: safety_threshold,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: safety_threshold,
        }
        
        try:
            self._model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            self._current_model_name = model_name
            logger.info(f"Model {model_name} configured successfully")
        except Exception as e:
            logger.error(f"Error configuring model: {e}")
            raise
    
    def _switch_to_fallback_model(self) -> bool:
        """
        Switch to fallback model if not already using it.
        
        Returns:
            bool: True if switched to fallback, False if already using fallback
        """
        # If we're already using the fallback model, we can't fall back further
        if self._current_model_name == FALLBACK_MODEL:
            return False
            
        logger.warning(f"Switching to fallback model: {FALLBACK_MODEL}")
        try:
            self._configure_model(model_name=FALLBACK_MODEL)
            self._fallback_used = True
            return True
        except Exception as e:
            logger.error(f"Error switching to fallback model: {e}")
            return False
    
    def create_chat_session(self, history: List[Dict[str, str]] = None) -> None:
        """
        Create a new chat session with optional history.
        
        Args:
            history (List[Dict[str, str]], optional): Chat history to initialize the session with.
        """
        if not self._model:
            self._configure_model()
        
        try:
            self._chat_session = self._model.start_chat(history=history)
            logger.info("Chat session created successfully")
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise
    
    def _is_quota_error(self, error) -> bool:
        """
        Check if an error is a quota limit error.
        
        Args:
            error: The error to check
            
        Returns:
            bool: True if it's a quota error, False otherwise
        """
        # Check for different forms of quota errors
        if hasattr(error, 'status_code') and error.status_code == QUOTA_ERROR_CODE:
            return True
        
        # Check error message text for quota-related keywords
        error_str = str(error).lower()
        quota_keywords = ['quota', 'rate limit', 'resource exhausted', 'too many requests']
        return any(keyword in error_str for keyword in quota_keywords)
    
    def _with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic and fallback to a different model on quota errors.
        
        Args:
            func: Function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        attempts = 0
        last_error = None
        
        while attempts < self._retry_attempts:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                last_error = e
                logger.warning(f"Attempt {attempts} failed: {e}")
                
                # If it's a quota error, try switching to fallback model
                if self._is_quota_error(e) and self._switch_to_fallback_model():
                    logger.info("Switched to fallback model due to quota limit")
                    # Reset attempts to give the fallback model a fresh start
                    attempts = 0
                    continue
                
                if attempts < self._retry_attempts:
                    retry_delay = self._retry_delay * (2 ** (attempts - 1))  # Exponential backoff
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                
        logger.error(f"All {self._retry_attempts} attempts failed. Last error: {last_error}")
        raise last_error
    
    def generate_project_ideas(self, prompt: str, temperature: float = None, 
                              max_tokens: int = None, images: List[Image.Image] = None, 
                              safety_level: str = None) -> str:
        """
        Generate project ideas based on the given prompt.
        
        Args:
            prompt (str): The prompt to generate ideas from
            temperature (float, optional): Temperature parameter for generation
            max_tokens (int, optional): Maximum number of tokens to generate
            images (List[Image.Image], optional): List of images to include in the prompt
            safety_level (str, optional): Safety level for content filtering
            
        Returns:
            str: Generated project ideas
        """
        if not self._model:
            self._configure_model(temperature=temperature, max_tokens=max_tokens, safety_level=safety_level)
        
        try:
            if images:
                contents = [prompt] + images
                response = self._with_retry(lambda: self._model.generate_content(contents))
            else:
                response = self._with_retry(lambda: self._model.generate_content(prompt))
            
            try:
                result_text = response.text
            except ValueError:
                logger.warning(f"Response was empty, likely due to safety filters. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'N/A'}")
                return "Üretilen içerik güvenlik politikalarını ihlal ettiği için engellendi. Lütfen isteğinizi değiştirip tekrar deneyin."

            # Add a note if fallback model was used
            if self._fallback_used:
                fallback_notice = "\n\n---\n*Not: Bu içerik alternatif bir model (gemini-1.5-flash) kullanılarak oluşturulmuştur. " \
                                 "Ana model kota sınırlaması nedeniyle kullanılamadı.*"
                result_text += fallback_notice
                
            return result_text
        except Exception as e:
            logger.error(f"Error generating project ideas: {e}")
            raise
    
    def chat_message(self, message: str, images: List[Image.Image] = None) -> str:
        """
        Send a message to the chat session and get a response.
        
        Args:
            message (str): The message to send
            images (List[Image.Image], optional): List of images to include in the message
            
        Returns:
            str: Response from the chat session
        """
        if not self._chat_session:
            self.create_chat_session()
        
        try:
            if images:
                contents = [message] + images
                response = self._with_retry(lambda: self._chat_session.send_message(contents))
            else:
                response = self._with_retry(lambda: self._chat_session.send_message(message))
            
            try:
                result_text = response.text
            except ValueError:
                logger.warning(f"Chat response was empty, likely due to safety filters. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'N/A'}")
                return "Yanıt, güvenlik politikalarını ihlal ettiği için engellendi. Lütfen sorunuzu değiştirip tekrar deneyin."

            # Add a note if fallback model was used
            if self._fallback_used:
                fallback_notice = "\n\n---\n*Not: Bu yanıt alternatif bir model (gemini-1.5-flash) kullanılarak oluşturulmuştur. " \
                                 "Ana model kota sınırlaması nedeniyle kullanılamadı.*"
                result_text += fallback_notice
                
            return result_text
        except Exception as e:
            logger.error(f"Error sending chat message: {e}")
            raise
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the current chat history.
        
        Returns:
            List[Dict[str, str]]: List of messages in the chat history
        """
        if not self._chat_session:
            return []
        
        history = []
        for message in self._chat_session.history:
            if hasattr(message, 'role') and hasattr(message, 'parts'):
                role = message.role
                content = ''.join(str(part) for part in message.parts)
                history.append({"role": role, "content": content})
        
        return history
    
    def process_image(self, image_bytes: bytes) -> Optional[Image.Image]:
        """
        Process an uploaded image for use with Gemini.
        
        Args:
            image_bytes (bytes): Raw image bytes
            
        Returns:
            Optional[Image.Image]: Processed PIL Image object or None if processing fails
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return image
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None 