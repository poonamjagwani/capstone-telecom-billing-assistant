from __future__ import annotations

import time
from duckduckgo_search import DDGS

from core.models import SourceItem


def _query_variants(query: str) -> list[str]:
    q = " ".join(query.split())
    q_lower = q.lower()
    variants = [q]
    # Better hit-rate for telecom market comparison prompts.
    if ("competitor" in q_lower or "market" in q_lower) and ("plan" in q_lower or "plans" in q_lower):
        variants.extend(
            [
                f"{q} canada wireless plans comparison",
                "best canada mobile phone plans comparison rogers bell telus freedom",
                "canada telecom competitor plans prepaid postpaid comparison",
            ]
        )
    return variants


def _dedupe_hits(hits: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for h in hits:
        url = (h.get("href") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(h)
    return out


def web_search(query: str, max_results: int = 5) -> tuple[str, list[SourceItem]]:
    variants = _query_variants(query)
    collected: list[dict] = []
    errors: list[str] = []
    # Try multiple variants and small retries to handle intermittent DDG blocks.
    for q in variants:
        for attempt in range(2):
            try:
                with DDGS() as ddgs:
                    hits = list(ddgs.text(q, max_results=max_results))
                if hits:
                    collected.extend(hits)
                    break
            except Exception as exc:
                errors.append(str(exc))
                time.sleep(0.5 * (attempt + 1))

    deduped = _dedupe_hits(collected)[: max_results * 2]
    if not deduped:
        suffix = f" Provider errors: {errors[0][:140]}" if errors else ""
        return (
            "No web results found. Try a more specific prompt like "
            "'compare canadian mobile plans by data and price'."
            + suffix,
            [],
        )

    sources = [
        SourceItem(source=h.get("href", ""), snippet=h.get("body", ""))
        for h in deduped
        if h.get("href")
    ][:max_results]
    lines = [f"- {h.get('title', 'Untitled')}: {h.get('body', '')}" for h in deduped[:max_results]]
    return "Top web findings:\n" + "\n".join(lines), sources

