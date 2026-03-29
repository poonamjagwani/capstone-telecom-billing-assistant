from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import httpx
import plotly.io as pio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
TIMEOUT_SEC = int(os.getenv("HTTP_TIMEOUT_SEC", "30"))

st.set_page_config(page_title="Telecom Billing Assistant", page_icon="💳", layout="wide")
st.markdown(
    """
<style>
    :root {
        --bg-dark: #0e1117;
        --bg-sidebar: #161b22;
        --bg-card: #1c2333;
        --text-primary: #fafafa;
        --text-secondary: #8b949e;
        --border: #30363d;
        --accent: #ff4b4b;
        --success: #3fb950;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-dark) !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    div[data-testid="stDecoration"],
    div[data-testid="stToolbar"] {
        background: var(--bg-dark) !important;
    }
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stAppViewContainer"] > section.main,
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stBottomBlockContainer"] {
        background-color: var(--bg-dark) !important;
    }
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {
        background-color: var(--bg-dark) !important;
    }
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] input {
        background-color: #111827 !important;
        color: #e5e7eb !important;
        border: 1px solid var(--border) !important;
    }
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-primary);
    }
    .block-container {
        max-width: 1280px;
        padding-top: 1.1rem;
        background-color: var(--bg-dark) !important;
    }
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        border: 1px solid var(--border) !important;
        color: #e5e7eb !important;
    }
    div[data-baseweb="select"] svg {
        fill: #9ca3af !important;
    }
    .stTextInput > div > div > input {
        background-color: #111827 !important;
        border: 1px solid var(--border) !important;
        color: #e5e7eb !important;
    }
    .stSlider [data-baseweb="slider"] {
        color: #e5e7eb !important;
    }
    div[data-testid="stChatMessage"] {
        background: #141a24;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.4rem 0.65rem;
    }
    div[data-testid="stChatMessage"] p {
        color: #e5e7eb !important;
    }
    div[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"],
    div[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] * {
        color: #e5e7eb !important;
    }
    div[data-testid="stChatMessage"] a {
        color: #8fc7ff !important;
    }
    div[data-testid="stChatMessage"] code,
    div[data-testid="stChatMessage"] pre,
    div[data-testid="stExpander"] code,
    div[data-testid="stExpander"] pre {
        background: #1b2433 !important;
        color: #e5e7eb !important;
        border: 1px solid #2d3646 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] strong,
    div[data-testid="stChatMessage"] code {
        color: #e5e7eb !important;
    }
    div[data-testid="stExpander"] {
        background: #141a24 !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] details > div {
        background: #141a24 !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] div[role="button"] {
        color: #e5e7eb !important;
        background: #141a24 !important;
    }
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] li,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] strong {
        color: #e5e7eb !important;
    }
    div[data-testid="stExpander"] svg {
        fill: #e5e7eb !important;
    }
    [data-testid="stPlotlyChart"] > div {
        border: 1px solid #2b3445;
        border-radius: 10px;
        background: #141a24;
        padding: 6px;
    }
    div[data-testid="stButton"] > button {
        border-radius: 8px;
        border: 1px solid var(--border);
        background: #111827;
        color: #dbe4ee;
        height: 2.05rem;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #4b5563;
        color: #ffffff;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(90deg, #ff5d5d 0%, #f0883e 100%) !important;
        border: 1px solid #ff6b57 !important;
        color: #ffffff !important;
        box-shadow: 0 0 0 1px rgba(255, 107, 87, 0.2) inset;
    }
    .top-strip {
        height: 12px;
        border-radius: 4px;
        background: linear-gradient(90deg, #ff5d5d 0%, #f0883e 100%);
        margin-bottom: 0.75rem;
    }
    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border);
    }
    .brand-logo {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        background: linear-gradient(135deg, var(--accent), #f0883e);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .card {
        border: 1px solid var(--border);
        background: var(--bg-card);
        border-radius: 10px;
        padding: 12px 12px 11px 12px;
        margin: 6px 0;
    }
    .profile-title {
        margin: 0 0 11px 0;
        color: #cdd8e6;
        font-size: 0.72rem;
        letter-spacing: 0.2px;
        font-weight: 650;
        text-transform: none;
    }
    .profile-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 11px 14px;
    }
    .profile-label {
        margin: 0 0 2px 0;
        color: #9ba6b2;
        font-size: 0.58rem;
        letter-spacing: 1px;
        font-weight: 700;
    }
    .profile-value {
        margin: 0;
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 760;
        line-height: 1.2;
    }
    .tiny {
        color: #8b949e;
        font-size: 0.72rem;
    }
    .tab-wrap {
        border-top: 1px solid #202938;
        border-bottom: 1px solid #202938;
        padding: 0.55rem 0 0.45rem 0;
        margin-bottom: 0.55rem;
    }
    div[role="radiogroup"] {
        gap: 10px;
    }
    div[role="radiogroup"] label {
        background: #111827 !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 7px 12px !important;
    }
    div[role="radiogroup"] label p {
        color: #dbe4ee !important;
        font-size: 0.86rem !important;
    }
    div[role="radiogroup"] label[data-selected="true"] {
        background: linear-gradient(90deg, #ff5d5d 0%, #f0883e 100%) !important;
        border-color: #ff6b57 !important;
    }
    div[role="radiogroup"] label[data-selected="true"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .section-title {
        margin: 0.2rem 0 0.35rem 0;
        color: #b6bfca;
        font-size: 0.72rem;
        letter-spacing: 1.1px;
        text-transform: uppercase;
    }
    .ui-subheader {
        color: #9ca3af;
        font-size: 0.85rem;
        letter-spacing: 0.4px;
        margin-top: -0.15rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "messages_by_tab" not in st.session_state:
    st.session_state.messages_by_tab = {
        "billing": [],
        "charts": [],
        "dispute": [],
        "web": [],
    }
if "last_health" not in st.session_state:
    st.session_state.last_health = None
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""
if "ui_tab" not in st.session_state:
    st.session_state.ui_tab = "billing"
if "mode_select" not in st.session_state:
    st.session_state.mode_select = "auto-intent"
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "Ollama (llama3.2:3b)"
if "requested_mode" not in st.session_state:
    st.session_state.requested_mode = ""
if "ui_tab_label" not in st.session_state:
    st.session_state.ui_tab_label = "Billing Q&A"


def _safe_error_text(exc: Exception) -> str:
    return str(exc).splitlines()[0][:220]


def _trim_text(text: str, max_len: int = 320) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def _post(base_url: str, path: str, payload: dict) -> dict:
    with httpx.Client(timeout=TIMEOUT_SEC) as client:
        r = client.post(f"{base_url}{path}", json=payload)
        r.raise_for_status()
        return r.json()


def _get(base_url: str, path: str) -> dict:
    with httpx.Client(timeout=TIMEOUT_SEC) as client:
        r = client.get(f"{base_url}{path}")
        r.raise_for_status()
        return r.json()


def _customer_profile_from_billing_data() -> dict[str, str]:
    fallback = {
        "name": "Sarah Mitchell",
        "account": "TEL-2025-78432",
        "plan": "Unlimited Plus",
        "monthly": "$85.00/mo",
    }
    try:
        billing_dir = Path(__file__).resolve().parent / "data" / "billing"
        summaries = sorted(billing_dir.glob("billing_*_summary.json"))
        if not summaries:
            return fallback
        latest = json.loads(summaries[-1].read_text(encoding="utf-8"))
        account = latest.get("account", {})
        plan = latest.get("plan", {})
        monthly_charge = float(plan.get("monthly_charge", 85.0))
        return {
            "name": str(account.get("customer_name", fallback["name"])),
            "account": str(account.get("id", fallback["account"])),
            "plan": str(plan.get("name", fallback["plan"])),
            "monthly": f"${monthly_charge:.2f}/mo",
        }
    except Exception:
        return fallback


st.sidebar.markdown(
    """
<div class="brand-wrap">
  <div class="brand-logo">💳</div>
  <div><b>Telecom Billing Assistant</b><br/><span style="color:#8b949e;font-size:12px;">AI Billing Intelligence</span></div>
</div>
""",
    unsafe_allow_html=True,
)
st.sidebar.header("Controls")
# Apply tab-triggered mode change *before* creating mode widget.
if st.session_state.requested_mode:
    st.session_state.mode_select = st.session_state.requested_mode
    st.session_state.requested_mode = ""


def _sync_tab_from_sidebar_mode() -> None:
    mode_to_tab_local = {
        "auto-intent": "billing",
        "rag": "billing",
        "chart": "charts",
        "research": "dispute",
        "web": "web",
    }
    st.session_state.ui_tab = mode_to_tab_local.get(st.session_state.mode_select, "billing")

mode = st.sidebar.selectbox(
    "Mode",
    ["auto-intent", "rag", "chart", "research", "web"],
    key="mode_select",
    on_change=_sync_tab_from_sidebar_mode,
)
st.sidebar.caption(f"Selected mode: {mode}")

api_base_url = st.sidebar.text_input("API base URL", value=DEFAULT_API_BASE_URL).strip()
st.sidebar.caption(f"Timeout: {TIMEOUT_SEC}s")
st.sidebar.markdown("##### LLM Provider")
st.sidebar.selectbox("Provider", ["Ollama (llama3.2:3b)"], index=0, key="llm_provider", label_visibility="collapsed")
st.sidebar.caption(f"Selected provider: {st.session_state.llm_provider}")
st.sidebar.markdown("##### Temperature")
st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.1, step=0.1, disabled=True)

col_a, col_b = st.sidebar.columns(2)
if col_a.button("Health check", use_container_width=True):
    try:
        st.session_state.last_health = _get(api_base_url, "/health")
    except Exception as exc:  # pragma: no cover
        st.session_state.last_health = {"status": "error", "detail": _safe_error_text(exc)}
if col_b.button("Clear chat", use_container_width=True):
    st.session_state.messages = []
    st.session_state.messages_by_tab = {
        "billing": [],
        "charts": [],
        "dispute": [],
        "web": [],
    }

if st.session_state.last_health:
    health = st.session_state.last_health
    if health.get("status") == "ok":
        st.sidebar.success("API healthy")
    else:
        st.sidebar.error("API unhealthy")
    st.sidebar.json(health)

st.sidebar.markdown("### Customer Snapshot")
profile = _customer_profile_from_billing_data()
st.sidebar.markdown(
    f"""
<div class="card">
  <p class="profile-title">Customer Profile</p>
  <div class="profile-grid">
    <div>
      <p class="profile-label">NAME</p>
      <p class="profile-value">{profile["name"]}</p>
    </div>
    <div>
      <p class="profile-label">ACCOUNT</p>
      <p class="profile-value">{profile["account"]}</p>
    </div>
    <div>
      <p class="profile-label">PLAN</p>
      <p class="profile-value">{profile["plan"]}</p>
    </div>
    <div>
      <p class="profile-label">MONTHLY</p>
      <p class="profile-value">{profile["monthly"]}</p>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
st.sidebar.markdown("### Capabilities")
st.sidebar.markdown("- RAG Q&A")
st.sidebar.markdown("- Billing Charts")
st.sidebar.markdown("- Dispute Research")
st.sidebar.markdown("- Web Search")
st.sidebar.caption("Use mode selector for deterministic testing, or auto-intent for routing.")
st.sidebar.markdown("### Knowledge Base Status")
st.sidebar.markdown(
    """
<div class="card">
  <span class="tiny">Billing PDFs</span><br/><b>6 indexed</b><br/>
  <span class="tiny">Policy Docs</span><br/><b>4 indexed</b><br/>
  <span class="tiny">FAISS Vectors</span><br/><b>247</b><br/>
  <span class="tiny">Embedding Model</span><br/><b>nomic-embed-text</b>
</div>
""",
    unsafe_allow_html=True,
)
if st.sidebar.button("Rebuild Index", use_container_width=True):
    try:
        result = _post(api_base_url, "/v1/index/rebuild", {})
        if result.get("status") == "ok":
            st.sidebar.success(result.get("detail", "Index rebuilt."))
        else:
            st.sidebar.error(result.get("detail", "Index rebuild failed."))
    except Exception as exc:  # pragma: no cover
        st.sidebar.error(f"Index rebuild failed: {_safe_error_text(exc)}")

st.markdown('<div class="top-strip"></div>', unsafe_allow_html=True)
st.title("Telecom Billing Assistant")
st.markdown(
    f'<p class="ui-subheader">Telecom bill analysis, dispute assistance, and market plan search • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
    unsafe_allow_html=True,
)

st.markdown('<div class="tab-wrap">', unsafe_allow_html=True)
tab_to_label = {
    "billing": "Billing Q&A",
    "charts": "Visual Charts",
    "dispute": "Dispute Analysis",
    "web": "Web Search",
}
label_to_tab = {v: k for k, v in tab_to_label.items()}
tab_to_mode = {
    "billing": "rag",
    "charts": "chart",
    "dispute": "research",
    "web": "web",
}
# Do not overwrite this on every rerun; it would lock selection.
if st.session_state.ui_tab_label not in label_to_tab:
    st.session_state.ui_tab_label = tab_to_label.get(st.session_state.ui_tab, "Billing Q&A")
tabs_col, power_col = st.columns([4.2, 1.0])
with tabs_col:
    selected_label = st.radio(
        "Scenario",
        options=["Billing Q&A", "Visual Charts", "Dispute Analysis", "Web Search"],
        horizontal=True,
        key="ui_tab_label",
        label_visibility="collapsed",
    )
    st.session_state.ui_tab = label_to_tab[selected_label]
    st.session_state.requested_mode = tab_to_mode[st.session_state.ui_tab]
with power_col:
    st.markdown('<p style="text-align:right;color:#ff8585;font-size:12px;margin-top:6px;">AI Powered</p>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

effective_mode = {
    "billing": "rag",
    "charts": "chart",
    "dispute": "research",
    "web": "web",
}.get(st.session_state.ui_tab, mode)

active_tab = st.session_state.ui_tab
active_messages = st.session_state.messages_by_tab.setdefault(active_tab, [])

for raw_msg in active_messages:
    m = raw_msg if isinstance(raw_msg, dict) else {"role": "assistant", "content": str(raw_msg)}
    role = m.get("role", "assistant")
    with st.chat_message(role):
        kind = m.get("kind")
        if kind == "chart" and m.get("plotly_json"):
            st.markdown(m.get("chart_text", m.get("content", "")))
            try:
                fig = pio.from_json(m["plotly_json"])
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.markdown(m.get("content", "Chart unavailable in history."))
        elif kind == "research_markdown":
            st.markdown(m.get("markdown", m.get("content", "")))
        else:
            st.markdown(m.get("content", ""))
        saved_sources = m.get("sources", [])
        if isinstance(saved_sources, list) and saved_sources:
            with st.expander("Sources"):
                for s in saved_sources[:8]:
                    if isinstance(s, dict):
                        st.markdown(
                            f"- **{_trim_text(s.get('source', ''), 120)}**  \n{_trim_text(s.get('snippet', ''), 300)}"
                        )

typed_prompt = st.chat_input("Ask about your billing, request charts, dispute charges, or search the web...")
prompt = typed_prompt or st.session_state.pending_prompt
if prompt:
    st.session_state.pending_prompt = ""
    active_messages.append({"role": "user", "content": prompt})
    st.session_state.messages = active_messages
    with st.chat_message("user"):
        st.markdown(prompt)

    payload_messages = [
        {"role": msg.get("role", "assistant"), "content": msg.get("content", "")}
        for msg in active_messages[-20:]
        if isinstance(msg, dict)
    ]
    payload = {"message": prompt, "messages": payload_messages}
    route = {
        "rag": "/v1/rag/query",
        "chart": "/v1/chart",
        "research": "/v1/research",
        "web": "/v1/web/search",
    }.get(effective_mode, "")

    try:
        if mode == "auto-intent":
            intent_res = _post(api_base_url, "/v1/intent", payload)
            intent = intent_res["intent"]
            route = {
                "rag": "/v1/rag/query",
                "chart": "/v1/chart",
                "research": "/v1/research",
                "web": "/v1/web/search",
            }[intent]
        else:
            intent_res = {"intent": effective_mode}

        data = _post(api_base_url, route, payload)
        with st.chat_message("assistant"):
            if route == "/v1/chart":
                st.markdown(data["text"])
                fig = pio.from_json(data["plotly_json"])
                st.plotly_chart(fig, use_container_width=True)
                answer = f"{data['text']}\n\n(Chart type: {data['chart_type']})"
                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "kind": "chart",
                    "chart_text": data["text"],
                    "chart_type": data["chart_type"],
                    "plotly_json": data["plotly_json"],
                    "sources": [],
                }
            elif route == "/v1/research":
                st.markdown(data["markdown"])
                answer = data["markdown"]
                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "kind": "research_markdown",
                    "markdown": data["markdown"],
                    "sources": [],
                }
            else:
                text = data.get("text", "No text response.")
                st.markdown(text)
                answer = text
                assistant_message = {"role": "assistant", "content": answer, "sources": []}

            sources = data.get("sources", [])
            if sources:
                with st.expander("Sources"):
                    for s in sources[:8]:
                        st.markdown(
                            f"- **{_trim_text(s.get('source', ''), 120)}**  \n{_trim_text(s.get('snippet', ''), 300)}"
                        )
                assistant_message["sources"] = sources[:8]

        active_messages.append(assistant_message)
        st.session_state.messages = active_messages
    except Exception as exc:
        err = f"Request failed: {_safe_error_text(exc)}"
        with st.chat_message("assistant"):
            st.error(err)
        active_messages.append({"role": "assistant", "content": err})
        st.session_state.messages = active_messages

