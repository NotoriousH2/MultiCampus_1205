"""Sora 2 영상 생성기 - Streamlit 애플리케이션.

OpenAI의 Sora 2 API를 사용하여 영상을 생성하는 Streamlit 애플리케이션입니다.
텍스트-투-비디오와 이미지-투-비디오 생성을 지원하며 진행 상황을 추적합니다.
"""

import sys
from pathlib import Path

import streamlit as st

# 임포트를 위해 앱 디렉토리를 경로에 추가
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from components.sidebar import render_sidebar
from components.video_form import render_video_form
from components.video_display import render_video_display


def main():
    """메인 애플리케이션 진입점."""
    # 페이지 설정
    st.set_page_config(
        page_title="Sora 2 영상 생성기",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 더 나은 스타일링을 위한 커스텀 CSS
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

    # 앱 제목
    st.title("Sora 2 영상 생성기")
    st.markdown("OpenAI Sora 2 API를 사용하여 영상을 생성하세요")

    # 사이드바 렌더링 및 설정 가져오기
    settings = render_sidebar()

    # 메인 콘텐츠 영역
    col1, col2 = st.columns([1, 1])

    with col1:
        # 영상 생성 폼
        form_data = render_video_form(settings)

    with col2:
        # 영상 결과 표시
        render_video_display(form_data, settings.get("api_key", ""))

    # 푸터
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9em;">
        Powered by OpenAI Sora 2 API |
        <a href="https://platform.openai.com/docs/guides/video-generation" target="_blank">문서</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
