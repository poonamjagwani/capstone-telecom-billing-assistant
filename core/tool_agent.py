from __future__ import annotations

from duckduckgo_search import DDGS

from core.models import SourceItem


def web_search(query: str, max_results: int = 5) -> tuple[str, list[SourceItem]]:
    with DDGS() as ddgs:
        hits = list(ddgs.text(query, max_results=max_results))
    if not hits:
        return "No web results found for this query.", []
    sources = [
        SourceItem(source=h.get("href", ""), snippet=h.get("body", ""))
        for h in hits
        if h.get("href")
    ]
    lines = [f"- {h.get('title', 'Untitled')}: {h.get('body', '')}" for h in hits[:5]]
    return "Top web findings:\n" + "\n".join(lines), sources

