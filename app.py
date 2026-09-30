"""Kate Life Events demo. Run: streamlit run app.py

Wiring only: keep logic in kate/ and screens in ui/ so people don't collide in this file.
"""
from datetime import timedelta

import streamlit as st

from kate import data
from kate.events import MOVING
from ui import bank, phone, theme

st.set_page_config(page_title="Kate Life Events", page_icon="🏠", layout="wide")
theme.apply()


@st.cache_data
def load():
    return data.load_personas(), data.load_transactions()


personas, transactions = load()

with st.sidebar:
    st.header("Demo controls")
    profile = st.selectbox("Customer", personas, format_func=lambda p: p["name"])
    today = st.slider("Today is", data.START + timedelta(days=60), data.END, data.END, format="D MMM")
    language = st.selectbox("Kate speaks", ["English", "Nederlands", "Français"])
    if st.button("Restart demo", width="stretch"):
        st.session_state.clear()
        st.rerun()


def detect(persona_id: str):
    return MOVING.detect(transactions[transactions["persona_id"] == persona_id], today)


detection = detect(profile["id"])
actions = MOVING.actions(profile, detection) if detection.triggered else []
visible = transactions[(transactions["persona_id"] == profile["id"]) & (transactions["date"].dt.date <= today)]
portfolio = [
    {"Customer": p["name"], "Confidence": f"{d.score:.0%}", "Status": d.status, "Signals": len(d.fired)}
    for p in personas
    for d in [detect(p["id"])]
]

left, right = st.columns([2, 3], gap="large")
with left:
    phone.render(profile, visible, detection, actions, language)
with right:
    bank.render(profile, detection, actions, portfolio)
