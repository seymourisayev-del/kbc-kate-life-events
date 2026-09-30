"""Shared KBC look.  OWNER: whoever touches it, keep it small"""
import streamlit as st

NAVY = "#003665"
BLUE = "#00AEEF"

CSS = f"""
<style>
  .block-container {{ padding-top: 2.5rem; }}
  .st-key-phone {{
    max-width: 400px; margin: 0 auto; background: #fff;
    border: 10px solid #0B1F33; border-radius: 42px; padding: 0 14px 18px 14px;
    box-shadow: 0 18px 40px rgba(0, 54, 101, .25);
  }}
  .phone-bar {{
    background: {NAVY}; color: #fff; margin: 0 -14px 12px -14px; padding: 18px 20px 14px 20px;
    border-radius: 30px 30px 0 0; border-bottom: 4px solid {BLUE}; font-weight: 700; font-size: 1.05rem;
  }}
  .phone-bar small {{ display: block; font-weight: 400; color: #CFE9F7; }}
  .balance {{ background: #F2F6FA; border-radius: 14px; padding: 12px 16px; margin-bottom: 10px; }}
  .balance b {{ font-size: 1.5rem; color: {NAVY}; }}
  .st-key-katecard {{
    background: linear-gradient(135deg, {NAVY}, #005A9C); border-radius: 16px; padding: 14px 16px;
  }}
  .st-key-katecard p {{ color: #fff; }}
  .tx {{ display: flex; justify-content: space-between; gap: 8px; padding: 7px 0;
         border-bottom: 1px solid #E6ECF2; font-size: .85rem; }}
  .tx small {{ color: #6B7C8F; display: block; }}
  .tx .amt {{ white-space: nowrap; font-weight: 600; }}
  .tx.signal {{ border-left: 4px solid {BLUE}; padding-left: 8px; background: #F0FAFE; }}
  .done {{ background: #E8F7EE; border-radius: 14px; padding: 12px 16px; margin-bottom: 10px; }}
  [data-testid="stMetric"] {{
    background: #F2F6FA; border-left: 4px solid {BLUE}; padding: .6rem .9rem; border-radius: 8px;
  }}
  .badge {{ padding: 2px 10px; border-radius: 999px; font-size: .75rem; font-weight: 600; color: #fff; }}
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def euro(value: float, decimals: int = 0) -> str:
    return f"€ {value:,.{decimals}f}".replace(",", " ")
