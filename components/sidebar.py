"""사이드바 UI - 모드 선택, LLM 설정, 진행 상태, 내보내기."""

from __future__ import annotations

import streamlit as st

from src.llm_client import PROVIDERS, is_llm_configured
from src.paper_state import (
    STAGES,
    STAGE_LABELS,
    MODE_INFO,
    get_paper_state,
    set_stage,
)
from components.export import render_export_buttons


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Review Paper Agent")
        st.caption("리뷰 논문 작성 도우미")

        # ── 작성 모드 ──
        st.divider()
        _render_mode_selector()

        # ── 진행 단계 ──
        st.divider()
        st.subheader("진행 단계")
        ps = get_paper_state()
        current_idx = STAGES.index(ps.current_stage)

        for i, stage in enumerate(STAGES):
            if i < current_idx:
                icon = ":white_check_mark:"
            elif i == current_idx:
                icon = ":arrow_forward:"
            else:
                icon = ":white_circle:"
            label = STAGE_LABELS[stage]

            if i <= current_idx:
                if st.button(f"{icon} {label}", key=f"nav_{stage}", use_container_width=True):
                    set_stage(stage)
                    st.rerun()
            else:
                st.markdown(f"{icon} {label}")

        # ── LLM 설정 ──
        st.divider()
        with st.expander("LLM API 설정", expanded=not is_llm_configured()):
            _render_llm_config()

        # ── 내보내기 ──
        st.divider()
        render_export_buttons()

        # ── 초기화 ──
        st.divider()
        if st.button("새 논문 시작", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def _render_mode_selector() -> None:
    ps = get_paper_state()

    st.subheader("작성 모드")

    modes = list(MODE_INFO.keys())
    labels = [f"{MODE_INFO[m]['icon']} {MODE_INFO[m]['label']}" for m in modes]
    current_idx = modes.index(ps.mode)

    selected = st.radio(
        "작성 모드 선택",
        modes,
        index=current_idx,
        format_func=lambda m: f"{MODE_INFO[m]['icon']} {MODE_INFO[m]['label']}",
        key="mode_selector",
        label_visibility="collapsed",
    )

    if selected != ps.mode:
        ps.mode = selected
        st.rerun()

    st.caption(MODE_INFO[ps.mode]["description"])


def _render_llm_config() -> None:
    cfg = st.session_state.get("llm_config", {})

    provider = st.selectbox(
        "AI 제공자",
        list(PROVIDERS.keys()),
        index=list(PROVIDERS.keys()).index(cfg.get("provider", "OpenAI")),
        key="llm_provider_select",
    )
    model = st.selectbox(
        "모델",
        PROVIDERS[provider]["models"],
        key="llm_model_select",
    )
    api_key = st.text_input(
        "API Key",
        value=cfg.get("api_key", ""),
        type="password",
        key="llm_api_key_input",
    )
    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        cfg.get("temperature", 0.7),
        0.1,
        key="llm_temp_slider",
    )

    if st.button("설정 저장", use_container_width=True):
        st.session_state.llm_config = {
            "provider": provider,
            "model": model,
            "api_key": api_key,
            "temperature": temperature,
        }
        if api_key.strip():
            st.success("LLM 설정이 저장되었습니다.")
        else:
            st.info("API Key 없이도 수동 모드로 사용할 수 있습니다.")
