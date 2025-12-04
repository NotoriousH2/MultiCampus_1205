"""Sidebar component for API key input and model selection."""

import streamlit as st

from services.sora_api import VideoModel, VideoSize, validate_api_key
from utils.storage import APIKeyStorage


def render_sidebar() -> dict:
    """Render the sidebar with API key input and model settings.

    Returns:
        Dictionary with selected settings.
    """
    with st.sidebar:
        st.header("Settings")

        # API Key Section
        st.subheader("OpenAI API Key")

        # Load saved API key
        saved_key = APIKeyStorage.get_api_key()
        if saved_key and "api_key_input" not in st.session_state:
            st.session_state.api_key_input = saved_key

        # API key input
        api_key = st.text_input(
            "API Key",
            type="password",
            key="api_key_input",
            placeholder="sk-...",
            help="Enter your OpenAI API key. It will be stored securely."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Save Key", use_container_width=True):
                if api_key:
                    with st.spinner("Validating..."):
                        if validate_api_key(api_key):
                            APIKeyStorage.set_api_key(api_key, save_locally=True)
                            st.success("Saved!")
                        else:
                            st.error("Invalid API key")
                else:
                    st.warning("Enter a key first")

        with col2:
            if st.button("Clear Key", use_container_width=True):
                APIKeyStorage.clear_local()
                if "api_key" in st.session_state:
                    del st.session_state.api_key
                if "api_key_input" in st.session_state:
                    st.session_state.api_key_input = ""
                st.rerun()

        # Show API key status
        if APIKeyStorage.is_api_key_set():
            st.success("API Key is configured")
        else:
            st.warning("API Key not set")

        st.divider()

        # Model Selection
        st.subheader("Model Settings")

        model = st.selectbox(
            "Model",
            options=[m.value for m in VideoModel],
            format_func=lambda x: {
                "sora-2": "Sora 2 (Fast)",
                "sora-2-pro": "Sora 2 Pro (High Quality)"
            }.get(x, x),
            help="sora-2 is faster, sora-2-pro produces higher quality output"
        )

        # Video Resolution
        size = st.selectbox(
            "Resolution",
            options=[s.value for s in VideoSize],
            index=1,  # Default to 720p
            format_func=lambda x: {
                "854x480": "480p (854x480)",
                "1280x720": "720p (1280x720)",
                "1920x1080": "1080p (1920x1080)"
            }.get(x, x),
            help="Higher resolution takes longer to generate"
        )

        # Video Duration
        seconds = st.slider(
            "Duration (seconds)",
            min_value=1,
            max_value=20,
            value=5,
            help="Video length in seconds"
        )

        st.divider()

        # Info section
        st.subheader("Info")
        st.markdown("""
        **Sora 2** - Fast generation for quick iterations

        **Sora 2 Pro** - Higher quality for production use

        **Tips:**
        - Describe shot type, subject, action, setting, and lighting
        - Be specific to get consistent results
        - Images must match the selected resolution
        """)

        return {
            "api_key": api_key or saved_key,
            "model": model,
            "size": size,
            "seconds": seconds
        }
