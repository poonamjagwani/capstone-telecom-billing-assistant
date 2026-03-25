# Telecom Billing Assistant (Capstone)

An **AI-assisted telecom billing demo**: answer questions from policy and bill PDFs (**RAG**), plot trends from structured billing data (**Plotly**), run **dispute-style research**, and use **web search** — with a **FastAPI** backend and **Streamlit** UI (planned). All customer names, carriers, and amounts are **synthetic**.

**Repository folder:** `capstone-telecom-billing-assistant`

**Application plan (single source of truth):** [Telecom_Billing_Assistant_app_plan_FastAPI.md](Telecom_Billing_Assistant_app_plan_FastAPI.md) — architecture, API routes, dataset conventions (§8), and implementation phases (§12). There is no separate “alternate” plan document in this repo.

---

## Status

| Phase | Scope | Status |
|-------|--------|--------|
| **1 — Data** | Synthetic policy + billing PDFs, per-PDF `*_summary.json`, generator script | **Done** |
| **2 — App** | `core/`, FastAPI (`deploy/server.py`), Streamlit (`app.py`), FAISS from PDFs, Ollama + optional OpenAI-compatible API | Not started — follow the application plan (§12) |

---

## What’s in this repo (today)

- **`data/policies/`** — Four NovaTel-style policy PDFs + matching `*_summary.json` (billing & payment; refund & dispute; roaming & international; plan & fair usage).
- **`data/billing/`** — Six monthly statements (Oct 2025 → Mar 2026) + `*_summary.json`, plus optional **`billing_rollup.json`**. The story includes a **Feb roaming spike** and a **Mar billing credit** for demos.
- **`scripts/generate_data.py`** — Single source of truth: regenerates every PDF and JSON so numbers stay aligned.
- **Application plan:** [Telecom_Billing_Assistant_app_plan_FastAPI.md](Telecom_Billing_Assistant_app_plan_FastAPI.md) — full build spec.
- **UI mockup:** [Telecom_Billing_Assistant_ui_mockup.html](Telecom_Billing_Assistant_ui_mockup.html) — static HTML reference (not the live app).

---

## Quick start (Phase 1 — regenerate data)

Python 3.10+ recommended.

```bash
cd capstone-telecom-billing-assistant
pip install -r requirements.txt
python scripts/generate_data.py
```

This writes:

- `data/policies/` — 4 PDFs + 4 `*_summary.json`
- `data/billing/` — 6 PDFs + 6 `*_summary.json` + `billing_rollup.json`

---

## Planned architecture (Phase 2)

- **FastAPI** — Routes such as `/health`, `/v1/rag/query`, `/v1/chart`, `/v1/research`, `/v1/web/search`, `/v1/intent` (see plan §5).
- **Streamlit** — UI only; calls the API over HTTP (stateless `messages[]` recommended in plan §10).
- **RAG** — FAISS index built from policy + billing PDFs; charts read **`billing/*_summary.json`**, not re-parsed PDF text (plan §8).

Full layout, API contract, and checklist: **[Telecom_Billing_Assistant_app_plan_FastAPI.md](Telecom_Billing_Assistant_app_plan_FastAPI.md)** (same document as above).

---

## Dependencies (Phase 1)

| Package | Purpose |
|---------|---------|
| `fpdf2` | Generate synthetic PDFs in `generate_data.py` |

Phase 2 will add FastAPI, Streamlit, embeddings/FAISS, etc. — see the application plan and future `requirements.txt` updates.

---

## Git

This repo includes a **`.gitignore`** for Python, virtualenvs, `.env`, IDE files, and future index artifacts.

Initialize and make your first commit when ready:

```bash
cd capstone-telecom-billing-assistant
git init
git add -A
git status   # review
git commit -m "Phase 1: synthetic data, generator script, application plan, README"
```

---

## Disclaimer

Content is **fictional** and for **education / demonstration** only. It does not represent any real carrier’s policies or bills.
