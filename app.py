"""Kate demo: three stories. Run: streamlit run app.py

Wiring only: keep logic in kate/ and screens in ui/ so people don't collide in this file.
"""
from datetime import date, timedelta

import streamlit as st

if tuple(int(p) for p in st.__version__.split(".")[:2]) < (1, 50):
    st.error(f"Streamlit {st.__version__} is too old for this app. Run it from the project environment:  \n"
             "`.venv\\Scripts\\python.exe -m streamlit run app.py`")
    st.stop()

from kate import avg_belgian, avg_student, data  # noqa: E402
from kate.events import MOVING  # noqa: E402
from ui import bank, care, phone, theme, trip  # noqa: E402

st.set_page_config(page_title="Kate Life Events", page_icon="🏠", layout="wide")
theme.apply()

STORIES = ["1 · Moving house", "2 · Are we covered for this trip?", "3 · Financial Care"]


@st.cache_data
def load():
    return data.load_personas(), data.load_transactions(), avg_belgian.load(), avg_student.load()


personas, transactions, (sofie, sofie_txs), (arne, arne_txs) = load()

with st.sidebar:
    st.header("Demo controls")
    story = st.radio("Story", STORIES)
    if story == STORIES[0]:
        profile = st.selectbox("Customer", personas, format_func=lambda p: p["name"])
        today = st.slider("Today is", data.START + timedelta(days=60), data.END, data.END, format="D MMM")
        language = st.selectbox("Kate speaks", ["English", "Nederlands", "Français"])
    elif story == STORIES[2]:
        today = st.slider("Today is", date(2026, 7, 31), avg_student.END, avg_student.END, format="D MMM")
    if st.button("Restart demo", width="stretch"):
        st.session_state.clear()
        st.rerun()

left, right = st.columns([2, 3], gap="large")

if story == STORIES[1]:
    with left:
        trip.render(sofie, sofie_txs, avg_belgian.END)
    with right:
        trip.render_bank(sofie, sofie_txs, avg_belgian.END)
elif story == STORIES[2]:
    with left:
        care.render(arne, arne_txs, today)
    with right:
        care.render_bank(arne, arne_txs, today)
else:
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
    with left:
        phone.render(profile, visible, detection, actions, language)
    with right:
        bank.render(profile, detection, actions, portfolio)
