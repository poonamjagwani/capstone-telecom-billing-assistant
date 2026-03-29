# Phase 2 Execution Checklist

This checklist translates `Telecom_Billing_Assistant_app_plan_FastAPI.md` into implementation tasks.

## 1) Foundation
- [x] Create app structure: `core/`, `deploy/`, `app.py`, `config.py`, `.env.example`
- [x] Expand `requirements.txt` for FastAPI, Streamlit, plotting, retrieval stack
- [x] Add environment defaults and path validation in `config.py`

## 2) Core modules
- [x] `core/llm_provider.py` for Ollama + optional OpenAI-compatible setup *(starter health hint + config wiring)*
- [x] `core/rag_engine.py` for index build/load/query over PDFs *(starter local summary index; FAISS wiring pending)*
- [x] `core/tool_agent.py` for DuckDuckGo-backed web lookup
- [x] `core/research_agent.py` for dispute-style report generation
- [x] `core/chart_generator.py` for billing JSON -> Plotly figures
- [x] `core/router.py` for intent routing (`rag`, `chart`, `research`, `web`)
- [x] `core/models.py` Pydantic request/response models

## 3) API layer
- [x] Implement `deploy/server.py` FastAPI app
- [x] Route coverage: `/health`, `/v1/intent`, `/v1/rag/query`, `/v1/chart`, `/v1/research`, `/v1/web/search`, `/v1/index/rebuild`
- [x] Add predictable error handling and response envelopes *(baseline)*

## 4) Streamlit client
- [x] Build chat interface in `app.py`
- [x] Wire HTTP calls to FastAPI routes
- [x] Render text, chart JSON, and markdown research reports

## 5) Validation
- [ ] Smoke test each route with one happy-path request
- [ ] Validate Feb anomaly and Mar credit flows in chart + research paths
- [ ] Update README run instructions for three processes (Ollama, FastAPI, Streamlit)

## 6) Hardening (after happy path)
- [ ] Optional pytest smoke tests
- [ ] Improve intent classifier (LLM-assisted fallback)
- [ ] Add lightweight caching for index/data loading
