"""Stage 1 - 주제 설정."""

from __future__ import annotations

import streamlit as st

from src.paper_state import get_paper_state, set_stage, add_chat
from src.llm_client import call_llm, is_llm_configured


def render() -> None:
    st.header("1. 주제 설정")
    st.markdown("리뷰 논문의 주제와 범위를 정의합니다.")

    ps = get_paper_state()

    ps.topic = st.text_input("논문 주제", value=ps.topic, placeholder="예: 대규모 언어 모델의 환각(hallucination) 현상")
    ps.research_question = st.text_area(
        "연구 질문 (Research Question)",
        value=ps.research_question,
        placeholder="예: LLM의 환각 현상은 어떤 유형이 있으며, 이를 완화하기 위한 기법은 무엇인가?",
        height=100,
    )
    ps.scope = st.text_area(
        "리뷰 범위",
        value=ps.scope,
        placeholder="예: 2020년 이후 발표된 주요 연구, Transformer 기반 모델 중심",
        height=80,
    )
    ps.keywords = st.text_input("키워드 (쉼표로 구분)", value=ps.keywords, placeholder="hallucination, LLM, factuality")

    # AI 추천
    if is_llm_configured() and ps.topic.strip():
        if st.button("AI로 연구 질문 제안받기", type="secondary"):
            with st.spinner("AI가 연구 질문을 생성하고 있습니다..."):
                suggestion = call_llm(
                    "당신은 학술 연구 주제 설정을 돕는 전문가입니다.",
                    f"다음 주제에 대한 리뷰 논문의 연구 질문, 범위, 키워드를 각각 3개씩 제안해 주세요.\n\n주제: {ps.topic}",
                )
                if suggestion:
                    st.info(suggestion)
                    add_chat("assistant", suggestion)

    st.divider()

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("다음: 개요 작성 →", type="primary", use_container_width=True, disabled=not ps.topic.strip()):
            set_stage("overview")
            st.rerun()

    if not ps.topic.strip():
        st.caption("주제를 입력하면 다음 단계로 진행할 수 있습니다.")
