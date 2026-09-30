"""Financial Care: strain detection + three autonomy modes.  OWNER: kate

Behaviour spec: kate/prompts/financial_care.md. Venue prices, Kate Deals and gym usage are
illustrative placeholders (bank data only shows totals, not what was bought).
"""
import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from kate.persona import STYLE

SPEC = (Path(__file__).parent / "prompts" / "financial_care.md").read_text(encoding="utf-8")

DISCRETIONARY = {"Drinks & nightlife", "Food delivery", "Eating out", "Shopping"}
# Average draft pint price per venue (illustrative), and the cheapest one around the corner.
PINT_PRICE = {"Den Bittere Pint": 4.10, "Café Commerce": 3.90, "De Giraf": 3.60, "Café Belge": 3.20,
              "Café Entrepot": 3.00}
CHEAPEST_NEARBY = ("Café Entrepot", 3.00)
KATE_DEAL_CASHBACK = 0.10  # illustrative Kate Deal on Uber Eats orders

MODES = {
    1: "I don't want to save money right now",
    2: "I want to save money",
    3: "Do whatever you think is best for me",
}


@dataclass
class Card:
    id: str
    title: str
    detail: str
    monthly: float  # € per month saved or protected


def assess(profile: dict, txs: pd.DataFrame, today) -> dict:
    today = pd.Timestamp(today)
    txs = txs[txs["date"] <= today]
    last30 = txs[txs["date"] > today - pd.Timedelta(days=30)]
    income30 = last30.loc[last30["amount"] > 0, "amount"].sum()
    spend30 = -last30.loc[last30["amount"] < 0, "amount"].sum()
    discretionary30 = -last30.loc[last30["category"].isin(DISCRETIONARY), "amount"].sum()
    balance = profile["start_balance"] + txs["amount"].sum()
    # Fixed costs due before the next month: kot rent (if any) + subscriptions + gym
    fixed_rows = txs[txs["category"].isin({"Housing", "Subscriptions"}) | txs["subcategory"].eq("Gym")]
    upcoming_fixed = -fixed_rows[fixed_rows["date"] > today - pd.Timedelta(days=31)]["amount"].sum()
    margin = balance - upcoming_fixed
    late_delivery = last30[(last30["counterparty"] == "Uber Eats") & (last30["time"] < "05:00")]
    signals = []
    if income30 - spend30 < 0:
        signals.append(f"Spent €{spend30 - income30:,.0f} more than came in over the last 30 days")
    if discretionary30 > 0.4 * max(income30, 1):
        signals.append(f"Going out and delivery: €{discretionary30:,.0f}, {discretionary30 / max(income30, 1):.0%} "
                       "of income")
    if margin < 0:
        signals.append(f"€{-margin:,.0f} short for next month's rent and subscriptions")
    elif margin < 200:
        signals.append(f"Only €{margin:,.0f} left after rent and subscriptions")
    return {
        "balance": balance, "income30": income30, "spend30": spend30, "discretionary30": discretionary30,
        "upcoming_fixed": upcoming_fixed, "margin": margin, "signals": signals,
        "strained": len(signals) >= 2, "health": "Budget protection" if margin < 200 else "Financial freedom",
        "late_delivery_count": len(late_delivery), "late_delivery_eur": -late_delivery["amount"].sum(),
        "last30": last30,
    }


def copilot_cards(profile: dict, state: dict) -> list[Card]:
    last30 = state["last30"]
    cards = []
    bars = last30[last30["counterparty"].isin(PINT_PRICE)]
    pricey = bars[bars["counterparty"].map(PINT_PRICE) >= CHEAPEST_NEARBY[1] + 0.5]
    if len(pricey):
        pints = (-pricey["amount"] / pricey["counterparty"].map(PINT_PRICE)).sum()
        extra = (pricey["counterparty"].map(PINT_PRICE) - CHEAPEST_NEARBY[1]).mean()
        top = pricey["counterparty"].mode()[0]
        cards.append(Card("bar", f"A pint at {top} costs €{PINT_PRICE[top]:.2f}",
                          f"{CHEAPEST_NEARBY[0]}, two minutes away, pours the same for €{CHEAPEST_NEARBY[1]:.2f}. "
                          f"About {pints:.0f} pints last month.", pints * extra))
    gym = profile.get("gym_usage")
    if gym and gym["tier"] == "Premium" and gym["clubs_used"] <= 1 and gym["buddy_visits"] == 0:
        cards.append(Card("gym", "Basic-Fit Premium → Basic",
                          f"You train at one club and never bring a buddy, the two things Premium adds. "
                          f"Same gym for €{gym['basic_price']:.2f}.", gym["price"] - gym["basic_price"]))
    delivery = -last30.loc[last30["counterparty"] == "Uber Eats", "amount"].sum()
    if delivery:
        cards.append(Card("deal", f"Kate Deal: {KATE_DEAL_CASHBACK:.0%} back on Uber Eats",
                          f"You ordered for €{delivery:.0f} last month. Activate the deal and get it back in "
                          "Kate Coins.", delivery * KATE_DEAL_CASHBACK))
    return cards


def autopilot_actions(profile: dict, state: dict) -> list[Card]:
    if state["health"] == "Financial freedom":
        return []
    card_payments = state["last30"]
    card_payments = card_payments[(card_payments["amount"] < 0)
                                  & card_payments["payment_method"].isin({"Card", "Bancontact"})]
    roundups = sum(math.ceil(-a) + a for a in card_payments["amount"])
    actions = [
        Card("rent", "Rent and bills go first",
             f"Your €{state['upcoming_fixed']:.0f} of kot rent and subscriptions are reserved before anything else, "
             "because they are the payments you can't miss. Your weekend-job pay tops the pot up first.", 0),
        Card("roundup", "Round-ups to your buffer pot",
             f"Every card payment is rounded up to the next euro. That would have saved €{roundups:.2f} last month.",
             roundups),
    ]
    gym = profile.get("gym_usage")
    if gym and gym["tier"] == "Premium":
        actions.append(Card("gym", "Gym switched to Basic from next month",
                            f"You only use one club, so Premium's extras cost you "
                            f"€{gym['price'] - gym['basic_price']:.2f} a month for nothing.",
                            gym["price"] - gym["basic_price"]))
    actions.append(Card("cap", "Going-out budget: €35 a week",
                        "No blocking. I only ping you when you pass it, until your next pay comes in.", 0))
    return actions


def system_prompt(profile: dict, state: dict, mode: int | None) -> str:
    facts = "\n".join(f"- {s}" for s in state["signals"]) or "- No strain signals"
    chosen = f"The customer chose Mode {mode}: \"{MODES[mode]}\"." if mode else "No mode chosen yet."
    return f"""{SPEC}

# THIS CUSTOMER
{profile['name']}, {profile['age']}, {profile['segment']}. Tone: {profile['tone']}
Balance €{state['balance']:.0f}; income last 30 days €{state['income30']:.0f}; spend €{state['spend30']:.0f};
margin after upcoming fixed costs €{state['margin']:.0f}. Financial health index: {state['health']}.
Signals:
{facts}
{chosen}

# IN THIS APP
You are replying inside a chat bubble in KBC Mobile. The app already shows the cards and numbers,
so do not list them. Maximum 50 words, plain text, no markdown. Lines starting with [app] are
instructions from the app, not from the customer. {STYLE}"""


def fallback(profile: dict, state: dict, mode: int | None) -> str:
    name = profile["first_name"]
    if mode is None:
        return ("I noticed your monthly expenses have been a bit higher than usual lately. I can help keep your "
                "budget on track depending on how much guidance you want.")
    if mode == 1:
        return f"Got it, {name}. No tips, no nudges. I'll only answer when you ask me something."
    if mode == 2:
        return f"Nice, {name}. Here are a few easy wins from last month. Tap the ones you like, skip the rest."
    if state["health"] == "Financial freedom":
        return f"You're in good shape, {name}. No rules active: enjoy your week, I'll keep an eye on things."
    return (f"Things are a bit tight until your next pay, {name}, so I've set up a few safety rules. Each one is "
            "explained below and you can undo any of them.")
