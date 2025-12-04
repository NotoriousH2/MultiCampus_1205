"""Sora 2 Video Generator - Streamlit Application.

A Streamlit application for generating videos using OpenAI's Sora 2 API.
Supports text-to-video and image-to-video generation with progress tracking.
"""

import sys
from pathlib import Path

import streamlit as st

# Add the app directory to path for imports
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from components.sidebar import render_sidebar
from components.video_form import render_video_form
from components.video_display import render_video_display


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Sora 2 Video Generator",
        page_icon="[VIDEO]",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        .main > div {
            padding-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # App title
    st.title("Sora 2 Video Generator")
    st.markdown("Generate videos using OpenAI's Sora 2 API")

    # Render sidebar and get settings
    settings = render_sidebar()

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        # Video generation form
        form_data = render_video_form(settings)

    with col2:
        # Video results display
        render_video_display(form_data, settings.get("api_key", ""))

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9em;">
        Powered by OpenAI Sora 2 API |
        <a href="https://platform.openai.com/docs/guides/video-generation" target="_blank">Documentation</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
