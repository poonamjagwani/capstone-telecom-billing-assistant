from __future__ import annotations

from core.models import IntentResponse


def classify_intent(message: str) -> IntentResponse:
    text = message.lower()
    if any(k in text for k in ["chart", "trend", "graph", "breakdown", "plot", "month"]):
        return IntentResponse(intent="chart", confidence=0.9, reason="Detected chart keywords.")
    # Keep policy-style questions in document Q&A instead of dispute report mode.
    if "policy" in text and any(k in text for k in ["refund", "overcharg", "billing error", "charge"]):
        return IntentResponse(intent="rag", confidence=0.92, reason="Detected policy Q&A intent.")
    if any(k in text for k in ["dispute", "refund", "chargeback", "investigate", "research"]):
        return IntentResponse(intent="research", confidence=0.9, reason="Detected dispute/research intent.")
    if any(k in text for k in ["web", "search", "news", "online", "internet"]):
        return IntentResponse(intent="web", confidence=0.85, reason="Detected web-search intent.")
    return IntentResponse(intent="rag", confidence=0.75, reason="Defaulting to document-grounded Q&A.")

