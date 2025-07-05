import streamlit as st
from horror_story_app.models.story import StoryInDB

def story_display(story: StoryInDB):
    """
    Displays a single story with its title, content, and a download button.

    Args:
        story: The StoryInDB object to display.
    """
    if not story:
        return

    st.subheader(f"📜 {story.title}")
    st.markdown("---")
    
    # Use a container with a border for better visual separation
    with st.container(border=True):
        st.markdown(story.content)

    st.markdown("---")

    # Prepare the content for the download button
    downloadable_content = f"Title: {story.title}\n\n{story.content}"
    
    st.download_button(
        label="📄 Download Story",
        data=downloadable_content,
        file_name=f"{story.title.replace(' ', '_').lower()}.txt",
        mime="text/plain",
        help="Download this story as a .txt file"
    )

if __name__ == '__main__':
    # This is an example of how to use the component.
    # In a real app, you would pass a StoryInDB object from your service.
    
    st.title("Story Display Component Preview")

    # Create a mock story object for demonstration
    mock_story_data = {
        "id": 1,
        "user_id": 1,
        "title": "The Phantom of the Library",
        "content": "The old library was silent, a tomb of forgotten words. Elara traced the spine of a dusty tome, its leather cracked like dry skin. As her fingers brushed the cover, a whisper, cold and sharp, slithered from the pages, coiling around her wrist. It wasn't a word, but a feeling—a chilling premonition of being watched by eyes that no longer existed.\n\nThe whisper grew, weaving through the shelves, a phantom melody of forgotten lives. The book in her hand pulsed with a faint, sickly light. It was a diary, she realized, and the last entry was a frantic scrawl: *'It reads you back.'*",
        "user_request": "A story about a haunted book.",
        "created_at": "2023-10-31 10:00:00"
    }
    mock_story = StoryInDB(**mock_story_data)
    
    story_display(mock_story) 