"""Sora API 서비스 - 영상 생성."""

import base64
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from openai import OpenAI


class VideoStatus(Enum):
    """영상 생성 상태."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoModel(Enum):
    """사용 가능한 Sora 모델."""
    SORA_2 = "sora-2"
    SORA_2_PRO = "sora-2-pro"


class VideoSize(Enum):
    """사용 가능한 영상 해상도."""
    SIZE_480P = "854x480"
    SIZE_720P = "1280x720"
    SIZE_1080P = "1920x1080"


class VideoDuration(Enum):
    """사용 가능한 영상 길이 (초)."""
    SEC_4 = "4"
    SEC_8 = "8"
    SEC_12 = "12"


@dataclass
class VideoJob:
    """영상 생성 작업 정보."""
    id: str
    status: VideoStatus
    progress: int
    model: str
    size: str
    seconds: str
    error_message: Optional[str] = None
    created_at: Optional[int] = None


class SoraAPIService:
    """OpenAI Sora API 서비스."""

    def __init__(self, api_key: str):
        """Sora API 서비스 초기화.

        Args:
            api_key: OpenAI API 키.
        """
        self.client = OpenAI(api_key=api_key)

    def create_video(
        self,
        prompt: str,
        model: str = "sora-2",
        size: str = "1280x720",
        seconds: str = "8",
        input_image: Optional[bytes] = None,
        image_mime_type: str = "image/jpeg"
    ) -> VideoJob:
        """새 영상 생성 작업을 시작합니다.

        Args:
            prompt: 생성할 영상에 대한 텍스트 설명.
            model: 사용할 모델 (sora-2 또는 sora-2-pro).
            size: 영상 해상도.
            seconds: 영상 길이 (초) - '4', '8', '12' 중 하나.
            input_image: 첫 프레임으로 사용할 이미지 바이트 (선택).
            image_mime_type: 입력 이미지의 MIME 타입.

        Returns:
            작업 정보가 담긴 VideoJob.
        """
        kwargs = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "seconds": seconds,
        }

        if input_image is not None:
            # 이미지를 base64 데이터 URL로 인코딩
            base64_image = base64.b64encode(input_image).decode("utf-8")
            data_url = f"data:{image_mime_type};base64,{base64_image}"
            kwargs["input_reference"] = data_url

        video = self.client.videos.create(**kwargs)

        return self._parse_video_response(video)

    def get_video_status(self, video_id: str) -> VideoJob:
        """영상 생성 작업의 현재 상태를 가져옵니다.

        Args:
            video_id: 영상 작업 ID.

        Returns:
            현재 상태가 담긴 VideoJob.
        """
        video = self.client.videos.retrieve(video_id)
        return self._parse_video_response(video)

    def poll_until_complete(
        self,
        video_id: str,
        poll_interval: float = 5.0,
        progress_callback: Optional[Callable[[VideoJob], None]] = None,
        max_attempts: int = 360  # 최대 30분
    ) -> VideoJob:
        """완료될 때까지 영상 상태를 폴링합니다.

        Args:
            video_id: 영상 작업 ID.
            poll_interval: 폴링 간격 (초).
            progress_callback: 진행 상황 업데이트 콜백 (선택).
            max_attempts: 최대 폴링 시도 횟수.

        Returns:
            최종 VideoJob 상태.
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

        # 타임아웃 - 마지막으로 알려진 상태 반환
        return self.get_video_status(video_id)

    def download_video(self, video_id: str) -> bytes:
        """완성된 영상을 바이트로 다운로드합니다.

        Args:
            video_id: 영상 작업 ID.

        Returns:
            영상 파일 바이트.
        """
        content = self.client.videos.download_content(video_id, variant="video")
        return content.read()

    def download_thumbnail(self, video_id: str) -> bytes:
        """영상 썸네일을 다운로드합니다.

        Args:
            video_id: 영상 작업 ID.

        Returns:
            썸네일 이미지 바이트.
        """
        content = self.client.videos.download_content(video_id, variant="thumbnail")
        return content.read()

    def list_videos(self, limit: int = 20, after: Optional[str] = None) -> list[VideoJob]:
        """최근 영상 생성 작업 목록을 가져옵니다.

        Args:
            limit: 반환할 최대 영상 수.
            after: 페이지네이션 커서.

        Returns:
            VideoJob 객체 목록.
        """
        kwargs = {"limit": limit}
        if after:
            kwargs["after"] = after

        response = self.client.videos.list(**kwargs)
        return [self._parse_video_response(v) for v in response.data]

    def delete_video(self, video_id: str) -> bool:
        """OpenAI 저장소에서 영상을 삭제합니다.

        Args:
            video_id: 영상 작업 ID.

        Returns:
            성공적으로 삭제되면 True.
        """
        self.client.videos.delete(video_id)
        return True

    def _parse_video_response(self, video) -> VideoJob:
        """API 응답을 VideoJob으로 파싱합니다.

        Args:
            video: API 응답 객체.

        Returns:
            VideoJob 인스턴스.
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
            seconds=str(getattr(video, "seconds", "8") or "8"),
            error_message=error_message,
            created_at=getattr(video, "created_at", None),
        )


def validate_api_key(api_key: str) -> bool:
    """OpenAI API 키를 간단한 API 호출로 검증합니다.

    Args:
        api_key: 검증할 API 키.

    Returns:
        키가 유효하면 True, 아니면 False.
    """
    try:
        client = OpenAI(api_key=api_key)
        # 간단한 검증 - 모델 목록 조회
        client.models.list()
        return True
    except Exception:
        return False
