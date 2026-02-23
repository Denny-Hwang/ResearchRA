"""리뷰 논문 작성 상태 관리."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Literal

import streamlit as st

Stage = Literal["topic", "overview", "structure", "draft", "finalize"]
Mode = Literal["quick", "standard", "expert"]

STAGES: list[Stage] = ["topic", "overview", "structure", "draft", "finalize"]

STAGE_LABELS: dict[Stage, str] = {
    "topic": "1. 주제 설정",
    "overview": "2. 하이레벨 개요",
    "structure": "3. 상세 구조 설계",
    "draft": "4. 초안 작성",
    "finalize": "5. 최종 완성",
}

MODE_INFO: dict[Mode, dict] = {
    "quick": {
        "label": "Quick Start",
        "icon": "🚀",
        "description": "핵심만 빠르게 — 주제와 기본 방향만 정하면 AI가 나머지를 채워줍니다.",
    },
    "standard": {
        "label": "Standard",
        "icon": "📝",
        "description": "균형 잡힌 진행 — 주요 의사결정은 사용자가, 세부 작성은 AI가 도와줍니다.",
    },
    "expert": {
        "label": "Expert",
        "icon": "🔬",
        "description": "심층 워크숍 — 각 단계마다 상세 질문으로 고품질 학술 논문을 설계합니다.",
    },
}


@dataclass
class Section:
    title: str = ""
    description: str = ""
    content: str = ""
    subsections: list[dict] = field(default_factory=list)


@dataclass
class PaperState:
    # 모드
    mode: Mode = "standard"

    # Stage 1 - 주제
    topic: str = ""
    research_question: str = ""
    scope: str = ""
    keywords: str = ""

    # Stage 1 - Expert 추가 필드
    motivation: str = ""
    exclusion_criteria: str = ""
    time_range: str = ""
    databases: str = ""

    # Stage 2 - 개요
    paper_type: str = "Narrative Review"
    overview: str = ""
    target_audience: str = ""
    contribution: str = ""

    # Stage 2 - Expert 추가 필드
    theoretical_framework: str = ""
    gap_analysis: str = ""
    methodology_notes: str = ""

    # Stage 3 - 구조
    sections: list[Section] = field(default_factory=list)

    # Stage 4 - 초안
    draft_sections: dict[str, str] = field(default_factory=dict)

    # Stage 5 - 최종
    final_paper: str = ""

    # 메타
    current_stage: Stage = "topic"
    chat_history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> PaperState:
        sections = [Section(**s) for s in d.pop("sections", [])]
        return cls(sections=sections, **d)


def get_paper_state() -> PaperState:
    """session_state에서 PaperState를 가져오거나 새로 생성한다."""
    if "paper_state" not in st.session_state:
        st.session_state.paper_state = PaperState()
    return st.session_state.paper_state


def get_mode() -> Mode:
    return get_paper_state().mode


def set_stage(stage: Stage) -> None:
    get_paper_state().current_stage = stage


def add_chat(role: str, content: str) -> None:
    get_paper_state().chat_history.append({"role": role, "content": content})


def export_state_json() -> str:
    return json.dumps(get_paper_state().to_dict(), ensure_ascii=False, indent=2)
