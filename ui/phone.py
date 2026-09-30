"""Customer view: KBC Mobile phone screen.  OWNER: frontend (customer)

Flow: home (timeline + Kate card) -> kate (chat, confirm, checklist) -> done.
"""
import os
import re
from html import escape

import streamlit as st

import services
from kate import persona
from ui.theme import euro

YES = re.compile(r"^\s*(yes|yep|yeah|ja|oui|correct|indeed|klopt)\b", re.I)


def _state(pid: str) -> dict:
    return st.session_state.setdefault(
        f"phone_{pid}", {"screen": "home", "chat": [], "confirmed": False, "approved": []}
    )


def _kate_says(state: dict, system: str, fallback: str):
    """Append Kate's next message: live LLM if available, scripted fallback otherwise."""
    try:
        with st.spinner("Kate is typing..."):
            text = services.chat(state["chat"], system).strip()
        st.session_state["llm_live"] = True
    except Exception:
        text = fallback
        st.session_state["llm_live"] = False
    state["chat"].append({"role": "assistant", "content": text})


def _app_note(state: dict, note: str):
    state["chat"].append({"role": "user", "content": f"[app] {note}", "hidden": True})


def _home(state, profile, txs, detection, system):
    balance = profile["start_balance"] + txs["amount"].sum()
    st.markdown(
        f'<div class="balance"><small>{escape(profile["products"][0]["name"])}</small><br>'
        f"<b>{euro(balance, 2)}</b></div>",
        unsafe_allow_html=True,
    )
    if detection.triggered:
        with st.container(key="katecard"):
            st.markdown(f"**{detection.event.icon} Kate noticed something**  \nIt looks like you are moving. "
                        "Shall I take care of the admin?")
            if st.button("Talk to Kate", type="primary", width="stretch"):
                state["screen"] = "kate"
                if not state["chat"]:
                    _app_note(state, "The customer opened your card. Start the conversation.")
                    _kate_says(state, system, persona.opening(profile, detection))
                st.rerun()

    signal_rows = (
        {(row["date"], row["counterparty"]) for f in detection.fired for row in f.evidence}
        if detection.triggered else set()
    )
    rows = []
    for tx in txs.sort_values("date", ascending=False).head(14).to_dict("records"):
        css = "tx signal" if (tx["date"], tx["counterparty"]) in signal_rows else "tx"
        rows.append(
            f'<div class="{css}"><div>{escape(tx["counterparty"])}'
            f'<small>{tx["date"]:%d %b} · {escape(tx["description"])}</small></div>'
            f'<div class="amt">{euro(tx["amount"], 2)}</div></div>'
        )
    st.markdown("**Recent transactions**" + "".join(rows), unsafe_allow_html=True)


def _kate(state, profile, detection, actions, system):
    pid = profile["id"]
    if st.button("‹ Back"):
        state["screen"] = "home"
        st.rerun()
    for message in state["chat"]:
        if not message.get("hidden"):
            avatar = ":material/support_agent:" if message["role"] == "assistant" else ":material/person:"
            st.chat_message(message["role"], avatar=avatar).write(message["content"])

    def confirm(text: str):
        state["chat"].append({"role": "user", "content": text})
        state["confirmed"] = True
        _app_note(state, "The customer confirmed. Congratulate them and point to the checklist below.")
        _kate_says(state, system, persona.confirmed(profile, actions))

    if not state["confirmed"]:
        yes, no = st.columns(2)
        if yes.button("Yes, I'm moving", type="primary", width="stretch"):
            confirm("Yes, that's right, I'm moving.")
            st.rerun()
        if no.button("No, not moving", width="stretch"):
            state["chat"].append({"role": "user", "content": "No, I'm not moving."})
            _kate_says(state, system, persona.not_moving(profile))
            st.rerun()
    else:
        st.markdown("**Your moving checklist**")
        picked = [a for a in actions if st.checkbox(a.title, value=True, help=a.detail, key=f"{pid}_{a.id}")]
        if st.button(f"Approve {len(picked)} actions", type="primary", width="stretch", disabled=not picked):
            state["approved"] = picked
            state["screen"] = "done"
            _app_note(state, "The customer approved: " + "; ".join(a.title for a in picked)
                      + ". Confirm it is arranged in one short, warm closing message.")
            _kate_says(state, system, persona.done(profile, picked))
            st.rerun()

    if text := st.chat_input("Message Kate", key=f"input_{pid}"):
        if not state["confirmed"] and YES.match(text):
            confirm(text)
        else:
            state["chat"].append({"role": "user", "content": text})
            _kate_says(state, system, "Sorry, I can't answer that right now. You can use the buttons below.")
        st.rerun()


def _done(state, profile):
    approved = state["approved"]
    minutes = sum(a.minutes_saved for a in approved)
    items = "".join(f"<div>✅ {escape(a.title)}</div>" for a in approved)
    st.markdown(
        f'<div class="done"><b>All set, {escape(profile["first_name"])}</b><br>'
        f"{len(approved)} tasks done in one tap · about {minutes / 60:.1f} hours of admin saved</div>{items}",
        unsafe_allow_html=True,
    )
    closing = state["chat"][-1]["content"]
    st.chat_message("assistant", avatar=":material/support_agent:").write(closing)
    if os.getenv("ELEVENLABS_API_KEY") and st.button("🔊 Hear Kate", width="stretch"):
        try:
            with st.spinner("Generating voice..."):
                st.audio(services.speak(closing), format="audio/mpeg", autoplay=True)
        except Exception as e:
            st.caption(f"Voice unavailable: {type(e).__name__}")
    if st.button("Back to overview", width="stretch"):
        state["screen"] = "home"
        st.rerun()


def render(profile: dict, txs, detection, actions: list, language: str):
    state = _state(profile["id"])
    if not detection.triggered and state["screen"] != "home":
        state["screen"] = "home"
    system = persona.system_prompt(profile, detection, actions, language) if detection.fired else ""
    with st.container(key="phone", border=False):
        st.markdown(
            f'<div class="phone-bar">KBC Mobile<small>Hello {escape(profile["first_name"])}</small></div>',
            unsafe_allow_html=True,
        )
        if state["screen"] == "home":
            _home(state, profile, txs, detection, system)
        elif state["screen"] == "kate":
            _kate(state, profile, detection, actions, system)
        else:
            _done(state, profile)
