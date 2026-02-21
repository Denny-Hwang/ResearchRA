"""Stage 3 - 상세 구조 설계."""

from __future__ import annotations

import streamlit as st

from src.paper_state import get_paper_state, set_stage, add_chat, Section
from src.llm_client import call_llm, is_llm_configured
from src.prompts import STRUCTURE_PROMPT


def _default_sections() -> list[Section]:
    """기본 리뷰 논문 구조를 반환한다."""
    return [
        Section(title="Abstract", description="논문의 요약"),
        Section(title="1. Introduction", description="연구 배경, 목적, 논문 구성 소개"),
        Section(title="2. Background", description="주요 개념 및 관련 연구 정리"),
        Section(title="3. Methodology", description="리뷰 방법론 (검색 전략, 선정 기준 등)"),
        Section(title="4. Main Review", description="주제별 핵심 리뷰 내용", subsections=[{"title": "4.1 Sub-topic A"}, {"title": "4.2 Sub-topic B"}]),
        Section(title="5. Discussion", description="주요 발견, 연구 간극, 향후 연구 방향"),
        Section(title="6. Conclusion", description="핵심 결론 요약"),
        Section(title="References", description="참고문헌 목록"),
    ]


def render() -> None:
    st.header("3. 상세 구조 설계")
    st.markdown("논문의 섹션 구조를 설계합니다. 섹션을 추가/수정/삭제할 수 있습니다.")

    ps = get_paper_state()

    # 구조가 없으면 기본 구조 또는 AI 생성
    col_ai, col_default = st.columns(2)
    with col_ai:
        if is_llm_configured():
            if st.button("AI로 구조 생성", type="secondary", use_container_width=True):
                with st.spinner("AI가 논문 구조를 설계하고 있습니다..."):
                    prompt = STRUCTURE_PROMPT.format(
                        topic=ps.topic,
                        research_question=ps.research_question,
                        overview=ps.overview,
                    )
                    result = call_llm(
                        "당신은 학술 리뷰 논문 구조를 설계하는 전문가입니다. 제안하는 구조를 명확하게 나열해 주세요.",
                        prompt,
                    )
                    if result:
                        st.session_state["ai_structure_suggestion"] = result
                        add_chat("assistant", f"[구조 제안]\n{result}")
    with col_default:
        if st.button("기본 구조 불러오기", use_container_width=True):
            ps.sections = _default_sections()
            st.rerun()

    # AI 제안 표시
    ai_suggestion = st.session_state.get("ai_structure_suggestion")
    if ai_suggestion:
        with st.expander("AI 구조 제안 (참고용)", expanded=True):
            st.markdown(ai_suggestion)
            if st.button("이 제안을 기반으로 구조 생성"):
                st.session_state.pop("ai_structure_suggestion", None)
                st.info("위 제안을 참고하여 아래에서 섹션을 직접 추가/수정해 주세요.")

    st.divider()

    # 섹션 편집
    st.subheader("논문 섹션 구조")

    if not ps.sections:
        st.info("'기본 구조 불러오기' 또는 직접 섹션을 추가하세요.")

    sections_to_remove = []
    for i, sec in enumerate(ps.sections):
        with st.expander(f"{sec.title or f'섹션 {i+1}'}", expanded=False):
            sec.title = st.text_input("섹션 제목", value=sec.title, key=f"sec_title_{i}")
            sec.description = st.text_area("설명", value=sec.description, key=f"sec_desc_{i}", height=80)

            # 하위 섹션
            st.markdown("**하위 섹션**")
            subs_to_remove = []
            for j, sub in enumerate(sec.subsections):
                c1, c2 = st.columns([5, 1])
                with c1:
                    new_title = st.text_input(
                        "하위 섹션 제목",
                        value=sub.get("title", ""),
                        key=f"sub_{i}_{j}",
                        label_visibility="collapsed",
                    )
                    sec.subsections[j]["title"] = new_title
                with c2:
                    if st.button("X", key=f"rm_sub_{i}_{j}"):
                        subs_to_remove.append(j)

            for idx in reversed(subs_to_remove):
                sec.subsections.pop(idx)
                st.rerun()

            if st.button("+ 하위 섹션 추가", key=f"add_sub_{i}"):
                sec.subsections.append({"title": ""})
                st.rerun()

            if st.button("이 섹션 삭제", key=f"rm_sec_{i}", type="secondary"):
                sections_to_remove.append(i)

    for idx in reversed(sections_to_remove):
        ps.sections.pop(idx)
        st.rerun()

    # 새 섹션 추가
    st.divider()
    if st.button("+ 새 섹션 추가"):
        ps.sections.append(Section())
        st.rerun()

    st.divider()

    # 네비게이션
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 개요", use_container_width=True):
            set_stage("overview")
            st.rerun()
    with col3:
        if st.button(
            "다음: 초안 작성 →",
            type="primary",
            use_container_width=True,
            disabled=len(ps.sections) == 0,
        ):
            set_stage("draft")
            st.rerun()
