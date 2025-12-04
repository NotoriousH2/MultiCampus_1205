"""Video generation form component."""

from typing import Optional

import streamlit as st


def render_video_form(settings: dict) -> Optional[dict]:
    """Render the video generation form.

    Args:
        settings: Dictionary with model settings from sidebar.

    Returns:
        Dictionary with form data if submitted, None otherwise.
    """
    st.header("Generate Video")

    # Generation mode tabs
    tab_prompt, tab_image = st.tabs(["Text to Video", "Image to Video"])

    with tab_prompt:
        prompt_only_form = _render_prompt_only_form(settings)
        if prompt_only_form:
            return prompt_only_form

    with tab_image:
        image_form = _render_image_form(settings)
        if image_form:
            return image_form

    return None


def _render_prompt_only_form(settings: dict) -> Optional[dict]:
    """Render text-to-video form.

    Args:
        settings: Dictionary with model settings.

    Returns:
        Form data if submitted, None otherwise.
    """
    with st.form("prompt_form"):
        st.markdown("### Text to Video")
        st.markdown("Describe the video you want to generate.")

        prompt = st.text_area(
            "Prompt",
            height=150,
            placeholder="Example: Wide shot of a child flying a red kite in a grassy park, golden hour sunlight, camera slowly pans upward.",
            help="Describe shot type, subject, action, setting, and lighting for best results."
        )

        # Example prompts
        with st.expander("Example Prompts"):
            st.markdown("""
            - **Nature:** "Aerial drone shot flying over a misty mountain range at sunrise, golden light filtering through clouds"
            - **Urban:** "Time-lapse of a busy city intersection at night, neon lights reflecting on wet pavement"
            - **Abstract:** "Colorful ink drops falling into water in slow motion, swirling and mixing together"
            - **Product:** "Close-up of a steaming coffee cup on a wooden table, morning light through blinds, soft depth of field"
            """)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"Model: {settings['model']} | Size: {settings['size']} | Duration: {settings['seconds']}s")
        with col2:
            submitted = st.form_submit_button("Generate", type="primary", use_container_width=True)

        if submitted:
            if not prompt:
                st.error("Please enter a prompt.")
                return None
            if not settings.get("api_key"):
                st.error("Please configure your API key in the sidebar.")
                return None

            return {
                "prompt": prompt,
                "model": settings["model"],
                "size": settings["size"],
                "seconds": settings["seconds"],
                "input_image": None
            }

    return None


def _render_image_form(settings: dict) -> Optional[dict]:
    """Render image-to-video form.

    Args:
        settings: Dictionary with model settings.

    Returns:
        Form data if submitted, None otherwise.
    """
    with st.form("image_form"):
        st.markdown("### Image to Video")
        st.markdown("Upload an image to use as the first frame of your video.")

        # Image upload
        uploaded_file = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png", "webp"],
            help="The image will be used as the first frame. Should match the selected resolution."
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Preview", use_container_width=True)

        prompt = st.text_area(
            "Prompt",
            height=100,
            placeholder="Example: The subject slowly turns around and smiles, then walks out of frame.",
            help="Describe what should happen in the video starting from your image."
        )

        # Warnings
        st.info("""
        **Note:**
        - Image resolution should match selected video size
        - Images with human faces may be rejected
        - Supported formats: JPEG, PNG, WebP
        """)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"Model: {settings['model']} | Size: {settings['size']} | Duration: {settings['seconds']}s")
        with col2:
            submitted = st.form_submit_button("Generate", type="primary", use_container_width=True)

        if submitted:
            if not prompt:
                st.error("Please enter a prompt.")
                return None
            if not uploaded_file:
                st.error("Please upload an image.")
                return None
            if not settings.get("api_key"):
                st.error("Please configure your API key in the sidebar.")
                return None

            # Read image bytes
            image_bytes = uploaded_file.read()

            # Determine MIME type
            mime_type = uploaded_file.type or "image/jpeg"

            return {
                "prompt": prompt,
                "model": settings["model"],
                "size": settings["size"],
                "seconds": settings["seconds"],
                "input_image": image_bytes,
                "image_mime_type": mime_type
            }

    return None
