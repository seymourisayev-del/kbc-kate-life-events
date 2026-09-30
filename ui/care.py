"""Story 3: Financial Care for Arne, with three autonomy modes.  OWNER: frontend (customer)"""
from html import escape

import pandas as pd
import streamlit as st

from kate import care
from ui.common import kate_reply, phone_bar, say
from ui.theme import euro


def _state() -> dict:
    return st.session_state.setdefault("care", {"mode": None, "msgs": {}, "accepted": [], "undone": []})


def _kate_message(profile, assessment, s) -> tuple[str, str]:
    """Kate's message for the current mode and health state, generated once and cached."""
    key = f"care_{s['mode']}_{assessment['health']}"
    if key not in s["msgs"]:
        if s["mode"] is None:
            note = "[app] Strain detected. Open with your Stage 1 prompt; the app shows the three options as buttons."
        else:
            note = (f"[app] The customer tapped option {s['mode']}. Confirm what you will do now in this mode, "
                    f"given the financial health index '{assessment['health']}'.")
        s["msgs"][key] = kate_reply([{"role": "user", "content": note}],
                                    care.system_prompt(profile, assessment, s["mode"]),
                                    care.fallback(profile, assessment, s["mode"]))
    return key, s["msgs"][key]


def render(profile: dict, txs: pd.DataFrame, today):
    s = _state()
    a = care.assess(profile, txs, today)
    with st.container(key="phone"):
        phone_bar(profile["first_name"])
        st.markdown(f'<div class="balance"><small>{escape(profile["products"][0]["name"])}</small><br>'
                    f"<b>{euro(a['balance'], 2)}</b></div>", unsafe_allow_html=True)

        if s["mode"] is None:
            if not a["strained"]:
                st.caption("Nothing to flag. Kate stays quiet.")
                return
            key, text = _kate_message(profile, a, s)
            say(text, key, speak=False)  # the video narration covers this story
            for mode, label in care.MODES.items():
                if st.button(label, key=f"mode_{mode}", width="stretch", type="primary" if mode == 2 else "secondary"):
                    s["mode"] = mode
                    st.rerun()
            return

        st.chat_message("user", avatar=":material/person:").write(care.MODES[s["mode"]])
        key, text = _kate_message(profile, a, s)
        say(text, key, speak=False)  # the video narration covers this story

        if s["mode"] == 1:
            st.caption("Proactive tips are off. Kate only answers when Arne asks her something.")
        elif s["mode"] == 2:
            total = 0.0
            for card in care.copilot_cards(profile, a):
                done = card.id in s["accepted"]
                with st.container(border=True):
                    st.markdown(f"**{card.title}**  \n{card.detail}  \nSaves about {euro(card.monthly)} a month")
                    if done:
                        st.caption("✅ Done")
                        total += card.monthly
                    elif st.button("Do it", key=f"accept_{card.id}", width="stretch"):
                        s["accepted"].append(card.id)
                        st.rerun()
            st.markdown(f"**Saved with your OK: {euro(total)} / month**")
        else:
            color = "#1E8E3E" if a["health"] == "Financial freedom" else "#E8A100"
            st.markdown(f'Financial health: <span class="badge" style="background:{color}">{a["health"]}</span>',
                        unsafe_allow_html=True)
            actions = care.autopilot_actions(profile, a)
            if not actions:
                st.caption("Cash flow is healthy, so Kate has no rules running.")
            total = 0.0
            for action in actions:
                undone = action.id in s["undone"]
                with st.container(border=True):
                    st.markdown(f"**{action.title}**  \n{action.detail}")
                    if undone:
                        st.caption("Undone")
                    else:
                        total += action.monthly
                        if st.button("Undo", key=f"undo_{action.id}"):
                            s["undone"].append(action.id)
                            st.rerun()
            if actions:
                st.markdown(f"**Freed up this month: {euro(total)}, and rent is paid first**")
        if st.button("Change how Kate helps", width="stretch"):
            s.update(mode=None, accepted=[], undone=[])
            st.rerun()


def render_bank(profile: dict, txs: pd.DataFrame, today):
    s = _state()
    a = care.assess(profile, txs, today)
    st.subheader("Kate Financial Care · bank view")
    st.markdown(f"**{profile['name']}** · {profile['segment']}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Balance", euro(a["balance"]))
    m2.metric("Margin after fixed costs", euro(a["margin"]))
    m3.metric("Health index", a["health"])
    st.markdown("**Strain signals**" + ("" if a["signals"] else ": none"))
    for signal in a["signals"]:
        st.markdown(f"- {signal}")
    st.caption(f"Strain = 2 or more signals → {'Kate reaches out' if a['strained'] else 'Kate stays quiet'}. "
               f"Late-night Uber Eats last 30 days: {a['late_delivery_count']} orders, "
               f"{euro(a['late_delivery_eur'])}.")
    mode = s["mode"]
    st.metric("Mode chosen by customer", f"{mode}: {care.MODES[mode]}" if mode else "not yet")
    last30 = a["last30"]
    by_cat = (-last30[last30["amount"] < 0].groupby("category")["amount"].sum()).sort_values(ascending=False)
    st.dataframe(by_cat.rename("€ last 30 days").round(0).to_frame(), width="stretch")
    st.caption("Venue prices, Kate Deals and gym usage are illustrative placeholders.")
