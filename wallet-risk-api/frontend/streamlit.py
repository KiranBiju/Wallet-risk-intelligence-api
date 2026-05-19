from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Configuration

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ANALYZE_ENDPOINT = f"{API_BASE_URL}/risk/score"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
REQUEST_TIMEOUT = 120

st.set_page_config(
    page_title="Wallet Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .risk-low {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.4rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: 700;
        display: inline-block;
    }
    .risk-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.4rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: 700;
        display: inline-block;
    }
    .risk-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.4rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: 700;
        display: inline-block;
    }
    .risk-unknown {
        background-color: #e5e7eb;
        color: #374151;
        padding: 0.4rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: 700;
        display: inline-block;
    }
    .pattern-chip {
        display: inline-block;
        background: #f3f4f6;
        padding: 0.35rem 0.65rem;
        margin: 0.2rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def validate_wallet(wallet: str) -> bool:
    """Basic Ethereum address validation."""
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", wallet.strip()))


@st.cache_data(ttl=60)
def check_health() -> Dict[str, Any]:
    try:
        resp = requests.get(HEALTH_ENDPOINT, timeout=10)
        return {
            "ok": resp.status_code == 200,
            "status_code": resp.status_code,
            "data": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {},
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@st.cache_data(show_spinner=False)
def analyze_wallet(wallet_address: str) -> Dict[str, Any]:
    payload = {"wallet": wallet_address}
    resp = requests.post(
        ANALYZE_ENDPOINT,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    
    return resp.json()

    return response.get("data", response)



def get_risk_css_class(risk_level: str) -> str:
    mapping = {
        "LOW": "risk-low",
        "MEDIUM": "risk-medium",
        "HIGH": "risk-high",
        "UNKNOWN": "risk-unknown",
    }
    return mapping.get((risk_level or "UNKNOWN").upper(), "risk-unknown")



def render_risk_badge(risk_level: str) -> None:
    css_class = get_risk_css_class(risk_level)
    st.markdown(
        f'<span class="{css_class}">{risk_level}</span>',
        unsafe_allow_html=True,
    )



def create_gauge(score: float) -> go.Figure:
    value = max(0.0, min(1.0, score)) * 100

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%", "font": {"size": 36}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"thickness": 0.35},
                "steps": [
                    {"range": [0, 30], "color": "#d1fae5"},
                    {"range": [30, 70], "color": "#fef3c7"},
                    {"range": [70, 100], "color": "#fee2e2"},
                ],
                "threshold": {
                    "line": {"width": 4},
                    "thickness": 0.75,
                    "value": value,
                },
            },
        )
    )

    fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20))
    return fig



def normalize_patterns(patterns: Any) -> pd.DataFrame:
    if not patterns:
        return pd.DataFrame()

    if isinstance(patterns, list):
        if patterns and isinstance(patterns[0], dict):
            return pd.DataFrame(patterns)
        return pd.DataFrame({"pattern": patterns})

    return pd.DataFrame()



def normalize_feature_importance(items: Any) -> pd.DataFrame:
    if not items:
        return pd.DataFrame()

    if isinstance(items, list):
        return pd.DataFrame(items)

    if isinstance(items, dict):
        return pd.DataFrame(
            [{"feature": k, "importance": v} for k, v in items.items()]
        )

    return pd.DataFrame()



def render_sidebar() -> None:
    st.sidebar.title("🛡️ Wallet Risk Intelligence")
    st.sidebar.markdown("Production-style Web3 fraud detection dashboard.")

    health = check_health()
    if health.get("ok"):
        st.sidebar.success("Backend Online")
    else:
        st.sidebar.error("Backend Offline")
        if health.get("error"):
            st.sidebar.caption(health["error"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Example Wallet")
    st.sidebar.code("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")


# Main UI

def main() -> None:
    render_sidebar()

    st.title("🛡️ Wallet Risk Intelligence API")
    st.caption(
        "Real-time blockchain wallet risk scoring using ML, RAG, and LLM explanations."
    )

    with st.container(border=True):
        wallet_address = st.text_input(
            "Wallet Address",
            placeholder="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            analyze_clicked = st.button("Analyze", use_container_width=True)
        with col2:
            st.info(
                "Enter an Ethereum wallet address to compute risk score and AI explanation."
            )

    if analyze_clicked:
        if not wallet_address:
            st.warning("Please enter a wallet address.")
            st.stop()

        if not validate_wallet(wallet_address):
            st.error("Invalid Ethereum wallet address.")
            st.stop()

        with st.spinner("Analyzing wallet..."):
            try:
                result = analyze_wallet(wallet_address)
            except requests.HTTPError as e:
                st.error(f"API Error: {e}")
                try:
                    st.json(e.response.json())
                except Exception:
                    st.text(e.response.text)
                st.stop()
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.stop()

        render_results(result)


# Results Rendering

def render_results(result: Dict[str, Any]) -> None:
    data = result.get("data", {})

    risk_score = float(data.get("risk_score", 0.0))
    risk_level = data.get("risk_level", "UNKNOWN")
    confidence = float(data.get("confidence", 0.0))
    activity_status = data.get("activity_status", "ACTIVE")
    explanation = data.get("explanation", "No explanation available.")

    # Overview
    st.markdown("## Risk Overview")

    left, right = st.columns([2, 3])

    with left:
        st.plotly_chart(create_gauge(risk_score), use_container_width=True)

    with right:
        render_risk_badge(risk_level)
        st.write("")

        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Score", f"{risk_score:.2%}")
        c2.metric("Confidence", f"{confidence:.2%}")
        c3.metric("Activity", activity_status)

        if data.get("timestamp"):
            st.caption(f"Generated at: {result['timestamp']}")
        else:
            st.caption(f"Generated at: {datetime.utcnow().isoformat()}Z")

    # Explanation
    st.markdown("## AI Explanation")
    st.info(explanation)

    # Patterns
    patterns_df = normalize_patterns(data.get("patterns_matched"))
    if not patterns_df.empty:
        st.markdown("## Detected Risk Patterns")

        if "pattern" in patterns_df.columns:
            chips_html = "".join(
                f'<span class="pattern-chip">{p}</span>'
                for p in patterns_df["pattern"].astype(str).tolist()
            )
            st.markdown(chips_html, unsafe_allow_html=True)

        st.dataframe(patterns_df, use_container_width=True)

    # Top Features
    top_features = data.get("top_features", {})
    if top_features:
        st.markdown("## Top Feature Values")
        feature_df = pd.DataFrame(
            [{"feature": k, "value": v} for k, v in top_features.items()]
        )
        st.dataframe(feature_df, use_container_width=True)

    # Feature Importance
    importance_df = normalize_feature_importance(
        data.get("feature_importance")
    )
    if not importance_df.empty and {"feature", "importance"}.issubset(
        importance_df.columns
    ):
        st.markdown("## Feature Importance")
        importance_df = importance_df.sort_values(
            "importance", ascending=False
        ).head(15)
        st.bar_chart(
            importance_df.set_index("feature")["importance"],
            use_container_width=True,
        )

    # Raw JSON
    with st.expander("Raw API Response"):
        st.json(result)


if __name__ == "__main__":
    main()