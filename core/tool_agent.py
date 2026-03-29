from __future__ import annotations

import re
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
                "best canada mobile phone plans comparison rogers bell telus freedom fizz koodo virgin",
                "canada telecom competitor plans prepaid postpaid comparison",
            ]
        )
    if "canada" in q_lower and ("plan" in q_lower or "unlimited" in q_lower):
        variants.extend(
            [
                "canada unlimited mobile plans 2026 bell rogers telus freedom fizz koodo price",
                "cheapest canadian unlimited data plans comparison",
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


def _is_telecom_relevant(hit: dict) -> bool:
    text = f"{hit.get('title', '')} {hit.get('body', '')} {hit.get('href', '')}".lower()
    telecom_tokens = {
        "plan",
        "mobile",
        "cell",
        "wireless",
        "carrier",
        "canada",
        "rogers",
        "bell",
        "telus",
        "freedom",
        "koodo",
        "fizz",
        "virgin",
        "videotron",
        "data",
        "gb",
        "5g",
        "monthly",
    }
    # Hard drop obvious grammar/dictionary/linguistics pages.
    bad_tokens = {"cambridge dictionary", "merriam-webster", "there their they're", "grammar"}
    if any(b in text for b in bad_tokens):
        return False
    return any(t in text for t in telecom_tokens)


def _extract_monthly_prices(text: str) -> list[float]:
    prices: list[float] = []
    t = text.lower()
    patterns = [
        r"\$(\d{1,3}(?:\.\d{1,2})?)",
        r"(\d{1,3}(?:\.\d{1,2})?)\s*cad\b",
        r"\bcad\s*(\d{1,3}(?:\.\d{1,2})?)",
        r"(\d{1,3}(?:\.\d{1,2})?)\s*/\s*month",
        r"(\d{1,3}(?:\.\d{1,2})?)\s*per\s*month",
        r"(\d{1,3}(?:\.\d{1,2})?)\s*/\s*mo\b",
    ]
    for pat in patterns:
        for m in re.findall(pat, t, flags=re.IGNORECASE):
            try:
                value = float(m)
                if 5 <= value <= 300:
                    prices.append(value)
            except ValueError:
                continue
    # Preserve order while deduping close duplicates.
    deduped: list[float] = []
    for p in prices:
        if not any(abs(p - d) < 0.01 for d in deduped):
            deduped.append(p)
    return deduped


def _score_plan_hit(hit: dict, target_price: float) -> tuple[float, float | None]:
    combined = f"{hit.get('title', '')} {hit.get('body', '')}"
    prices = _extract_monthly_prices(combined)
    best_price = min(prices, key=lambda p: abs(p - target_price)) if prices else None
    # Lower score is better.
    score = abs(best_price - target_price) if best_price is not None else 1000.0
    body = (hit.get("body") or "").lower()
    if "unlimited" in body:
        score -= 5.0
    if "canada" in body:
        score -= 2.0
    return score, best_price


def _infer_target_price(query: str, default_price: float = 85.0) -> float:
    prices = _extract_monthly_prices(query)
    return prices[0] if prices else default_price


def _is_competitor_plan_query(query: str) -> bool:
    q = query.lower()
    return (
        ("competitor" in q or "compare" in q or "cheaper" in q or "market" in q)
        and ("plan" in q or "plans" in q or "unlimited" in q)
        and ("canada" in q or "cad" in q)
    )


def _fallback_competitor_options(target_price: float) -> tuple[str, list[SourceItem]]:
    options = [
        ("Freedom Mobile Unlimited 50GB", 45.0, "50GB high-speed data, throttled after cap"),
        ("Koodo Unlimited 30GB", 55.0, "30GB high-speed data, reduced speed after cap"),
        ("Public Mobile Unlimited 20GB", 40.0, "20GB high-speed data, value-focused plan"),
    ]
    lines: list[str] = []
    for name, price, desc in options:
        delta = price - target_price
        lines.append(f"- {name} - ~${price:.0f}/mo ({delta:+.0f} CAD vs your 85 CAD plan). {desc}")
    text = (
        "Cheaper competitor options near your current 85 CAD/month plan "
        "(fallback when live web snippets are unavailable):\n"
        + "\n".join(lines)
    )
    sources = [
        SourceItem(
            source="fallback://canada-competitor-plan-baseline",
            snippet="Demo-safe fallback options used because live search results were unavailable.",
        )
    ]
    return text, sources


def web_search(query: str, max_results: int = 5) -> tuple[str, list[SourceItem]]:
    variants = _query_variants(query)
    collected: list[dict] = []
    errors: list[str] = []
    # Try multiple variants and small retries to handle intermittent DDG blocks.
    for q in variants:
        for attempt in range(2):
            try:
                with DDGS() as ddgs:
                    hits = list(ddgs.text(q, max_results=max(max_results, 10)))
                if hits:
                    collected.extend(hits)
                    break
            except Exception as exc:
                errors.append(str(exc))
                time.sleep(0.5 * (attempt + 1))

    deduped = _dedupe_hits(collected)
    relevant = [h for h in deduped if _is_telecom_relevant(h)]
    if not relevant:
        relevant = deduped
    target_price = _infer_target_price(query, default_price=85.0)
    ranked = sorted(
        relevant,
        key=lambda h: _score_plan_hit(h, target_price)[0],
    )
    top_hits = ranked[: max_results * 2]
    if not top_hits:
        if _is_competitor_plan_query(query):
            return _fallback_competitor_options(target_price)
        suffix = f" Provider errors: {errors[0][:140]}" if errors else ""
        return (
            "No web results found. Try a more specific prompt like "
            "'compare canadian mobile plans by data and price'."
            + suffix,
            [],
        )

    sources = [
        SourceItem(source=h.get("href", ""), snippet=h.get("body", ""))
        for h in top_hits
        if h.get("href")
    ][:max_results]
    q_lower = query.lower()
    require_cheaper = "cheaper" in q_lower or "lower" in q_lower or "save" in q_lower
    prefer_unlimited = "unlimited" in q_lower
    priced_hits: list[tuple[dict, float]] = []
    for h in top_hits:
        _, price = _score_plan_hit(h, target_price)
        if price is None:
            continue
        if require_cheaper and price >= target_price:
            continue
        full_text = f"{h.get('title', '')} {h.get('body', '')}".lower()
        if prefer_unlimited and "unlimited" not in full_text:
            continue
        # Keep realistic mobile-plan prices and avoid obvious outliers.
        if 10 <= price <= 150:
            priced_hits.append((h, price))

    # Fallback for demo reliability: if unlimited-only filter is too strict, retry with priced telecom results.
    if not priced_hits and prefer_unlimited:
        for h in top_hits:
            _, price = _score_plan_hit(h, target_price)
            if price is None:
                continue
            if require_cheaper and price >= target_price:
                continue
            if 10 <= price <= 150:
                priced_hits.append((h, price))

    if not priced_hits:
        # Last fallback: show best telecom hits to avoid dead-end loop.
        fallback_lines = [
            f"- {h.get('title', 'Untitled')}: {h.get('body', '')}"
            for h in top_hits[:max_results]
        ]
        return ("Top telecom findings (priced snippets were limited):\n" + "\n".join(fallback_lines), sources)

    option_lines: list[str] = []
    final_sources: list[SourceItem] = []
    for h, price in priced_hits[:max_results]:
        body = h.get("body", "")
        title = h.get("title", "Untitled")
        delta = price - target_price
        delta_txt = f"{delta:+.0f} CAD vs your 85 CAD plan"
        option_lines.append(f"- {title} - ~${price:.0f}/mo ({delta_txt}). {body}")
        if h.get("href"):
            final_sources.append(SourceItem(source=h.get("href", ""), snippet=h.get("body", "")))

    header = (
        "Cheaper competitor options with explicit monthly pricing:\n"
        if require_cheaper
        else "Closest competitor options near your current 85 CAD/month plan:\n"
    )
    return (header + "\n".join(option_lines), final_sources[:max_results])

