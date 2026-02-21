"""리뷰 논문 작성 도우미 - Streamlit 앱."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Review Paper Agent",
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.paper_state import get_paper_state
from pages.sidebar import render_sidebar
from pages import stage_topic, stage_overview, stage_structure, stage_draft, stage_finalize

# 사이드바
render_sidebar()

# 메인 영역 - 현재 단계에 맞는 페이지 렌더링
ps = get_paper_state()

STAGE_RENDERERS = {
    "topic": stage_topic.render,
    "overview": stage_overview.render,
    "structure": stage_structure.render,
    "draft": stage_draft.render,
    "finalize": stage_finalize.render,
}

renderer = STAGE_RENDERERS.get(ps.current_stage, stage_topic.render)
renderer()

# 하단 대화형 도우미
st.divider()
with st.expander("대화형 도우미", expanded=False):
    st.markdown("논문 작성 과정에서 궁금한 점을 질문하세요.")

    from src.llm_client import call_llm, is_llm_configured
    from src.prompts import CHAT_PROMPT, SYSTEM_PROMPT
    from src.paper_state import add_chat, STAGE_LABELS

    # 채팅 이력 표시
    for msg in ps.chat_history[-10:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("질문을 입력하세요...")
    if user_input:
        add_chat("user", user_input)
        with st.chat_message("user"):
            st.markdown(user_input)

        if is_llm_configured():
            with st.spinner("답변 생성 중..."):
                context = f"주제: {ps.topic}\n개요: {ps.overview[:200]}..." if ps.overview else f"주제: {ps.topic}"
                prompt = CHAT_PROMPT.format(
                    topic=ps.topic or "(미설정)",
                    stage=STAGE_LABELS.get(ps.current_stage, ps.current_stage),
                    context=context,
                    question=user_input,
                )
                answer = call_llm(SYSTEM_PROMPT, prompt)
                if answer:
                    add_chat("assistant", answer)
                    with st.chat_message("assistant"):
                        st.markdown(answer)
        else:
            msg = "LLM API가 설정되지 않았습니다. 사이드바에서 API Key를 입력해 주세요."
            add_chat("assistant", msg)
            with st.chat_message("assistant"):
                st.info(msg)
