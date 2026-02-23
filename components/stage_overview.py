"""Stage 2 - 하이레벨 개요 (모드별 분기)."""

from __future__ import annotations

import streamlit as st

from src.paper_state import get_paper_state, get_mode, set_stage, add_chat
from src.llm_client import call_llm, is_llm_configured
from src.prompts import SYSTEM_PROMPTS, OVERVIEW_PROMPTS


PAPER_TYPES = [
    "Narrative Review",
    "Systematic Review",
    "Scoping Review",
    "Meta-Analysis",
    "Critical Review",
    "State-of-the-Art Review",
]


def render() -> None:
    mode = get_mode()

    if mode == "quick":
        _render_quick()
    elif mode == "expert":
        _render_expert()
    else:
        _render_standard()


# ────────────────────────── Quick ──────────────────────────

def _render_quick() -> None:
    st.header("개요")
    st.info("**Quick Start** — 기본 정보를 확인하고 AI가 개요를 자동 생성합니다.")

    ps = get_paper_state()

    ps.paper_type = st.selectbox(
        "논문 유형",
        PAPER_TYPES,
        index=PAPER_TYPES.index(ps.paper_type) if ps.paper_type in PAPER_TYPES else 0,
    )

    if is_llm_configured() and not ps.overview.strip():
        if st.button("AI로 개요 자동 생성", type="secondary"):
            with st.spinner("개요 생성 중..."):
                prompt = OVERVIEW_PROMPTS["quick"].format(
                    topic=ps.topic,
                    keywords=ps.keywords,
                )
                result = call_llm(SYSTEM_PROMPTS["quick"], prompt)
                if result:
                    ps.overview = result
                    add_chat("assistant", f"[개요 생성]\n{result}")
                    st.rerun()

    ps.overview = st.text_area("개요", value=ps.overview, height=200, placeholder="AI가 생성하거나 직접 작성하세요...")

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 주제", use_container_width=True):
            set_stage("topic")
            st.rerun()
    with col3:
        if st.button("다음 →", type="primary", use_container_width=True, disabled=not ps.overview.strip()):
            set_stage("structure")
            st.rerun()


# ────────────────────────── Standard ──────────────────────────

def _render_standard() -> None:
    st.header("2. 하이레벨 개요")
    st.markdown("논문의 유형을 선택하고, 전체적인 방향과 개요를 작성합니다.")

    ps = get_paper_state()

    ps.paper_type = st.selectbox(
        "논문 유형",
        PAPER_TYPES,
        index=PAPER_TYPES.index(ps.paper_type) if ps.paper_type in PAPER_TYPES else 0,
    )

    if is_llm_configured():
        if st.button("AI로 개요 생성하기", type="secondary"):
            with st.spinner("AI가 개요를 생성하고 있습니다..."):
                prompt = OVERVIEW_PROMPTS["standard"].format(
                    topic=ps.topic,
                    research_question=ps.research_question,
                    scope=ps.scope,
                    keywords=ps.keywords,
                    paper_type=ps.paper_type,
                )
                result = call_llm(SYSTEM_PROMPTS["standard"], prompt)
                if result:
                    ps.overview = result
                    add_chat("assistant", f"[개요 생성]\n{result}")
                    st.rerun()

    ps.overview = st.text_area("논문 개요", value=ps.overview, height=300, placeholder="논문의 전체적인 방향, 배경, 목적, 기여점 등을 기술합니다...")
    ps.target_audience = st.text_input("대상 독자", value=ps.target_audience, placeholder="예: NLP 연구자, AI 엔지니어, 대학원생")
    ps.contribution = st.text_area("기대 기여점", value=ps.contribution, height=100, placeholder="이 리뷰 논문이 기존 연구와 차별화되는 점은?")

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 주제 설정", use_container_width=True):
            set_stage("topic")
            st.rerun()
    with col3:
        if st.button("다음: 구조 설계 →", type="primary", use_container_width=True, disabled=not ps.overview.strip()):
            set_stage("structure")
            st.rerun()

    if not ps.overview.strip():
        st.caption("개요를 작성하면 다음 단계로 진행할 수 있습니다.")


# ────────────────────────── Expert ──────────────────────────

def _render_expert() -> None:
    st.header("2. 하이레벨 개요 — Expert")
    st.markdown("논문의 학술적 프레임워크와 기여점을 심층 설계합니다.")

    ps = get_paper_state()

    ps.paper_type = st.selectbox(
        "논문 유형",
        PAPER_TYPES,
        index=PAPER_TYPES.index(ps.paper_type) if ps.paper_type in PAPER_TYPES else 0,
        help="Systematic Review: PRISMA 가이드라인 | Scoping Review: PRISMA-ScR | Meta-Analysis: 정량적 통합",
    )

    if is_llm_configured():
        if st.button("AI로 심층 개요 생성", type="secondary"):
            with st.spinner("AI가 심층 개요를 생성하고 있습니다..."):
                prompt = OVERVIEW_PROMPTS["expert"].format(
                    topic=ps.topic,
                    research_question=ps.research_question,
                    scope=ps.scope,
                    keywords=ps.keywords,
                    paper_type=ps.paper_type,
                    motivation=ps.motivation,
                    exclusion_criteria=ps.exclusion_criteria,
                    time_range=ps.time_range,
                    databases=ps.databases,
                )
                result = call_llm(SYSTEM_PROMPTS["expert"], prompt)
                if result:
                    ps.overview = result
                    add_chat("assistant", f"[심층 개요 생성]\n{result}")
                    st.rerun()

    ps.overview = st.text_area("논문 개요", value=ps.overview, height=350, placeholder="연구 배경, 간극, 기여점을 포함한 상세 개요...")

    st.subheader("학술적 프레임워크")
    ps.theoretical_framework = st.text_area(
        "이론적 프레임워크",
        value=ps.theoretical_framework,
        height=100,
        placeholder="분석에 사용할 이론적 틀이나 분류 기준 (예: Technology Acceptance Model, Bloom's Taxonomy 등)",
    )
    ps.gap_analysis = st.text_area(
        "연구 간극 분석 (Gap Analysis)",
        value=ps.gap_analysis,
        height=100,
        placeholder="기존 리뷰에서 다루지 못한 영역, 이 리뷰가 채울 간극",
    )
    ps.methodology_notes = st.text_area(
        "방법론 노트",
        value=ps.methodology_notes,
        height=100,
        placeholder="검색 전략, 선정/제외 기준, 품질 평가 방법, 데이터 추출 프로세스 등",
    )

    ps.target_audience = st.text_input("대상 독자", value=ps.target_audience, placeholder="예: NLP 연구자, AI 엔지니어, 대학원생")
    ps.contribution = st.text_area("기대 기여점", value=ps.contribution, height=100, placeholder="이 리뷰의 독창적 기여")

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 주제 설정", use_container_width=True):
            set_stage("topic")
            st.rerun()
    with col3:
        if st.button("다음: 구조 설계 →", type="primary", use_container_width=True, disabled=not ps.overview.strip()):
            set_stage("structure")
            st.rerun()

    if not ps.overview.strip():
        st.caption("개요를 작성하면 다음 단계로 진행할 수 있습니다.")
