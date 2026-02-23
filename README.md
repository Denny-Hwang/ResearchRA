# Review Paper Agent

Streamlit 기반 리뷰 논문 작성 도우미 앱입니다.
특정 주제에 대해 **하이레벨 개요 → 상세 구조 → 초안 → 최종 완성**까지 단계별로 진행하며, 각 단계에서 사용자 검토를 거칩니다.

## 주요 기능

- **5단계 워크플로우**: 주제 설정 → 개요 → 구조 설계 → 초안 작성 → 최종 완성
- **3가지 작성 모드**: 사용자 수준에 맞게 질문 깊이와 자동화 수준 조절
- **LLM API 연동 (선택)**: OpenAI / Anthropic API를 입력하면 AI 보조 활성화
- **수동 모드 지원**: API 없이도 모든 내용을 직접 작성 가능
- **대화형 도우미**: 논문 작성 중 질문할 수 있는 채팅 기능
- **내보내기**: Markdown (.md), Word (.docx) 다운로드

## 작성 모드

| 모드 | 설명 | 대상 |
|---|---|---|
| **Quick Start** | 주제만 입력하면 AI가 나머지를 자동 완성. MVP 프로토타이핑 방식 | 빠르게 초안이 필요한 경우 |
| **Standard** | 주요 의사결정은 사용자가, 세부 작성은 AI가 보조 | 일반적인 리뷰 논문 작성 |
| **Expert** | 매 단계마다 심층 워크숍 질문으로 고품질 학술 논문 설계 | 학술지 투고 수준의 논문 |

## 프로젝트 구조

```
ResearchRA/
├── app.py                         # Streamlit 메인 앱
├── requirements.txt               # Python 의존성
├── .streamlit/config.toml         # Streamlit 테마 설정
├── src/
│   ├── llm_client.py              # OpenAI / Anthropic API 클라이언트
│   ├── paper_state.py             # 논문 상태 및 모드 관리
│   └── prompts.py                 # 모드별 LLM 프롬프트 템플릿
└── components/
    ├── sidebar.py                 # 사이드바 (모드 선택, 진행 단계, LLM 설정)
    ├── export.py                  # Markdown / Word 내보내기
    ├── stage_topic.py             # 1단계: 주제 설정
    ├── stage_overview.py          # 2단계: 하이레벨 개요
    ├── stage_structure.py         # 3단계: 상세 구조 설계
    ├── stage_draft.py             # 4단계: 초안 작성
    └── stage_finalize.py          # 5단계: 최종 완성
```

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## LLM API 설정

앱 실행 후 왼쪽 사이드바의 **LLM API 설정**에서:

1. AI 제공자 선택 (OpenAI 또는 Anthropic)
2. 모델 선택
3. API Key 입력
4. Temperature 조절
5. **설정 저장** 클릭

API Key가 없어도 모든 내용을 수동으로 작성할 수 있습니다.
