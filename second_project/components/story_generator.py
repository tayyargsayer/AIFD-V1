import streamlit as st
from horror_story_app.services.story_service import StoryService
from horror_story_app.components.story_display import story_display

def story_generator():
    """
    Displays the main story generation interface.
    This includes input fields for the story request and preferences,
    a button to generate the story, and a display for the result.
    """
    st.subheader("🖋️ Weave Your Nightmare")
    st.markdown("Describe the terror you wish to unleash upon the world.")

    # Initialize StoryService
    story_service = StoryService()

    # --- Story Request Inputs ---
    user_request = st.text_area(
        "What is the story about?",
        placeholder="e.g., A group of friends find a cursed board game.",
        max_chars=500,
        help="Describe the basic plot of your horror story (max 500 characters)."
    )

    col1, col2 = st.columns(2)
    with col1:
        story_type = st.selectbox(
            "Style of Horror",
            ("Cosmic Horror (Lovecraftian)", "Gothic Horror (Poe, Shelley)", "Slasher (80s movie style)", "Psychological Thriller", "Supernatural/Paranormal"),
            help="Choose the overall tone and style."
        )
        story_length = st.select_slider(
            "Story Length",
            options=["flash fiction (1 paragraph)", "short (3-4 paragraphs)", "medium (5-7 paragraphs)"],
            value="short (3-4 paragraphs)",
            help="How long should the story be?"
        )
    with col2:
        horror_elements = st.multiselect(
            "Key Horror Elements",
            ("Monsters", "Ghosts", "Cursed Objects", "Body Horror", "Isolation", "Madness", "Dark Rituals"),
            help="Select up to 3 key elements to include."
        )

    # --- Generate Button ---
    if st.button("Conjure the Story", type="primary", use_container_width=True):
        if not user_request:
            st.warning("You must provide a story request before conjuring.")
        elif 'user_id' not in st.session_state:
            st.error("Cannot generate story. Please confirm your identity above first.")
        else:
            with st.spinner("The spirits are writing... Please wait."):
                preferences = {
                    "type": story_type,
                    "length": story_length,
                    "elements": horror_elements,
                }
                
                new_story = story_service.generate_and_save_story(
                    user_id=st.session_state.user_id,
                    user_request=user_request,
                    preferences=preferences
                )

                if new_story:
                    st.session_state['latest_story'] = new_story
                    st.success("A new horror has been born!")
                    st.balloons()
                else:
                    st.error("The spirits were unable to complete the story. It may have been too terrifying... or an error occurred. Please try again.")

    # --- Display Area ---
    # Display the most recently generated story if it exists in the session state
    if 'latest_story' in st.session_state:
        st.divider()
        st.subheader("Your Latest Creation")
        story_display(st.session_state.latest_story) 