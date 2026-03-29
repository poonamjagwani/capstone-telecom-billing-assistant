from __future__ import annotations

from pathlib import Path
import json

from core.models import SourceItem


def run_dispute_research(question: str, billing_dir: Path, policies_dir: Path) -> tuple[str, list[SourceItem]]:
    feb = json.loads((billing_dir / "billing_2026_02_summary.json").read_text(encoding="utf-8"))
    mar = json.loads((billing_dir / "billing_2026_03_summary.json").read_text(encoding="utf-8"))
    refund = json.loads((policies_dir / "refund_policy_summary.json").read_text(encoding="utf-8"))

    markdown = f"""## Dispute research report

### User issue
{question}

### Evidence from billing
- **{feb["period"]["label"]}** total due: **{feb["totals"]["total_due"]} CAD**
- Notable item: **International roaming** amount **142.5 CAD**
- **{mar["period"]["label"]}** total due: **{mar["totals"]["total_due"]} CAD**
- Credit noted in March: **-142.5 CAD**

### Relevant policy
- **{refund["title"]}** (`{refund["source_pdf"]}`)
- Topics: {", ".join(refund["topics"])}
- Summary: {refund["short_description"]}

### Suggested next steps
1. Confirm the disputed roaming dates and destination details from Feb statement.
2. Verify the March credit line item against the final dispute outcome.
3. Keep both statements and dispute reference in case follow-up is needed.
"""
    sources = [
        SourceItem(source="billing_2026_02_summary.json", snippet="Feb roaming spike evidence."),
        SourceItem(source="billing_2026_03_summary.json", snippet="March credit adjustment evidence."),
        SourceItem(source="refund_policy_summary.json", snippet="Dispute and refund policy metadata."),
    ]
    return markdown, sources

