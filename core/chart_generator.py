from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import plotly.express as px


def _apply_mockup_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#141a24",
        plot_bgcolor="#0f1522",
        font={"color": "#e5e7eb", "size": 13},
        title={"font": {"size": 16, "color": "#e5e7eb"}},
        margin={"l": 40, "r": 20, "t": 52, "b": 42},
        xaxis={
            "showgrid": False,
            "linecolor": "#2f3b52",
            "tickfont": {"color": "#c8d1dd"},
            "title": {"font": {"color": "#c8d1dd"}},
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#253146",
            "zeroline": False,
            "tickfont": {"color": "#c8d1dd"},
            "title": {"font": {"color": "#c8d1dd"}},
        },
    )
    return fig


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
        fig.update_traces(line={"color": "#7aa2ff", "width": 3}, marker={"color": "#7aa2ff", "size": 8})
        text = "Showing monthly total due trend from billing summaries."
    elif chart_kind == "breakdown":
        latest = summaries[-1]
        rows = [{"category": x["category"], "amount": x["amount"]} for x in latest["line_items"]]
        fig = px.bar(
            rows,
            x="category",
            y="amount",
            title=f"Line item breakdown - {latest['period']['label']}",
            color="category",
            color_discrete_sequence=["#4da3ff", "#f08a3e", "#ff5d5d", "#3fb950", "#bc8cff", "#8b949e"],
        )
        text = f"Showing line-item category breakdown for {latest['period']['label']}."
    else:  # compare
        rows = [{"period": s["period"]["label"], "total_due": s["totals"]["total_due"]} for s in summaries[-3:]]
        fig = px.bar(rows, x="period", y="total_due", title="Last 3 months comparison", color="period")
        text = "Comparing total due for the last three months."

    fig = _apply_mockup_theme(fig)
    fig.update_layout(showlegend=False)
    return text, fig.to_json(), chart_kind

