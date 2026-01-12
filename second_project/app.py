import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
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
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
        response = model.generate_content(
            prompt,
            generation_config={
                "response_modalities": ["IMAGE", "TEXT"]
            }
        )

        image_data = None

        # Öncelikle media alanını kontrol et
        if hasattr(response, "media") and response.media:
            image_data = response.media[0].data
        # Alternatif olarak candidates/parts yapısını kontrol et
        elif hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts") and candidate.content.parts:
                for part in candidate.content.parts:
                    # Bazı durumlarda birden fazla part olabilir, ilk görseli bul
                    if hasattr(part, "inline_data") and part.inline_data and hasattr(part.inline_data, "data"):
                        image_data = part.inline_data.data
                        break

        if image_data:
            try:
                image = Image.open(io.BytesIO(image_data))
                st.image(image, caption="Generated Image", use_container_width=True)
            except Exception as img_err:
                st.error(f"Image data could not be displayed: {img_err}")
        else:
            # Daha fazla hata mesajı ve response içeriğini göster
            st.warning(
                "Could not generate an image from the prompt. "
                "The model might have refused the request, or the response format is unsupported. "
                f"Raw response: {getattr(response, 'candidates', None) or getattr(response, 'media', None)}"
            )

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
