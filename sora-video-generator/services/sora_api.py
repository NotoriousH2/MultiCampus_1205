"""Sora API service for video generation."""

import base64
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from openai import OpenAI


class VideoStatus(Enum):
    """Video generation status."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoModel(Enum):
    """Available Sora models."""
    SORA_2 = "sora-2"
    SORA_2_PRO = "sora-2-pro"


class VideoSize(Enum):
    """Available video sizes."""
    SIZE_480P = "854x480"
    SIZE_720P = "1280x720"
    SIZE_1080P = "1920x1080"


@dataclass
class VideoJob:
    """Video generation job information."""
    id: str
    status: VideoStatus
    progress: int
    model: str
    size: str
    seconds: int
    error_message: Optional[str] = None
    created_at: Optional[int] = None


class SoraAPIService:
    """Service for interacting with OpenAI Sora API."""

    def __init__(self, api_key: str):
        """Initialize the Sora API service.

        Args:
            api_key: OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)

    def create_video(
        self,
        prompt: str,
        model: str = "sora-2",
        size: str = "1280x720",
        seconds: int = 5,
        input_image: Optional[bytes] = None,
        image_mime_type: str = "image/jpeg"
    ) -> VideoJob:
        """Create a new video generation job.

        Args:
            prompt: Text description of the video to generate.
            model: Model to use (sora-2 or sora-2-pro).
            size: Video resolution.
            seconds: Video duration in seconds.
            input_image: Optional image bytes to use as first frame.
            image_mime_type: MIME type of the input image.

        Returns:
            VideoJob with job information.
        """
        kwargs = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "seconds": seconds,
        }

        if input_image is not None:
            # Encode image to base64 data URL
            base64_image = base64.b64encode(input_image).decode("utf-8")
            data_url = f"data:{image_mime_type};base64,{base64_image}"
            kwargs["input_reference"] = data_url

        video = self.client.videos.create(**kwargs)

        return self._parse_video_response(video)

    def get_video_status(self, video_id: str) -> VideoJob:
        """Get the current status of a video generation job.

        Args:
            video_id: The video job ID.

        Returns:
            VideoJob with current status.
        """
        video = self.client.videos.retrieve(video_id)
        return self._parse_video_response(video)

    def poll_until_complete(
        self,
        video_id: str,
        poll_interval: float = 5.0,
        progress_callback: Optional[Callable[[VideoJob], None]] = None,
        max_attempts: int = 360  # 30 minutes max
    ) -> VideoJob:
        """Poll video status until completion.

        Args:
            video_id: The video job ID.
            poll_interval: Seconds between polls.
            progress_callback: Optional callback for progress updates.
            max_attempts: Maximum number of poll attempts.

        Returns:
            Final VideoJob status.
        """
        attempts = 0
        while attempts < max_attempts:
            job = self.get_video_status(video_id)

            if progress_callback:
                progress_callback(job)

            if job.status in (VideoStatus.COMPLETED, VideoStatus.FAILED):
                return job

            time.sleep(poll_interval)
            attempts += 1

        # Timeout - return last known status
        return self.get_video_status(video_id)

    def download_video(self, video_id: str) -> bytes:
        """Download the completed video as bytes.

        Args:
            video_id: The video job ID.

        Returns:
            Video file bytes.
        """
        content = self.client.videos.download_content(video_id, variant="video")
        return content.read()

    def download_thumbnail(self, video_id: str) -> bytes:
        """Download the video thumbnail.

        Args:
            video_id: The video job ID.

        Returns:
            Thumbnail image bytes.
        """
        content = self.client.videos.download_content(video_id, variant="thumbnail")
        return content.read()

    def list_videos(self, limit: int = 20, after: Optional[str] = None) -> list[VideoJob]:
        """List recent video generation jobs.

        Args:
            limit: Maximum number of videos to return.
            after: Cursor for pagination.

        Returns:
            List of VideoJob objects.
        """
        kwargs = {"limit": limit}
        if after:
            kwargs["after"] = after

        response = self.client.videos.list(**kwargs)
        return [self._parse_video_response(v) for v in response.data]

    def delete_video(self, video_id: str) -> bool:
        """Delete a video from OpenAI storage.

        Args:
            video_id: The video job ID.

        Returns:
            True if deleted successfully.
        """
        self.client.videos.delete(video_id)
        return True

    def _parse_video_response(self, video) -> VideoJob:
        """Parse API response into VideoJob.

        Args:
            video: API response object.

        Returns:
            VideoJob instance.
        """
        status_str = getattr(video, "status", "queued")
        try:
            status = VideoStatus(status_str)
        except ValueError:
            status = VideoStatus.QUEUED

        error_message = None
        if hasattr(video, "error") and video.error:
            error_message = getattr(video.error, "message", str(video.error))

        return VideoJob(
            id=video.id,
            status=status,
            progress=getattr(video, "progress", 0) or 0,
            model=getattr(video, "model", "sora-2"),
            size=getattr(video, "size", "1280x720"),
            seconds=int(getattr(video, "seconds", 5) or 5),
            error_message=error_message,
            created_at=getattr(video, "created_at", None),
        )


def validate_api_key(api_key: str) -> bool:
    """Validate an OpenAI API key by making a simple API call.

    Args:
        api_key: The API key to validate.

    Returns:
        True if the key is valid, False otherwise.
    """
    try:
        client = OpenAI(api_key=api_key)
        # Simple validation - list models
        client.models.list()
        return True
    except Exception:
        return False
