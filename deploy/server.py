from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from core.chart_generator import generate_chart
from core.llm_provider import llm_health_hint
from core.models import (
    ChartRequest,
    ChartResponse,
    IntentRequest,
    IntentResponse,
    RagRequest,
    RagResponse,
    RebuildIndexResponse,
    ResearchRequest,
    ResearchResponse,
    WebSearchRequest,
    WebSearchResponse,
)
from core.rag_engine import RagEngine
from core.research_agent import run_dispute_research
from core.router import classify_intent
from core.tool_agent import web_search

settings = get_settings()
rag_engine = RagEngine(settings.index_dir, settings.billing_dir, settings.policies_dir)


@asynccontextmanager
async def lifespan(_: FastAPI):
    rag_engine.build_index(force_rebuild=False)
    yield


app = FastAPI(title="Telecom Billing Assistant API", version="0.1.0", lifespan=lifespan)
if settings.allow_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "dependencies_ok": True,
        "llm_hint": llm_health_hint(settings),
    }


@app.post("/v1/intent", response_model=IntentResponse)
def intent(req: IntentRequest) -> IntentResponse:
    return classify_intent(req.message)


@app.post("/v1/rag/query", response_model=RagResponse)
def rag_query(req: RagRequest) -> RagResponse:
    text, sources = rag_engine.query(req.message, top_k=req.top_k)
    return RagResponse(text=text, sources=sources)


@app.post("/v1/chart", response_model=ChartResponse)
def chart(req: ChartRequest) -> ChartResponse:
    text, plotly_json, chart_type = generate_chart(req.message, settings.billing_dir, req.chart_type)
    return ChartResponse(text=text, plotly_json=plotly_json, chart_type=chart_type)


@app.post("/v1/research", response_model=ResearchResponse)
def research(req: ResearchRequest) -> ResearchResponse:
    markdown, sources = run_dispute_research(req.message, settings.billing_dir, settings.policies_dir)
    return ResearchResponse(markdown=markdown, sources=sources)


@app.post("/v1/web/search", response_model=WebSearchResponse)
def web(req: WebSearchRequest) -> WebSearchResponse:
    try:
        text, sources = web_search(req.message, req.max_results)
        return WebSearchResponse(text=text, sources=sources)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=f"Web search unavailable: {exc}") from exc


@app.post("/v1/index/rebuild", response_model=RebuildIndexResponse)
def rebuild() -> RebuildIndexResponse:
    result = rag_engine.build_index(force_rebuild=True)
    return RebuildIndexResponse(status=result["status"], detail=result["detail"])

