"""Stage 1 - 주제 설정 (모드별 분기)."""

from __future__ import annotations

import streamlit as st

from src.paper_state import get_paper_state, get_mode, set_stage, add_chat
from src.llm_client import call_llm, is_llm_configured
from src.prompts import SYSTEM_PROMPTS, QUICK_AUTOFILL_TOPIC, EXPERT_WORKSHOP_TOPIC


def render() -> None:
    mode = get_mode()

    if mode == "quick":
        _render_quick()
    elif mode == "expert":
        _render_expert()
    else:
        _render_standard()


# ────────────────────────── Quick Start ──────────────────────────

def _render_quick() -> None:
    st.header("주제 설정")
    st.info("**Quick Start** — 주제만 입력하면 나머지는 AI가 채워줍니다.")

    ps = get_paper_state()
    ps.topic = st.text_input(
        "리뷰할 주제를 입력하세요",
        value=ps.topic,
        placeholder="예: 대규모 언어 모델의 환각(hallucination) 현상",
    )

    if is_llm_configured() and ps.topic.strip():
        if st.button("AI로 자동 완성", type="secondary"):
            with st.spinner("AI가 연구 질문, 범위, 키워드를 생성 중..."):
                result = call_llm(
                    SYSTEM_PROMPTS["quick"],
                    QUICK_AUTOFILL_TOPIC.format(topic=ps.topic),
                )
                if result:
                    st.info(result)
                    add_chat("assistant", result)
                    # 사용자가 확인할 수 있도록 표시
                    _try_parse_autofill(ps, result)

    # 자동완성 결과 확인/수정
    if ps.research_question or ps.scope or ps.keywords:
        with st.expander("자동 생성된 내용 확인/수정", expanded=True):
            ps.research_question = st.text_input("연구 질문", value=ps.research_question, key="q_rq")
            ps.scope = st.text_input("범위", value=ps.scope, key="q_scope")
            ps.keywords = st.text_input("키워드", value=ps.keywords, key="q_kw")

    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("다음 →", type="primary", use_container_width=True, disabled=not ps.topic.strip()):
            set_stage("overview")
            st.rerun()


# ────────────────────────── Standard ──────────────────────────

def _render_standard() -> None:
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

    if is_llm_configured() and ps.topic.strip():
        if st.button("AI로 연구 질문 제안받기", type="secondary"):
            with st.spinner("AI가 연구 질문을 생성하고 있습니다..."):
                suggestion = call_llm(
                    SYSTEM_PROMPTS["standard"],
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


# ────────────────────────── Expert ──────────────────────────

def _render_expert() -> None:
    st.header("1. 주제 설정 — Expert Workshop")
    st.markdown(
        "각 항목을 꼼꼼히 정의합니다. "
        "잘 정의된 주제와 범위가 고품질 리뷰 논문의 기반이 됩니다."
    )

    ps = get_paper_state()

    st.subheader("핵심 정보")
    ps.topic = st.text_input("논문 주제", value=ps.topic, placeholder="예: 대규모 언어 모델의 환각(hallucination) 현상")
    ps.research_question = st.text_area(
        "연구 질문 (Research Questions)",
        value=ps.research_question,
        placeholder="RQ1: ...\nRQ2: ...\nRQ3: ...",
        height=120,
        help="체계적 리뷰에서는 PICO(Population, Intervention, Comparison, Outcome) 형식이 권장됩니다.",
    )

    st.subheader("범위 및 검색 전략")
    col1, col2 = st.columns(2)
    with col1:
        ps.scope = st.text_area(
            "리뷰 범위 (Scope)",
            value=ps.scope,
            placeholder="포함할 연구 유형, 대상 기술 등",
            height=100,
        )
        ps.time_range = st.text_input(
            "검색 기간",
            value=ps.time_range,
            placeholder="예: 2018-2024",
        )
    with col2:
        ps.exclusion_criteria = st.text_area(
            "제외 기준 (Exclusion Criteria)",
            value=ps.exclusion_criteria,
            placeholder="예: 비영어 논문 제외, 2페이지 미만 workshop paper 제외",
            height=100,
        )
        ps.databases = st.text_input(
            "검색 데이터베이스",
            value=ps.databases,
            placeholder="예: Google Scholar, IEEE Xplore, ACM DL, ArXiv",
        )

    ps.keywords = st.text_input("키워드 (쉼표로 구분)", value=ps.keywords, placeholder="hallucination, LLM, factuality, grounding")

    st.subheader("연구 동기")
    ps.motivation = st.text_area(
        "이 리뷰를 수행하는 동기",
        value=ps.motivation,
        placeholder="왜 이 시점에 이 리뷰가 필요한가? 기존 리뷰의 한계는?",
        height=100,
    )

    # AI 워크숍 가이드
    if is_llm_configured() and ps.topic.strip():
        st.divider()
        if st.button("AI 워크숍 가이드 받기", type="secondary"):
            with st.spinner("AI가 심층 질문을 준비하고 있습니다..."):
                result = call_llm(
                    SYSTEM_PROMPTS["expert"],
                    EXPERT_WORKSHOP_TOPIC.format(
                        topic=ps.topic,
                        research_question=ps.research_question,
                        scope=ps.scope,
                        keywords=ps.keywords,
                    ),
                )
                if result:
                    st.session_state["expert_workshop_guide"] = result
                    add_chat("assistant", result)

        guide = st.session_state.get("expert_workshop_guide")
        if guide:
            with st.expander("AI 워크숍 가이드", expanded=True):
                st.markdown(guide)

    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("다음: 개요 작성 →", type="primary", use_container_width=True, disabled=not ps.topic.strip()):
            set_stage("overview")
            st.rerun()

    if not ps.topic.strip():
        st.caption("주제를 입력하면 다음 단계로 진행할 수 있습니다.")


# ── 유틸 ──

def _try_parse_autofill(ps, text: str) -> None:
    """AI 응답에서 JSON 파싱을 시도한다."""
    import json
    try:
        # JSON 블록 추출 시도
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            ps.research_question = data.get("research_question", ps.research_question)
            ps.scope = data.get("scope", ps.scope)
            ps.keywords = data.get("keywords", ps.keywords)
    except (json.JSONDecodeError, ValueError):
        pass
