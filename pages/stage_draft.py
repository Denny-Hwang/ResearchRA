"""Stage 4 - 초안 작성."""

from __future__ import annotations

import streamlit as st

from src.paper_state import get_paper_state, set_stage, add_chat
from src.llm_client import call_llm, is_llm_configured
from src.prompts import DRAFT_SECTION_PROMPT, REFINE_PROMPT


def _structure_summary(ps) -> str:
    """전체 구조를 텍스트 요약으로 변환."""
    lines = []
    for sec in ps.sections:
        lines.append(f"- {sec.title}: {sec.description}")
        for sub in sec.subsections:
            lines.append(f"  - {sub.get('title', '')}")
    return "\n".join(lines)


def render() -> None:
    st.header("4. 초안 작성")
    st.markdown("각 섹션별로 초안을 작성합니다. AI 도움을 받거나 직접 작성할 수 있습니다.")

    ps = get_paper_state()

    if not ps.sections:
        st.warning("먼저 구조 설계 단계에서 섹션을 추가해 주세요.")
        if st.button("← 구조 설계로 돌아가기"):
            set_stage("structure")
            st.rerun()
        return

    # 진행률 표시
    total = len(ps.sections)
    written = sum(1 for sec in ps.sections if ps.draft_sections.get(sec.title, "").strip())
    st.progress(written / total if total > 0 else 0, text=f"작성 완료: {written}/{total} 섹션")

    # AI 전체 생성 버튼
    if is_llm_configured():
        if st.button("AI로 미작성 섹션 모두 생성", type="secondary"):
            structure_sum = _structure_summary(ps)
            progress_bar = st.progress(0)
            for idx, sec in enumerate(ps.sections):
                if ps.draft_sections.get(sec.title, "").strip():
                    progress_bar.progress((idx + 1) / total)
                    continue
                with st.spinner(f"'{sec.title}' 작성 중..."):
                    subs_text = ""
                    if sec.subsections:
                        subs_text = "**하위 섹션**:\n" + "\n".join(
                            f"- {s.get('title', '')}" for s in sec.subsections
                        )
                    prompt = DRAFT_SECTION_PROMPT.format(
                        topic=ps.topic,
                        overview=ps.overview,
                        structure_summary=structure_sum,
                        section_title=sec.title,
                        section_description=sec.description,
                        subsections_text=subs_text,
                    )
                    result = call_llm(
                        "당신은 학술 리뷰 논문을 작성하는 전문 연구원입니다.",
                        prompt,
                    )
                    if result:
                        ps.draft_sections[sec.title] = result
                        add_chat("assistant", f"[초안 생성: {sec.title}]")
                progress_bar.progress((idx + 1) / total)
            st.rerun()

    st.divider()

    # 섹션별 탭
    tab_labels = [sec.title for sec in ps.sections]
    if tab_labels:
        tabs = st.tabs(tab_labels)
        for i, (tab, sec) in enumerate(zip(tabs, ps.sections)):
            with tab:
                _render_section_editor(ps, sec, i)

    st.divider()

    # 네비게이션
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 구조 설계", use_container_width=True):
            set_stage("structure")
            st.rerun()
    with col3:
        if st.button(
            "다음: 최종 완성 →",
            type="primary",
            use_container_width=True,
            disabled=written == 0,
        ):
            set_stage("finalize")
            st.rerun()

    if written == 0:
        st.caption("하나 이상의 섹션 초안을 작성하면 다음 단계로 진행할 수 있습니다.")


def _render_section_editor(ps, sec, idx: int) -> None:
    """개별 섹션 초안 편집기."""
    current = ps.draft_sections.get(sec.title, "")

    # AI 개별 생성
    col_gen, col_refine = st.columns(2)
    with col_gen:
        if is_llm_configured():
            if st.button(f"AI로 작성", key=f"gen_{idx}"):
                with st.spinner("생성 중..."):
                    subs_text = ""
                    if sec.subsections:
                        subs_text = "**하위 섹션**:\n" + "\n".join(
                            f"- {s.get('title', '')}" for s in sec.subsections
                        )
                    prompt = DRAFT_SECTION_PROMPT.format(
                        topic=ps.topic,
                        overview=ps.overview,
                        structure_summary=_structure_summary(ps),
                        section_title=sec.title,
                        section_description=sec.description,
                        subsections_text=subs_text,
                    )
                    result = call_llm(
                        "당신은 학술 리뷰 논문을 작성하는 전문 연구원입니다.",
                        prompt,
                    )
                    if result:
                        ps.draft_sections[sec.title] = result
                        add_chat("assistant", f"[초안 생성: {sec.title}]")
                        st.rerun()

    with col_refine:
        if is_llm_configured() and current.strip():
            feedback = st.text_input("피드백 입력", key=f"feedback_{idx}", placeholder="수정 요청사항 입력")
            if st.button("AI로 개선", key=f"refine_{idx}"):
                if feedback.strip():
                    with st.spinner("개선 중..."):
                        prompt = REFINE_PROMPT.format(
                            current_content=current,
                            feedback=feedback,
                        )
                        result = call_llm(
                            "당신은 학술 논문 편집 전문가입니다.",
                            prompt,
                        )
                        if result:
                            ps.draft_sections[sec.title] = result
                            add_chat("assistant", f"[개선: {sec.title}] 피드백: {feedback}")
                            st.rerun()

    # 텍스트 에디터
    new_content = st.text_area(
        f"{sec.title} 내용",
        value=ps.draft_sections.get(sec.title, ""),
        height=400,
        key=f"draft_{idx}",
    )
    ps.draft_sections[sec.title] = new_content
