"""Video result display component."""

import base64
import time
from typing import Optional

import streamlit as st

from services.sora_api import SoraAPIService, VideoJob, VideoStatus


def render_video_display(form_data: Optional[dict], api_key: str) -> None:
    """Render video generation progress and results.

    Args:
        form_data: Form submission data or None.
        api_key: OpenAI API key.
    """
    st.header("Results")

    # Initialize session state for video jobs
    if "video_jobs" not in st.session_state:
        st.session_state.video_jobs = []

    # Process new form submission
    if form_data:
        _start_video_generation(form_data, api_key)

    # Display video jobs
    if not st.session_state.video_jobs:
        st.info("No videos generated yet. Use the form above to create a video.")
        return

    # Display jobs in reverse order (newest first)
    for i, job_data in enumerate(reversed(st.session_state.video_jobs)):
        job_index = len(st.session_state.video_jobs) - 1 - i
        _render_job_card(job_data, job_index, api_key)


def _start_video_generation(form_data: dict, api_key: str) -> None:
    """Start a new video generation job.

    Args:
        form_data: Form submission data.
        api_key: OpenAI API key.
    """
    try:
        service = SoraAPIService(api_key)

        with st.spinner("Starting video generation..."):
            job = service.create_video(
                prompt=form_data["prompt"],
                model=form_data["model"],
                size=form_data["size"],
                seconds=form_data["seconds"],
                input_image=form_data.get("input_image"),
                image_mime_type=form_data.get("image_mime_type", "image/jpeg")
            )

        # Store job data
        job_data = {
            "job": job,
            "prompt": form_data["prompt"],
            "video_bytes": None,
            "start_time": time.time()
        }
        st.session_state.video_jobs.append(job_data)

        st.success(f"Video generation started! Job ID: {job.id}")
        st.balloons()

    except Exception as e:
        st.error(f"Failed to start video generation: {str(e)}")


def _render_job_card(job_data: dict, job_index: int, api_key: str) -> None:
    """Render a single video job card.

    Args:
        job_data: Job data dictionary.
        job_index: Index in the jobs list.
        api_key: OpenAI API key.
    """
    job: VideoJob = job_data["job"]

    with st.container(border=True):
        # Header with status
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            status_emoji = {
                VideoStatus.QUEUED: "...",
                VideoStatus.IN_PROGRESS: "...",
                VideoStatus.COMPLETED: "[OK]",
                VideoStatus.FAILED: "[X]"
            }
            st.subheader(f"{status_emoji.get(job.status, '')} Job {job.id[:20]}...")

        with col2:
            st.caption(f"Model: {job.model}")

        with col3:
            st.caption(f"{job.size} | {job.seconds}s")

        # Prompt
        with st.expander("Prompt", expanded=False):
            st.text(job_data["prompt"])

        # Status-specific rendering
        if job.status == VideoStatus.COMPLETED:
            _render_completed_job(job_data, job_index, api_key)
        elif job.status == VideoStatus.FAILED:
            _render_failed_job(job)
        else:
            _render_in_progress_job(job_data, job_index, api_key)


def _render_completed_job(job_data: dict, job_index: int, api_key: str) -> None:
    """Render a completed video job.

    Args:
        job_data: Job data dictionary.
        job_index: Index in the jobs list.
        api_key: OpenAI API key.
    """
    job: VideoJob = job_data["job"]
    st.success("Video generation completed!")

    # Download video if not already downloaded
    if job_data.get("video_bytes") is None:
        try:
            with st.spinner("Downloading video..."):
                service = SoraAPIService(api_key)
                job_data["video_bytes"] = service.download_video(job.id)
                st.session_state.video_jobs[job_index] = job_data
        except Exception as e:
            st.error(f"Failed to download video: {str(e)}")
            return

    video_bytes = job_data["video_bytes"]

    # Display video player
    st.video(video_bytes)

    # Download button
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download MP4",
            data=video_bytes,
            file_name=f"sora_video_{job.id[:10]}.mp4",
            mime="video/mp4",
            use_container_width=True
        )

    with col2:
        elapsed = job_data.get("elapsed_time", 0)
        if elapsed:
            st.caption(f"Generated in {elapsed:.1f} seconds")


def _render_failed_job(job: VideoJob) -> None:
    """Render a failed video job.

    Args:
        job: VideoJob instance.
    """
    st.error("Video generation failed!")
    if job.error_message:
        st.error(f"Error: {job.error_message}")


def _render_in_progress_job(job_data: dict, job_index: int, api_key: str) -> None:
    """Render an in-progress video job.

    Args:
        job_data: Job data dictionary.
        job_index: Index in the jobs list.
        api_key: OpenAI API key.
    """
    job: VideoJob = job_data["job"]

    # Progress bar
    progress_text = "Queued..." if job.status == VideoStatus.QUEUED else f"Generating: {job.progress}%"
    progress_bar = st.progress(job.progress / 100, text=progress_text)

    # Elapsed time
    elapsed = time.time() - job_data.get("start_time", time.time())
    st.caption(f"Elapsed: {elapsed:.0f} seconds")

    # Refresh button
    if st.button("Refresh Status", key=f"refresh_{job_index}"):
        _refresh_job_status(job_data, job_index, api_key)
        st.rerun()

    # Auto-refresh with polling
    _auto_refresh_job(job_data, job_index, api_key)


def _refresh_job_status(job_data: dict, job_index: int, api_key: str) -> None:
    """Refresh the status of a video job.

    Args:
        job_data: Job data dictionary.
        job_index: Index in the jobs list.
        api_key: OpenAI API key.
    """
    try:
        service = SoraAPIService(api_key)
        updated_job = service.get_video_status(job_data["job"].id)
        job_data["job"] = updated_job

        if updated_job.status == VideoStatus.COMPLETED:
            job_data["elapsed_time"] = time.time() - job_data.get("start_time", time.time())

        st.session_state.video_jobs[job_index] = job_data
    except Exception as e:
        st.error(f"Failed to refresh status: {str(e)}")


def _auto_refresh_job(job_data: dict, job_index: int, api_key: str) -> None:
    """Auto-refresh job status using Streamlit's rerun.

    Args:
        job_data: Job data dictionary.
        job_index: Index in the jobs list.
        api_key: OpenAI API key.
    """
    job: VideoJob = job_data["job"]

    # Only auto-refresh for in-progress jobs
    if job.status not in (VideoStatus.QUEUED, VideoStatus.IN_PROGRESS):
        return

    # Check if enough time has passed since last refresh
    last_refresh = job_data.get("last_refresh", 0)
    current_time = time.time()

    if current_time - last_refresh >= 10:  # Refresh every 10 seconds
        job_data["last_refresh"] = current_time
        _refresh_job_status(job_data, job_index, api_key)

        # Show notification if completed
        if job_data["job"].status == VideoStatus.COMPLETED:
            st.balloons()
            st.toast("Video generation completed!", icon="[OK]")

        st.rerun()
