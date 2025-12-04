"""영상 생성 폼 컴포넌트."""

from typing import Optional

import streamlit as st


def render_video_form(settings: dict) -> Optional[dict]:
    """영상 생성 폼을 렌더링합니다.

    Args:
        settings: 사이드바에서 가져온 모델 설정 딕셔너리.

    Returns:
        제출된 경우 폼 데이터 딕셔너리, 아니면 None.
    """
    st.header("영상 생성")

    # 생성 모드 탭
    tab_prompt, tab_image = st.tabs(["텍스트로 영상 만들기", "이미지로 영상 만들기"])

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
    """텍스트-투-비디오 폼을 렌더링합니다.

    Args:
        settings: 모델 설정 딕셔너리.

    Returns:
        제출된 경우 폼 데이터, 아니면 None.
    """
    with st.form("prompt_form"):
        st.markdown("### 텍스트로 영상 만들기")
        st.markdown("생성하고 싶은 영상을 설명하세요.")

        prompt = st.text_area(
            "프롬프트",
            height=150,
            placeholder="예시: 넓은 잔디 공원에서 빨간 연을 날리는 아이의 와이드 샷, 골든아워 햇빛, 카메라가 천천히 위로 패닝.",
            help="최상의 결과를 위해 촬영 유형, 피사체, 동작, 배경, 조명을 설명하세요."
        )

        # 예시 프롬프트
        with st.expander("프롬프트 예시"):
            st.markdown("""
            - **자연:** "일출 시 안개 낀 산맥 위를 날아가는 에어리얼 드론 샷, 구름 사이로 스며드는 황금빛"
            - **도시:** "밤의 분주한 도시 교차로 타임랩스, 젖은 도로에 반사되는 네온 불빛"
            - **추상:** "물에 떨어지는 다채로운 잉크 방울 슬로우 모션, 소용돌이치며 섞이는 모습"
            - **제품:** "나무 테이블 위 김이 나는 커피 컵 클로즈업, 블라인드 사이로 들어오는 아침 빛, 부드러운 피사계 심도"
            """)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"모델: {settings['model']} | 해상도: {settings['size']} | 길이: {settings['seconds']}초")
        with col2:
            submitted = st.form_submit_button("생성하기", type="primary", use_container_width=True)

        if submitted:
            if not prompt:
                st.error("프롬프트를 입력해주세요.")
                return None
            if not settings.get("api_key"):
                st.error("사이드바에서 API 키를 설정해주세요.")
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
    """이미지-투-비디오 폼을 렌더링합니다.

    Args:
        settings: 모델 설정 딕셔너리.

    Returns:
        제출된 경우 폼 데이터, 아니면 None.
    """
    with st.form("image_form"):
        st.markdown("### 이미지로 영상 만들기")
        st.markdown("영상의 첫 프레임으로 사용할 이미지를 업로드하세요.")

        # 이미지 업로드
        uploaded_file = st.file_uploader(
            "이미지 업로드",
            type=["jpg", "jpeg", "png", "webp"],
            help="이미지가 첫 프레임으로 사용됩니다. 선택한 해상도와 일치해야 합니다."
        )

        if uploaded_file:
            st.image(uploaded_file, caption="미리보기", use_container_width=True)

        prompt = st.text_area(
            "프롬프트",
            height=100,
            placeholder="예시: 피사체가 천천히 뒤를 돌아 미소 짓고, 프레임 밖으로 걸어 나갑니다.",
            help="이미지에서 시작해서 영상에서 어떤 일이 일어나야 하는지 설명하세요."
        )

        # 주의사항
        st.info("""
        **주의사항:**
        - 이미지 해상도는 선택한 영상 크기와 일치해야 합니다
        - 사람 얼굴이 포함된 이미지는 거부될 수 있습니다
        - 지원 형식: JPEG, PNG, WebP
        """)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"모델: {settings['model']} | 해상도: {settings['size']} | 길이: {settings['seconds']}초")
        with col2:
            submitted = st.form_submit_button("생성하기", type="primary", use_container_width=True)

        if submitted:
            if not prompt:
                st.error("프롬프트를 입력해주세요.")
                return None
            if not uploaded_file:
                st.error("이미지를 업로드해주세요.")
                return None
            if not settings.get("api_key"):
                st.error("사이드바에서 API 키를 설정해주세요.")
                return None

            # 이미지 바이트 읽기
            image_bytes = uploaded_file.read()

            # MIME 타입 결정
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
