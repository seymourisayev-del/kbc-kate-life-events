"""KBC hackathon dashboard skeleton. Run: streamlit run app.py"""
import pandas as pd
import streamlit as st

import services

KBC_NAVY = "#003665"
KBC_BLUE = "#00AEEF"

st.set_page_config(page_title="KBC | TODO product name", page_icon="🏦", layout="wide")

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 1.5rem; }}
      .kbc-header {{
        background: {KBC_NAVY}; color: white; padding: 1rem 1.5rem;
        border-radius: 12px; border-bottom: 4px solid {KBC_BLUE}; margin-bottom: 1.25rem;
      }}
      .kbc-header h1 {{ color: white; font-size: 1.6rem; margin: 0; padding: 0; }}
      .kbc-header p {{ color: #CFE9F7; margin: 0.25rem 0 0 0; }}
      [data-testid="stMetric"] {{
        background: #F2F6FA; border-left: 4px solid {KBC_BLUE};
        padding: 0.75rem 1rem; border-radius: 8px;
      }}
      [data-testid="stSidebar"] {{ background: {KBC_NAVY}; }}
      [data-testid="stSidebar"] * {{ color: white; }}
    </style>
    <div class="kbc-header">
      <h1>TODO product name</h1>
      <p>TODO one-line promise for the named user</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("TODO user name")
    st.caption("TODO role")
    st.divider()
    st.selectbox("TODO selector", ["—"])

# The one hard number goes in the first tile.
k1, k2, k3, k4 = st.columns(4)
k1.metric("TODO € / hours saved", "—")
k2.metric("TODO", "—")
k3.metric("TODO", "—")
k4.metric("TODO", "—")

left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("TODO main table")
    st.dataframe(pd.DataFrame(), width="stretch")
    st.subheader("TODO chart / explanation")
    st.empty()

with right:
    st.subheader("AI assistant")
    prompt = st.text_area("Ask", placeholder="TODO default prompt", label_visibility="collapsed")
    generate, read_aloud = st.columns(2)
    if generate.button("Generate", type="primary", width="stretch") and prompt:
        with st.spinner("Thinking..."):
            st.session_state["answer"] = services.ask_llm(prompt)
    if answer := st.session_state.get("answer"):
        st.markdown(answer)
        if read_aloud.button("Read aloud", width="stretch"):
            with st.spinner("Generating voice..."):
                st.audio(services.speak(answer), format="audio/mpeg", autoplay=True)
