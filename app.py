from __future__ import annotations

import json
import os

import httpx
import plotly.io as pio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
TIMEOUT_SEC = int(os.getenv("HTTP_TIMEOUT_SEC", "30"))

st.set_page_config(page_title="Telecom Billing Assistant", page_icon="💳", layout="wide")
st.title("AI Powered Telecom Billing Assistant")
st.caption("Phase 2 client (calls FastAPI routes)")

if "messages" not in st.session_state:
    st.session_state.messages = []

mode = st.sidebar.selectbox("Mode", ["auto-intent", "rag", "chart", "research", "web"])
st.sidebar.write(f"API: `{API_BASE_URL}`")


def _post(path: str, payload: dict) -> dict:
    with httpx.Client(timeout=TIMEOUT_SEC) as client:
        r = client.post(f"{API_BASE_URL}{path}", json=payload)
        r.raise_for_status()
        return r.json()


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask about bills, policies, trends, or disputes...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {"message": prompt, "messages": st.session_state.messages[-20:]}
    route = {
        "rag": "/v1/rag/query",
        "chart": "/v1/chart",
        "research": "/v1/research",
        "web": "/v1/web/search",
    }.get(mode, "")

    try:
        if mode == "auto-intent":
            intent = _post("/v1/intent", payload)["intent"]
            route = {
                "rag": "/v1/rag/query",
                "chart": "/v1/chart",
                "research": "/v1/research",
                "web": "/v1/web/search",
            }[intent]

        data = _post(route, payload)
        with st.chat_message("assistant"):
            if route == "/v1/chart":
                st.markdown(data["text"])
                fig = pio.from_json(data["plotly_json"])
                st.plotly_chart(fig, use_container_width=True)
                answer = f"{data['text']}\n\n(Chart type: {data['chart_type']})"
            elif route == "/v1/research":
                st.markdown(data["markdown"])
                answer = data["markdown"]
            else:
                text = data.get("text", "No text response.")
                st.markdown(text)
                answer = text

            sources = data.get("sources", [])
            if sources:
                with st.expander("Sources"):
                    st.json(sources)
                    answer += "\n\nSources:\n" + json.dumps(sources, indent=2)

        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as exc:
        err = f"Request failed: {exc}"
        with st.chat_message("assistant"):
            st.error(err)
        st.session_state.messages.append({"role": "assistant", "content": err})

