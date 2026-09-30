"""Story 2: Sofie asks Kate by voice "are we covered for this trip?".  OWNER: frontend (customer)"""
import hashlib
from html import escape

import pandas as pd
import streamlit as st

import services
from kate import coverage
from ui.common import kate_reply, phone_bar, say, voice_available
from ui.theme import euro

QUESTION = "We're going to Normandy in the autumn holiday with the car. Are we covered?"


def _system(profile: dict, trip: dict, checks: list) -> str:
    lines = "\n".join(f"- {c.risk}: {'COVERED by ' + c.by if c.covered else 'NOT covered (' + c.by + ')'}"
                      + (f"; fix: {c.fix}" + (f", €{c.fix_premium:.0f}/year" if c.fix_premium else "")
                         if not c.covered and c.fix else "")
                      for c in checks)
    return f"""You are Kate, KBC's digital assistant, answering out loud in the KBC Mobile app.
Customer: {profile['name']}, {profile['segment']}. Tone: {profile['tone']}
Upcoming trip (seen in her payments): {trip['destination']}, {trip['from']} to {trip['to']},
booked with {trip['booked_with']} for €{trip['cost']:.0f}.
Cover check against her KBC products:
{lines}

Rules: answer in at most 60 words, spoken style, no lists or markdown. Say first what is covered,
then the gaps, then offer to fix the gaps in one tap. Only use the facts above; never invent cover."""


def _fallback(checks: list) -> str:
    ok = [c.risk.lower() for c in checks if c.covered]
    missing = [c.risk.lower() for c in coverage.gaps(checks)]
    return (f"Good news: {' and '.join(ok)} are covered. But {', '.join(missing)} are not. "
            "I can fix that in one tap, before you leave.")


def render(profile: dict, txs: pd.DataFrame, today):
    s = st.session_state.setdefault("trip", {"question": None, "answer": None, "fixed": False, "audio": None})
    trip = coverage.find_trip(txs, today)
    with st.container(key="phone"):
        phone_bar(profile["first_name"])
        balance = profile["start_balance"] + txs[txs["date"] <= pd.Timestamp(today)]["amount"].sum()
        st.markdown(f'<div class="balance"><small>{escape(profile["products"][0]["name"])}</small><br>'
                    f"<b>{euro(balance, 2)}</b></div>", unsafe_allow_html=True)
        if not trip:
            st.caption("No upcoming trip in the payments yet.")
            return
        checks = coverage.check(profile, txs, trip)

        question = None
        if voice_available():
            audio = st.audio_input("Talk to Kate", key="trip_mic")
            if audio is not None:
                digest = hashlib.md5(audio.getvalue()).hexdigest()
                if digest != s["audio"]:
                    s["audio"] = digest
                    try:
                        with st.spinner("Listening..."):
                            question = services.transcribe(audio.getvalue())
                    except Exception as e:
                        st.caption(f"Speech-to-text unavailable: {type(e).__name__}")
        if st.button(f'🎤 "{QUESTION}"', width="stretch"):
            question = QUESTION
        if typed := st.chat_input("Or type your question", key="trip_input"):
            question = typed
        if question:
            s.update(question=question, fixed=False)
            s["answer"] = kate_reply([{"role": "user", "content": question}], _system(profile, trip, checks),
                                     _fallback(checks))
            st.session_state.pop("spoken_trip", None)
            st.rerun()

        if s["question"]:
            st.chat_message("user", avatar="🙂").write(s["question"])
            say(s["answer"], "trip")
            rows = "".join(
                f"<div class='tx'><div>{'✅' if c.covered else '⚠️'} {escape(c.risk)}"
                f"<small>{escape(c.by)}</small></div></div>" for c in checks)
            st.markdown(f"**Your cover for {escape(trip['destination'])}, {trip['from']} – {trip['to']}**" + rows,
                        unsafe_allow_html=True)
            fixes = [c for c in coverage.gaps(checks) if c.fix_premium]
            premium = sum(c.fix_premium for c in fixes)
            if s["fixed"]:
                st.markdown(f'<div class="done"><b>Covered, {escape(profile["first_name"])}</b><br>'
                            + "<br>".join(f"✅ {escape(c.fix)}" for c in fixes)
                            + "<br>Certificates are in your KBC Mobile inbox.</div>", unsafe_allow_html=True)
            elif fixes and st.button(f"Fix it: {len(fixes)} covers · {euro(premium)} / year", type="primary",
                                     width="stretch"):
                s["fixed"] = True
                st.rerun()


def render_bank(profile: dict, txs: pd.DataFrame, today):
    st.subheader("Kate Trip Cover · bank view")
    st.markdown(f"**{profile['name']}** · {profile['segment']}")
    trip = coverage.find_trip(txs, today)
    if not trip:
        st.info("No upcoming trip detected.")
        return
    checks = coverage.check(profile, txs, trip)
    gaps = coverage.gaps(checks)
    m1, m2, m3 = st.columns(3)
    m1.metric("Trip detected", f"{trip['destination']} {trip['from']}")
    m2.metric("Cover gaps", f"{len(gaps)} of {len(checks)}")
    m3.metric("Premium if fixed", euro(sum(c.fix_premium for c in gaps)) + " / yr")
    st.caption(f"Signal: {trip['booked_with']} payment of {euro(trip['cost'])} on {trip['booked_on']:%d %b}. "
               "Checked against her products without her having to ask first.")
    st.dataframe(pd.DataFrame([{"Risk": c.risk, "Covered": "✅" if c.covered else "⚠️", "By": c.by,
                                "Fix": c.fix or "", "€ / yr": euro(c.fix_premium) if c.fix_premium else ""}
                               for c in checks]),
                 hide_index=True, width="stretch")
    st.caption("Cover rules and premiums are illustrative, not KBC policy terms.")
