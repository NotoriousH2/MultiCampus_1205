"""사이드바 컴포넌트 - API 키 입력 및 모델 선택."""

import streamlit as st

from services.sora_api import VideoModel, VideoSize, VideoDuration, validate_api_key
from utils.storage import APIKeyStorage


def render_sidebar() -> dict:
    """API 키 입력과 모델 설정이 포함된 사이드바를 렌더링합니다.

    Returns:
        선택된 설정이 담긴 딕셔너리.
    """
    with st.sidebar:
        st.header("설정")

        # API 키 섹션
        st.subheader("OpenAI API 키")

        # 저장된 API 키 불러오기
        saved_key = APIKeyStorage.get_api_key()
        if saved_key and "api_key_input" not in st.session_state:
            st.session_state.api_key_input = saved_key

        # API 키 입력
        api_key = st.text_input(
            "API 키",
            type="password",
            key="api_key_input",
            placeholder="sk-...",
            help="OpenAI API 키를 입력하세요. 안전하게 저장됩니다."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("저장", use_container_width=True):
                if api_key:
                    with st.spinner("검증 중..."):
                        if validate_api_key(api_key):
                            APIKeyStorage.set_api_key(api_key, save_locally=True)
                            st.success("저장 완료!")
                        else:
                            st.error("유효하지 않은 API 키")
                else:
                    st.warning("먼저 키를 입력하세요")

        with col2:
            if st.button("삭제", use_container_width=True):
                APIKeyStorage.clear_local()
                if "api_key" in st.session_state:
                    del st.session_state.api_key
                if "api_key_input" in st.session_state:
                    st.session_state.api_key_input = ""
                st.rerun()

        # API 키 상태 표시
        if APIKeyStorage.is_api_key_set():
            st.success("API 키가 설정되었습니다")
        else:
            st.warning("API 키가 설정되지 않았습니다")

        st.divider()

        # 모델 설정
        st.subheader("모델 설정")

        model = st.selectbox(
            "모델",
            options=[m.value for m in VideoModel],
            format_func=lambda x: {
                "sora-2": "Sora 2 (빠름)",
                "sora-2-pro": "Sora 2 Pro (고품질)"
            }.get(x, x),
            help="sora-2는 빠르고, sora-2-pro는 더 높은 품질의 결과물을 생성합니다"
        )

        # 영상 해상도
        size = st.selectbox(
            "해상도",
            options=[s.value for s in VideoSize],
            index=1,  # 기본값 720p
            format_func=lambda x: {
                "854x480": "480p (854x480)",
                "1280x720": "720p (1280x720)",
                "1920x1080": "1080p (1920x1080)"
            }.get(x, x),
            help="높은 해상도는 생성 시간이 더 오래 걸립니다"
        )

        # 영상 길이
        seconds = st.selectbox(
            "영상 길이",
            options=[d.value for d in VideoDuration],
            index=1,  # 기본값 8초
            format_func=lambda x: f"{x}초",
            help="영상 길이를 선택하세요 (4초, 8초, 12초)"
        )

        st.divider()

        # 정보 섹션
        st.subheader("안내")
        st.markdown("""
        **Sora 2** - 빠른 생성으로 신속한 반복 작업에 적합

        **Sora 2 Pro** - 프로덕션용 고품질 출력

        **팁:**
        - 촬영 유형, 피사체, 동작, 배경, 조명을 설명하세요
        - 구체적으로 작성하면 일관된 결과를 얻을 수 있습니다
        - 이미지는 선택한 해상도와 일치해야 합니다
        """)

        return {
            "api_key": api_key or saved_key,
            "model": model,
            "size": size,
            "seconds": seconds
        }
