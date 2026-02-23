"""Stage 5 - 최종 완성 (모드별 분기)."""

from __future__ import annotations

import streamlit as st

from src.paper_state import get_paper_state, get_mode, set_stage, add_chat
from src.llm_client import call_llm, is_llm_configured
from src.prompts import SYSTEM_PROMPTS, FINALIZE_PROMPTS, REFINE_PROMPT


def render() -> None:
    mode = get_mode()
    ps = get_paper_state()

    if mode == "quick":
        st.header("최종 완성")
        st.info("**Quick Start** — 초안을 하나의 논문으로 빠르게 통합합니다.")
    elif mode == "expert":
        st.header("5. 최종 완성 — Expert")
        st.markdown("최상위 저널 수준의 품질로 논문을 통합하고 정제합니다.")
    else:
        st.header("5. 최종 완성")
        st.markdown("섹션별 초안을 하나의 완성된 논문으로 통합합니다.")

    written_sections = {k: v for k, v in ps.draft_sections.items() if v.strip()}
    st.info(f"작성된 섹션: {len(written_sections)}개")

    # 통합 버튼
    if is_llm_configured():
        if st.button("AI로 전체 논문 통합하기", type="secondary"):
            with st.spinner("AI가 논문을 통합하고 있습니다..."):
                all_sections_text = ""
                for sec in ps.sections:
                    content = ps.draft_sections.get(sec.title, "")
                    if content.strip():
                        all_sections_text += f"\n\n## {sec.title}\n\n{content}"

                prompt_tpl = FINALIZE_PROMPTS[mode]
                fmt_kwargs = dict(topic=ps.topic, all_sections=all_sections_text)
                if mode != "quick":
                    fmt_kwargs["research_question"] = ps.research_question

                prompt = prompt_tpl.format(**fmt_kwargs)
                result = call_llm(SYSTEM_PROMPTS[mode], prompt)
                if result:
                    ps.final_paper = result
                    add_chat("assistant", "[최종 논문 통합 완료]")
                    st.rerun()
    else:
        if st.button("초안들을 단순 결합하기"):
            parts = [f"# {ps.topic}\n"]
            for sec in ps.sections:
                content = ps.draft_sections.get(sec.title, "")
                if content.strip():
                    parts.append(f"\n## {sec.title}\n\n{content}")
            ps.final_paper = "\n".join(parts)
            st.rerun()

    st.divider()

    if ps.final_paper:
        st.subheader("최종 논문")

        view_mode = st.radio("보기 모드", ["미리보기", "편집"], horizontal=True, key="final_view_mode")

        if view_mode == "미리보기":
            st.markdown(ps.final_paper)
        else:
            ps.final_paper = st.text_area("최종 논문 편집", value=ps.final_paper, height=600, key="final_editor")

        # AI 개선
        if is_llm_configured():
            st.divider()
            feedback = st.text_input("전체 논문에 대한 피드백", placeholder="예: 서론을 더 구체적으로, 결론에 향후 연구 방향 추가")
            if st.button("AI로 피드백 반영"):
                if feedback.strip():
                    with st.spinner("개선 중..."):
                        prompt = REFINE_PROMPT.format(current_content=ps.final_paper, feedback=feedback)
                        result = call_llm(SYSTEM_PROMPTS[mode], prompt)
                        if result:
                            ps.final_paper = result
                            add_chat("assistant", f"[최종 논문 개선] 피드백: {feedback}")
                            st.rerun()

        st.divider()
        st.success("논문이 완성되었습니다! 사이드바에서 Markdown 또는 Word 파일로 내보낼 수 있습니다.")
    else:
        st.info("위 버튼을 눌러 초안들을 하나의 논문으로 통합하세요.")

    st.divider()
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← 초안 작성", use_container_width=True):
            set_stage("draft")
            st.rerun()
