from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import plotly.express as px


def _load_billing_summaries(billing_dir: Path) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for path in sorted(billing_dir.glob("billing_*_summary.json")):
        summaries.append(json.loads(path.read_text(encoding="utf-8")))
    if not summaries:
        raise FileNotFoundError(f"No billing summaries found in {billing_dir}")
    return summaries


def detect_chart_type(message: str) -> str:
    text = message.lower()
    if any(k in text for k in ["breakdown", "category", "categories", "line item"]):
        return "breakdown"
    if any(k in text for k in ["compare", "comparison", "vs"]):
        return "compare"
    return "trend"


def generate_chart(message: str, billing_dir: Path, chart_type: str | None = None) -> tuple[str, str, str]:
    chart_kind = chart_type or detect_chart_type(message)
    summaries = _load_billing_summaries(billing_dir)

    if chart_kind == "trend":
        rows = [{"period": s["period"]["label"], "total_due": s["totals"]["total_due"]} for s in summaries]
        fig = px.line(rows, x="period", y="total_due", markers=True, title="Monthly total due (CAD)")
        text = "Showing monthly total due trend from billing summaries."
    elif chart_kind == "breakdown":
        latest = summaries[-1]
        rows = [{"category": x["category"], "amount": x["amount"]} for x in latest["line_items"]]
        fig = px.bar(rows, x="category", y="amount", title=f"Line item breakdown - {latest['period']['label']}")
        text = f"Showing line-item category breakdown for {latest['period']['label']}."
    else:  # compare
        rows = [{"period": s["period"]["label"], "total_due": s["totals"]["total_due"]} for s in summaries[-3:]]
        fig = px.bar(rows, x="period", y="total_due", title="Last 3 months comparison")
        text = "Comparing total due for the last three months."

    return text, fig.to_json(), chart_kind

