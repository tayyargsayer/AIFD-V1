import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
import io
from PIL import Image

# Load environment variables from .env file
load_dotenv()

def generate_image(prompt: str):
    """
    Generates an image based on a text prompt using the Gemini API.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Please create a .env file and add your API key.")
        return

    try:
        # Configure the client
        client = genai.Client(api_key=api_key)
        
        # Define the model and generation config
        model = "gemini-2.0-flash-preview-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            response_mime_type="image/png",
        )

        # Generate the content
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

        # Process the response
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            if part.inline_data and part.inline_data.data:
                # Display the image
                image_data = part.inline_data.data
                image = Image.open(io.BytesIO(image_data))
                st.image(image, caption="Generated Image", use_column_width=True)
            elif part.text:
                st.info(f"Received text instead of an image: {part.text}")
        else:
            st.warning("Could not generate an image from the prompt. The model might have refused the request.")

    except Exception as e:
        st.error(f"An error occurred: {e}")


# --- Streamlit App UI ---
st.set_page_config(page_title="Gemini Image Generator", layout="wide")
st.title("Text-to-Image Generation with Gemini")

st.info("Enter a descriptive prompt below and click 'Generate Image' to create an image.")

prompt_text = st.text_area("Your Prompt:", height=100, placeholder="e.g., A majestic horse running on a beach at sunset")

if st.button("Generate Image", use_container_width=True):
    if prompt_text:
        with st.spinner("Generating your masterpiece..."):
            generate_image(prompt_text)
    else:
        st.warning("Please enter a prompt to generate an image.")