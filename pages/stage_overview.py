"""Stage 2 - 하이레벨 개요."""

from __future__ import annotations

import streamlit as st

from src.paper_state import get_paper_state, set_stage, add_chat
from src.llm_client import call_llm, is_llm_configured
from src.prompts import OVERVIEW_PROMPT


PAPER_TYPES = [
    "Narrative Review",
    "Systematic Review",
    "Scoping Review",
    "Meta-Analysis",
    "Critical Review",
    "State-of-the-Art Review",
]


def render() -> None:
    st.header("2. 하이레벨 개요")
    st.markdown("논문의 유형을 선택하고, 전체적인 방향과 개요를 작성합니다.")

    ps = get_paper_state()

    ps.paper_type = st.selectbox(
        "논문 유형",
        PAPER_TYPES,
        index=PAPER_TYPES.index(ps.paper_type) if ps.paper_type in PAPER_TYPES else 0,
    )

    # AI 개요 생성
    if is_llm_configured():
        if st.button("AI로 개요 생성하기", type="secondary"):
            with st.spinner("AI가 개요를 생성하고 있습니다..."):
                prompt = OVERVIEW_PROMPT.format(
                    topic=ps.topic,
                    research_question=ps.research_question,
                    scope=ps.scope,
                    keywords=ps.keywords,
                    paper_type=ps.paper_type,
                )
                result = call_llm(
                    "당신은 학술 리뷰 논문 작성을 돕는 전문 연구 보조원입니다.",
                    prompt,
                )
                if result:
                    ps.overview = result
                    add_chat("assistant", f"[개요 생성]\n{result}")
                    st.rerun()

    ps.overview = st.text_area(
        "논문 개요",
        value=ps.overview,
        height=300,
        placeholder="논문의 전체적인 방향, 배경, 목적, 기여점 등을 기술합니다...",
    )

    ps.target_audience = st.text_input(
        "대상 독자",
        value=ps.target_audience,
        placeholder="예: NLP 연구자, AI 엔지니어, 대학원생",
    )

    ps.contribution = st.text_area(
        "기대 기여점",
        value=ps.contribution,
        height=100,
        placeholder="이 리뷰 논문이 기존 연구와 차별화되는 점은?",
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 주제 설정", use_container_width=True):
            set_stage("topic")
            st.rerun()
    with col3:
        if st.button(
            "다음: 구조 설계 →",
            type="primary",
            use_container_width=True,
            disabled=not ps.overview.strip(),
        ):
            set_stage("structure")
            st.rerun()

    if not ps.overview.strip():
        st.caption("개요를 작성하면 다음 단계로 진행할 수 있습니다.")
