"""Internal bank view: detection score, signals, business impact, plug-ins.  OWNER: frontend (bank)"""
import pandas as pd
import streamlit as st

from kate import impact
from kate.events import REGISTRY
from ui.theme import BLUE, NAVY, euro

STATUS_COLOR = {"triggered": "#1E8E3E", "watching": "#E8A100", "quiet": "#6B7C8F"}


def _badge(text: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}">{text}</span>'


def _assumptions() -> dict:
    return {key: st.session_state.get(f"a_{key}", default) for key, default in impact.DEFAULTS.items()}


def render(profile: dict, detection, actions: list, portfolio: list[dict]):
    st.subheader("Kate Life Events · bank view")
    st.markdown(
        f"**{profile['name']}** · {profile['segment']} &nbsp; "
        + _badge(detection.status.upper(), STATUS_COLOR[detection.status]),
        unsafe_allow_html=True,
    )
    result = impact.compute(_assumptions())
    live_signals = [s for s in detection.event.signals if s.match]
    m1, m2, m3 = st.columns(3)
    m1.metric("Confidence: " + detection.event.name.lower(), f"{detection.score:.0%}")
    m2.metric("Signals fired", f"{len(detection.fired)} / {len(live_signals)}")
    m3.metric("Premium protected or won per 10k customers", euro(result["premium"]) + " / yr")

    tab_detect, tab_impact, tab_plugins = st.tabs(["Detection", "Business impact", "Plug-ins"])

    with tab_detect:
        st.progress(detection.score, text=f"Confidence {detection.score:.0%} · Kate speaks up at 70%")
        fired = {f.signal.id: f for f in detection.fired}
        rows = []
        for signal in live_signals:
            hit = fired.get(signal.id)
            first = hit.evidence[0] if hit else None
            rows.append({
                "Signal": signal.label,
                "Fired": "✅" if hit else "",
                "Weight": signal.weight,
                "Evidence": f"{first['counterparty']}: {first['description']}" if first else "",
                "Date": f"{first['date']:%d %b}" if first else "",
                "Amount": euro(sum(r["amount"] for r in hit.evidence), 2) if hit else "",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        if detection.triggered:
            premium = sum(a.annual_premium for a in actions)
            st.caption(f"Inferred: {detection.facts['kind']} · new address {detection.facts['new_address']} · "
                       f"{len(actions)} actions prepared · {euro(premium)} annual premium at stake for this customer")
        st.markdown("**All customers on the same rules**")
        st.dataframe(pd.DataFrame(portfolio), hide_index=True, width="stretch")
        live = st.session_state.get("llm_live")
        if live is not None:
            st.caption("Kate's messages: live LLM" if live else "Kate's messages: scripted fallback (no LLM reachable)")

    with tab_impact:
        left, right = st.columns([2, 3])
        with left:
            st.caption("Assumptions (illustrative, adjust live)")
            for key, (label, default, low, high, step) in impact.ASSUMPTIONS.items():
                st.slider(label, low, high, default, step, key=f"a_{key}")
            base = st.number_input("KBC retail customer base", value=3_000_000, step=100_000)
        with right:
            result = impact.compute(_assumptions())
            st.metric("Annual premium protected or won per 10k customers", euro(result["premium"]))
            c1, c2 = st.columns(2)
            c1.metric("Movers detected", f"{result['detected']:.0f}")
            c2.metric("Un- or underinsured movers caught", f"{result['underinsured_caught']:.0f}")
            c1.metric("Policies retained", f"{result['retained']:.0f}")
            c2.metric("New policies won", f"{result['won']:.0f}")
            c1.metric("Customer admin hours saved", f"{result['hours_saved']:.0f}")
            c2.metric(f"At {base / 1e6:.1f}M customers", euro(result["premium"] * base / 10_000) + " / yr")

    with tab_plugins:
        st.caption("Every life event is a plug-in with the same interface: signals → confidence → actions.")
        for column, event in zip(st.columns(len(REGISTRY)), REGISTRY):
            with column.container(border=True):
                badge = _badge("LIVE", BLUE) if event.live else _badge("PLANNED", NAVY)
                st.markdown(f"### {event.icon}\n**{event.name}** {badge}", unsafe_allow_html=True)
                st.caption("Signals")
                st.markdown("\n".join(f"- {s.label}" for s in event.signals[:4]))
                st.caption("Actions")
                examples = event.example_actions or [a.title.split(" to ")[0] for a in actions[:3]]
                st.markdown("\n".join(f"- {a}" for a in examples))
