"""Helpers shared by the story screens.  OWNER: frontend (customer)"""
import os
from html import escape

import streamlit as st

import services


def phone_bar(first_name: str):
    st.markdown(f'<div class="phone-bar">KBC Mobile<small>Hello {escape(first_name)}</small></div>',
                unsafe_allow_html=True)


def kate_reply(messages: list[dict], system: str, fallback: str) -> str:
    """Live LLM reply, or the scripted fallback when no LLM is reachable."""
    try:
        with st.spinner("Kate is thinking..."):
            text = services.chat(messages, system).strip()
        st.session_state["llm_live"] = True
        return text
    except Exception:
        st.session_state["llm_live"] = False
        return fallback


def voice_available() -> bool:
    return bool(os.getenv("ELEVENLABS_API_KEY"))


def say(text: str, key: str, speak: bool = True):
    """Kate's bubble, plus a spoken version the first time when ElevenLabs is configured."""
    st.chat_message("assistant", avatar=":material/support_agent:").write(text)
    if speak and voice_available() and not st.session_state.get(f"spoken_{key}"):
        try:
            with st.spinner("Kate is speaking..."):
                st.audio(services.speak(text), format="audio/mpeg", autoplay=True)
            st.session_state[f"spoken_{key}"] = True
        except Exception as e:
            st.caption(f"Voice unavailable: {type(e).__name__}")
