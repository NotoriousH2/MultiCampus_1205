"""영상 결과 표시 컴포넌트."""

import time
from typing import Optional

import streamlit as st

from services.sora_api import SoraAPIService, VideoJob, VideoStatus


def render_video_display(form_data: Optional[dict], api_key: str) -> None:
    """영상 생성 진행 상황 및 결과를 렌더링합니다.

    Args:
        form_data: 폼 제출 데이터 또는 None.
        api_key: OpenAI API 키.
    """
    st.header("결과")

    # 영상 작업을 위한 세션 상태 초기화
    if "video_jobs" not in st.session_state:
        st.session_state.video_jobs = []

    # 새 폼 제출 처리
    if form_data:
        _start_video_generation(form_data, api_key)

    # 영상 작업 표시
    if not st.session_state.video_jobs:
        st.info("아직 생성된 영상이 없습니다. 위의 폼을 사용하여 영상을 만들어보세요.")
        return

    # 역순으로 작업 표시 (최신 순)
    for i, job_data in enumerate(reversed(st.session_state.video_jobs)):
        job_index = len(st.session_state.video_jobs) - 1 - i
        _render_job_card(job_data, job_index, api_key)


def _start_video_generation(form_data: dict, api_key: str) -> None:
    """새 영상 생성 작업을 시작합니다.

    Args:
        form_data: 폼 제출 데이터.
        api_key: OpenAI API 키.
    """
    try:
        service = SoraAPIService(api_key)

        with st.spinner("영상 생성을 시작하는 중..."):
            job = service.create_video(
                prompt=form_data["prompt"],
                model=form_data["model"],
                size=form_data["size"],
                seconds=form_data["seconds"],
                input_image=form_data.get("input_image"),
                image_mime_type=form_data.get("image_mime_type", "image/jpeg")
            )

        # 작업 데이터 저장
        job_data = {
            "job": job,
            "prompt": form_data["prompt"],
            "video_bytes": None,
            "start_time": time.time()
        }
        st.session_state.video_jobs.append(job_data)

        st.success(f"영상 생성이 시작되었습니다! 작업 ID: {job.id}")
        st.balloons()

    except Exception as e:
        st.error(f"영상 생성 시작 실패: {str(e)}")


def _render_job_card(job_data: dict, job_index: int, api_key: str) -> None:
    """개별 영상 작업 카드를 렌더링합니다.

    Args:
        job_data: 작업 데이터 딕셔너리.
        job_index: 작업 목록에서의 인덱스.
        api_key: OpenAI API 키.
    """
    job: VideoJob = job_data["job"]

    with st.container(border=True):
        # 상태가 포함된 헤더
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            status_text = {
                VideoStatus.QUEUED: "[대기중]",
                VideoStatus.IN_PROGRESS: "[생성중]",
                VideoStatus.COMPLETED: "[완료]",
                VideoStatus.FAILED: "[실패]"
            }
            st.subheader(f"{status_text.get(job.status, '')} 작업 {job.id[:20]}...")

        with col2:
            st.caption(f"모델: {job.model}")

        with col3:
            st.caption(f"{job.size} | {job.seconds}초")

        # 프롬프트
        with st.expander("프롬프트", expanded=False):
            st.text(job_data["prompt"])

        # 상태별 렌더링
        if job.status == VideoStatus.COMPLETED:
            _render_completed_job(job_data, job_index, api_key)
        elif job.status == VideoStatus.FAILED:
            _render_failed_job(job)
        else:
            _render_in_progress_job(job_data, job_index, api_key)


def _render_completed_job(job_data: dict, job_index: int, api_key: str) -> None:
    """완료된 영상 작업을 렌더링합니다.

    Args:
        job_data: 작업 데이터 딕셔너리.
        job_index: 작업 목록에서의 인덱스.
        api_key: OpenAI API 키.
    """
    job: VideoJob = job_data["job"]
    st.success("영상 생성이 완료되었습니다!")

    # 아직 다운로드하지 않은 경우 영상 다운로드
    if job_data.get("video_bytes") is None:
        try:
            with st.spinner("영상 다운로드 중..."):
                service = SoraAPIService(api_key)
                job_data["video_bytes"] = service.download_video(job.id)
                st.session_state.video_jobs[job_index] = job_data
        except Exception as e:
            st.error(f"영상 다운로드 실패: {str(e)}")
            return

    video_bytes = job_data["video_bytes"]

    # 영상 플레이어 표시
    st.video(video_bytes)

    # 다운로드 버튼
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="MP4 다운로드",
            data=video_bytes,
            file_name=f"sora_video_{job.id[:10]}.mp4",
            mime="video/mp4",
            use_container_width=True
        )

    with col2:
        elapsed = job_data.get("elapsed_time", 0)
        if elapsed:
            st.caption(f"생성 소요 시간: {elapsed:.1f}초")


def _render_failed_job(job: VideoJob) -> None:
    """실패한 영상 작업을 렌더링합니다.

    Args:
        job: VideoJob 인스턴스.
    """
    st.error("영상 생성에 실패했습니다!")
    if job.error_message:
        st.error(f"오류: {job.error_message}")


def _render_in_progress_job(job_data: dict, job_index: int, api_key: str) -> None:
    """진행 중인 영상 작업을 렌더링합니다.

    Args:
        job_data: 작업 데이터 딕셔너리.
        job_index: 작업 목록에서의 인덱스.
        api_key: OpenAI API 키.
    """
    job: VideoJob = job_data["job"]

    # 진행률 표시줄
    progress_text = "대기 중..." if job.status == VideoStatus.QUEUED else f"생성 중: {job.progress}%"
    st.progress(job.progress / 100, text=progress_text)

    # 경과 시간
    elapsed = time.time() - job_data.get("start_time", time.time())
    st.caption(f"경과 시간: {elapsed:.0f}초")

    # 새로고침 버튼
    if st.button("상태 새로고침", key=f"refresh_{job_index}"):
        _refresh_job_status(job_data, job_index, api_key)
        st.rerun()

    # 폴링을 통한 자동 새로고침
    _auto_refresh_job(job_data, job_index, api_key)


def _refresh_job_status(job_data: dict, job_index: int, api_key: str) -> None:
    """영상 작업의 상태를 새로고침합니다.

    Args:
        job_data: 작업 데이터 딕셔너리.
        job_index: 작업 목록에서의 인덱스.
        api_key: OpenAI API 키.
    """
    try:
        service = SoraAPIService(api_key)
        updated_job = service.get_video_status(job_data["job"].id)
        job_data["job"] = updated_job

        if updated_job.status == VideoStatus.COMPLETED:
            job_data["elapsed_time"] = time.time() - job_data.get("start_time", time.time())

        st.session_state.video_jobs[job_index] = job_data
    except Exception as e:
        st.error(f"상태 새로고침 실패: {str(e)}")


def _auto_refresh_job(job_data: dict, job_index: int, api_key: str) -> None:
    """Streamlit의 rerun을 사용하여 작업 상태를 자동 새로고침합니다.

    Args:
        job_data: 작업 데이터 딕셔너리.
        job_index: 작업 목록에서의 인덱스.
        api_key: OpenAI API 키.
    """
    job: VideoJob = job_data["job"]

    # 진행 중인 작업만 자동 새로고침
    if job.status not in (VideoStatus.QUEUED, VideoStatus.IN_PROGRESS):
        return

    # 마지막 새로고침 이후 충분한 시간이 경과했는지 확인
    last_refresh = job_data.get("last_refresh", 0)
    current_time = time.time()

    if current_time - last_refresh >= 10:  # 10초마다 새로고침
        job_data["last_refresh"] = current_time
        _refresh_job_status(job_data, job_index, api_key)

        # 완료 시 알림 표시
        if job_data["job"].status == VideoStatus.COMPLETED:
            st.balloons()
            st.toast("영상 생성이 완료되었습니다!", icon="[OK]")

        st.rerun()
