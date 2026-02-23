"""LLM API 클라이언트 - OpenAI 및 Anthropic API 지원."""

from __future__ import annotations

import streamlit as st


def _call_openai(api_key: str, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content


def _call_anthropic(api_key: str, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=8192,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return resp.content[0].text


PROVIDERS = {
    "OpenAI": {
        "call": _call_openai,
        "models": ["gpt-5.2", "gpt-4o", "gpt-4o-mini", "o3", "o4-mini", "gpt-4.1", "gpt-4.1-mini"],
    },
    "Anthropic": {
        "call": _call_anthropic,
        "models": ["claude-sonnet-4-6", "claude-opus-4-6", "claude-haiku-4-5-20251001"],
    },
}


def call_llm(system_prompt: str, user_prompt: str) -> str | None:
    """session_state에 저장된 설정으로 LLM을 호출한다.

    API 키가 설정되지 않았으면 None을 반환한다.
    """
    cfg = st.session_state.get("llm_config", {})
    api_key = cfg.get("api_key", "").strip()
    if not api_key:
        return None

    provider = cfg.get("provider", "OpenAI")
    model = cfg.get("model", PROVIDERS[provider]["models"][0])
    temperature = cfg.get("temperature", 0.7)

    try:
        return PROVIDERS[provider]["call"](api_key, model, system_prompt, user_prompt, temperature)
    except Exception as e:
        st.error(f"LLM API 호출 실패: {e}")
        return None


def is_llm_configured() -> bool:
    """LLM API 키가 설정되어 있는지 확인한다."""
    cfg = st.session_state.get("llm_config", {})
    return bool(cfg.get("api_key", "").strip())
