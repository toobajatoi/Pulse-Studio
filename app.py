"""Pulse — visual Design Companion."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from llm import run_job

DATA_PATH = Path(__file__).parent / "data" / "usability_feedback.csv"

st.set_page_config(page_title="Pulse", page_icon="✦", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
      html, body, [class*="css"] { font-family: Inter, sans-serif; }
      .stApp {
        background:
          radial-gradient(800px 360px at 10% 0%, #d8f3ee, transparent 55%),
          radial-gradient(720px 320px at 92% 8%, #d7e8ff, transparent 50%),
          #fff;
      }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stToolbar"], .stAppDeployButton { display: none !important; }
      h1 { letter-spacing: -0.04em; }
      .stButton>button { background:#111; color:#fff; border:0; border-radius:999px; font-weight:600; height:42px; }
      .card { background:#fff; border:1px solid #ececec; border-radius:20px; padding:16px 16px 14px; height:100%; }
      .card h3 { margin:8px 0 6px; font-size:18px; letter-spacing:-0.03em; }
      .card p { margin:0; color:#444; font-size:13px; line-height:1.4; }
      .pill { display:inline-block; background:#111; color:#fff; border-radius:999px; font-size:11px; font-weight:700; padding:3px 8px; margin-right:6px; }
      .pill.soft { background:#f1f1f3; color:#111; }
      .phone { width:280px; margin:0 auto; background:#111; border-radius:32px; padding:12px 12px 18px; }
      .phone-screen { background:#fff; border-radius:22px; min-height:360px; padding:22px 18px; display:flex; flex-direction:column; gap:10px; }
      .phone h2 { margin:0; font-size:26px; letter-spacing:-0.04em; }
      .phone .help { color:#666; font-size:14px; }
      .cta { background:#111; color:#fff; border-radius:999px; text-align:center; padding:12px; font-weight:700; margin-top:auto; }
      .ghost { background:#f4f4f5; border-radius:12px; padding:10px 12px; font-size:13px; color:#333; }
      .wire { background:#f6f6f7; border-radius:16px; padding:10px; }
      .row { background:#fff; border:1px solid #e8e8e8; border-radius:12px; padding:10px 12px; margin:6px 0; font-size:13px; }
      .row.last { background:#111; color:#fff; border-color:#111; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_notes() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def groq_from_secrets() -> str:
    try:
        return str(st.secrets.get("GROQ_API_KEY", "") or "")
    except Exception:
        return ""


def render_summary(data: dict) -> None:
    themes = data.get("themes") or []
    cols = st.columns(max(len(themes), 1))
    for col, theme in zip(cols, themes):
        with col:
            st.markdown(
                f"""
                <div class="card">
                  <span class="pill">{(theme.get('severity') or 'high').upper()}</span>
                  <span class="pill soft">{theme.get('count', 0)} notes</span>
                  <h3>{theme.get('name', '')}</h3>
                  <p>“{theme.get('quote', '')}”</p>
                  <p style="margin-top:10px"><b>{theme.get('fix', '')}</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    wins = data.get("wins") or []
    if wins:
        st.write("")
        chips = " ".join(f'<span class="pill soft">{w.get("change","")}</span>' for w in wins[:3])
        st.markdown(chips, unsafe_allow_html=True)


def render_copy(data: dict) -> None:
    st.markdown(
        f"""
        <div class="phone">
          <div class="phone-screen">
            <h2>{data.get('headline', '')}</h2>
            <div class="help">{data.get('helper', '')}</div>
            <div class="ghost">{data.get('empty', '')}</div>
            <div class="ghost">{data.get('error', '')}</div>
            <div class="cta">{data.get('cta', '')}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_layouts(data: dict) -> None:
    layouts = data.get("layouts") or []
    cols = st.columns(max(len(layouts), 1))
    for col, layout in zip(cols, layouts):
        rows = layout.get("structure") or []
        blocks = "".join(
            f'<div class="row{" last" if i == len(rows) - 1 else ""}">{step}</div>'
            for i, step in enumerate(rows[:4])
        )
        with col:
            st.markdown(
                f"""
                <div class="card">
                  <span class="pill">Layout</span>
                  <h3>{layout.get('name', '')}</h3>
                  <div class="wire">{blocks}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main() -> None:
    df = load_notes()
    groq_key = groq_from_secrets()

    st.title("Pulse")
    f1, f2 = st.columns(2)
    city = f1.selectbox("City", ["All"] + sorted(df["city"].unique().tolist()))
    screen = f2.selectbox("Screen", ["All"] + sorted(df["screen"].unique().tolist()))

    view = df.copy()
    if city != "All":
        view = view[view["city"] == city]
    if screen != "All":
        view = view[view["screen"] == screen]
    rows = view.to_dict("records")
    if not rows:
        st.info("No notes.")
        return

    m1, m2, m3 = st.columns(3)
    for col, label, value in (
        (m1, "Notes", len(view)),
        (m2, "Failed", int((view["success"] == "fail").sum())),
        (m3, "Cities", view["city"].nunique()),
    ):
        col.markdown(
            f'<div class="card"><p>{label}</p><h3 style="font-size:32px;margin:0">{value}</h3></div>',
            unsafe_allow_html=True,
        )

    target = screen if screen != "All" else "Ride"
    filt = f"{city}|{screen}|{target}"
    if st.session_state.get("filt") != filt:
        st.session_state.filt = filt
        for key in ("summary", "copy", "layouts"):
            st.session_state.pop(key, None)

    if not groq_key:
        groq_key = st.text_input("Groq key", type="password")

    tab_sum, tab_copy, tab_lay = st.tabs(["Feedback", "Copy", "Layouts"])

    with tab_sum:
        if st.button("Refresh", key="sum_btn") or "summary" not in st.session_state:
            with st.spinner(" "):
                data, src = run_job("summary", rows, groq_key)
            st.session_state.summary = data
        render_summary(st.session_state.summary)

    with tab_copy:
        language = st.radio("Lang", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
        if st.button("Refresh", key="copy_btn") or "copy" not in st.session_state:
            with st.spinner(" "):
                data, src = run_job("copy", rows, groq_key, language=language, screen=target)
            st.session_state.copy = data
        render_copy(st.session_state.copy)

    with tab_lay:
        if st.button("Refresh", key="lay_btn") or "layouts" not in st.session_state:
            with st.spinner(" "):
                data, src = run_job("layouts", rows, groq_key, screen=target)
            st.session_state.layouts = data
        render_layouts(st.session_state.layouts)


if __name__ == "__main__":
    main()
