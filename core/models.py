from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str


class IntentRequest(BaseModel):
    message: str
    messages: list[Message] = Field(default_factory=list)


class IntentResponse(BaseModel):
    intent: Literal["rag", "chart", "research", "web"]
    confidence: float = 0.7
    reason: str = ""


class RagRequest(BaseModel):
    message: str
    messages: list[Message] = Field(default_factory=list)
    top_k: int = 4


class SourceItem(BaseModel):
    source: str
    snippet: str = ""


class RagResponse(BaseModel):
    text: str
    sources: list[SourceItem] = Field(default_factory=list)


class ChartRequest(BaseModel):
    message: str
    messages: list[Message] = Field(default_factory=list)
    chart_type: Literal["trend", "breakdown", "compare"] | None = None


class ChartResponse(BaseModel):
    text: str
    plotly_json: str
    chart_type: str


class WebSearchRequest(BaseModel):
    message: str
    messages: list[Message] = Field(default_factory=list)
    max_results: int = 5


class WebSearchResponse(BaseModel):
    text: str
    sources: list[SourceItem] = Field(default_factory=list)


class ResearchRequest(BaseModel):
    message: str
    messages: list[Message] = Field(default_factory=list)


class ResearchResponse(BaseModel):
    markdown: str
    sources: list[SourceItem] = Field(default_factory=list)


class RebuildIndexResponse(BaseModel):
    status: str
    detail: str

