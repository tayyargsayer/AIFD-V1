import streamlit as st
from horror_story_app.services.user_service import UserService

def user_form():
    """
    Displays a form for the user to enter their information.
    Handles form submission to create a new user.
    Stores the user's ID in the session state upon successful creation.
    """
    st.subheader("👤 Who are you, brave reader?")
    st.markdown("We need to know who is daring to create these tales of terror.")

    # Initialize UserService
    user_service = UserService()

    with st.form(key="user_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", help="Please enter your first name (letters only).")
        with col2:
            last_name = st.text_input("Last Name", help="Please enter your last name (letters only).")
        
        age = st.number_input("Age", min_value=13, max_value=99, value=18, help="You must be between 13 and 99 to proceed.")
        
        submitted = st.form_submit_button("Confirm Identity")

        if submitted:
            if not first_name or not last_name:
                st.error("Please enter both your first and last name.")
            else:
                with st.spinner("Verifying your identity..."):
                    try:
                        # Attempt to create the user
                        user_id = user_service.create_user(
                            first_name=first_name,
                            last_name=last_name,
                            age=age
                        )

                        if user_id:
                            st.session_state['user_id'] = user_id
                            st.session_state['user_name'] = f"{first_name} {last_name}"
                            st.success(f"Welcome, {first_name}! Your identity has been recorded.")
                            # Rerun to update the UI state
                            st.rerun()
                        else:
                            # Error message from service is printed to console, show generic error to user
                            st.error("There was a problem verifying your identity. Please check your inputs (e.g., names should not contain numbers) and try again.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}") 