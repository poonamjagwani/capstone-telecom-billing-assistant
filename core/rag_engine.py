from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.models import SourceItem


class RagEngine:
    """
    Lightweight phase-2 starter RAG:
    - builds a local JSON index from policy and billing summary files
    - returns heuristic matches by keyword overlap
    This keeps the API functional before FAISS wiring is completed.
    """

    def __init__(self, index_dir: Path, billing_dir: Path, policies_dir: Path) -> None:
        self.index_dir = index_dir
        self.billing_dir = billing_dir
        self.policies_dir = policies_dir
        self.index_file = index_dir / "summary_index.json"
        self._docs: list[dict[str, Any]] = []

    def build_index(self, force_rebuild: bool = False) -> dict[str, str]:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        if self.index_file.exists() and not force_rebuild:
            self._docs = json.loads(self.index_file.read_text(encoding="utf-8"))
            return {"status": "ok", "detail": "Loaded existing local summary index."}

        docs: list[dict[str, Any]] = []
        for path in sorted(self.policies_dir.glob("*_summary.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            text = " ".join(
                [
                    payload.get("title", ""),
                    payload.get("short_description", ""),
                    " ".join(payload.get("topics", [])),
                ]
            )
            docs.append({"source": path.name, "text": text})

        for path in sorted(self.billing_dir.glob("billing_*_summary.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            line_items = " ".join(x.get("description", "") for x in payload.get("line_items", []))
            notes = " ".join(payload.get("notes", []))
            text = f"{payload['period']['label']} {line_items} {notes}"
            docs.append({"source": path.name, "text": text})

        self._docs = docs
        self.index_file.write_text(json.dumps(docs, indent=2), encoding="utf-8")
        return {"status": "ok", "detail": f"Built local summary index with {len(docs)} documents."}

    def query(self, question: str, top_k: int = 4) -> tuple[str, list[SourceItem]]:
        if not self._docs:
            self.build_index(force_rebuild=False)

        q_terms = {t for t in question.lower().split() if len(t) > 2}
        scored: list[tuple[int, dict[str, Any]]] = []
        for d in self._docs:
            text = d["text"].lower()
            score = sum(1 for t in q_terms if t in text)
            if score > 0:
                scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        if not top:
            return (
                "I could not find a strong match in the current document summaries. Try rephrasing with a month, charge type, or policy topic.",
                [],
            )
        sources = [SourceItem(source=d["source"], snippet=d["text"][:220]) for _, d in top]
        answer_lines = [f"- {s.source}" for s in sources]
        return "Relevant documents found:\n" + "\n".join(answer_lines), sources

