"""Life-event engine: signals -> confidence -> actions.  OWNER: detection

Every life event is a plug-in with the same interface. Moving is live; the others are
declared (signals + actions listed) but not wired, to show how the engine scales.
"""
import re
from dataclasses import dataclass, field
from math import prod
from typing import Callable

import pandas as pd

WINDOW_DAYS = 90  # signals older than this no longer count
HISTORY_DAYS = 60  # a counterparty is only "new" if we had this much history before it
TRIGGER, WATCH = 0.70, 0.30

ADDRESS = re.compile(r"([A-Z][\w\-]+ \d+, \d{4} [A-Z]\w+)")


def _text(df: pd.DataFrame) -> pd.Series:
    return (df["counterparty"] + " " + df["description"]).str.lower()


def keyword(pattern: str, exclude: str | None = None, new_only: bool = False) -> Callable:
    """Outgoing payments whose text matches `pattern`; `new_only` keeps first-time counterparties."""

    def match(recent, full, window_start):
        hit = recent[_text(recent).str.contains(pattern, regex=True) & (recent["amount"] < 0)]
        if exclude:
            hit = hit[~_text(hit).str.contains(exclude, regex=True)]
        if new_only:
            first_seen = hit["counterparty"].map(full.groupby("counterparty")["date"].min())
            cutoff = max(window_start, full["date"].min() + pd.Timedelta(days=HISTORY_DAYS))
            hit = hit[first_seen >= cutoff]
        return hit

    return match


def spend_spike(pattern: str, min_total: float, days: int = 45) -> Callable:
    def match(recent, full, window_start):
        since = recent["date"].max() - pd.Timedelta(days=days) if len(recent) else window_start
        hit = recent[_text(recent).str.contains(pattern, regex=True) & (recent["date"] >= since)]
        return hit if -hit["amount"].sum() >= min_total else hit.iloc[0:0]

    return match


@dataclass
class Signal:
    id: str
    label: str
    weight: float  # P(event | this signal alone); combined with noisy-OR
    match: Callable | None = None


@dataclass
class Fired:
    signal: Signal
    evidence: list[dict]


@dataclass
class Action:
    id: str
    title: str
    detail: str
    kind: str  # insurance | bank | reminder
    annual_premium: float = 0  # KBC premium at stake (retained or new)
    minutes_saved: int = 20


@dataclass
class Detection:
    event: "LifeEvent"
    score: float
    fired: list[Fired]
    facts: dict = field(default_factory=dict)

    @property
    def status(self) -> str:
        return "triggered" if self.score >= TRIGGER else "watching" if self.score >= WATCH else "quiet"

    @property
    def triggered(self) -> bool:
        return self.score >= TRIGGER


@dataclass
class LifeEvent:
    id: str
    name: str
    icon: str
    signals: list[Signal]
    live: bool = True
    example_actions: list[str] = field(default_factory=list)

    def detect(self, txs: pd.DataFrame, today) -> Detection:
        today = pd.Timestamp(today)
        full = txs[txs["date"] <= today]
        window_start = today - pd.Timedelta(days=WINDOW_DAYS)
        recent = full[full["date"] >= window_start]
        fired = []
        for signal in self.signals:
            rows = signal.match(recent, full, window_start) if signal.match and len(recent) else []
            if len(rows):
                fired.append(Fired(signal, rows.to_dict("records")))
        score = 1 - prod(1 - f.signal.weight for f in fired)
        return Detection(self, score, fired, self.facts(fired))

    def facts(self, fired: list[Fired]) -> dict:
        return {}

    def actions(self, profile: dict, detection: Detection) -> list[Action]:
        return []


class Moving(LifeEvent):
    def facts(self, fired):
        ids = {f.signal.id for f in fired}
        addresses = [m.group(1) for f in fired for row in f.evidence if (m := ADDRESS.search(row["description"]))]
        return {
            "kind": "buy" if ids & {"notary", "mortgage"} else "rent",
            "new_address": addresses[0] if addresses else None,
        }

    def actions(self, profile, detection):
        new = detection.facts.get("new_address") or "your new address"
        buying = detection.facts.get("kind") == "buy"
        has = {p["type"] for p in profile["products"]}
        actions = []
        if "home" in has and buying:
            actions.append(Action("home_owner", f"Switch home insurance to owner cover at {new}",
                                  "Your tenant policy does not cover a house you own. Building and contents, "
                                  "active from the day of the deed.", "insurance", 480, 40))
            actions.append(Action("home_stop", f"End tenant cover on {profile['address']}",
                                  "Stops on the handover date, so you never pay double.", "insurance", 0, 15))
            actions.append(Action("loan_cover", "Review debt balance insurance for your new home loan",
                                  "Protects your family if one income falls away.", "insurance", 320, 30))
        elif "home" in has:
            actions.append(Action("home_move", f"Move home insurance to {new}",
                                  "Same cover, new address and size.", "insurance", 210, 30))
        else:
            actions.append(Action("home_new", f"Take out tenant fire insurance for {new}",
                                  "Required for tenants in Flanders. In your own flat you are no longer "
                                  "covered by someone else's policy.", "insurance", 145, 40))
        if "car" in has:
            actions.append(Action("car_address", "Update the address on your car insurance",
                                  "Your premium can change with your postcode. We recalculate it for you.",
                                  "insurance", 0, 15))
        if "family" not in has:
            actions.append(Action("family_new", "Add family liability insurance",
                                  "Covers damage you cause to others, e.g. water damage at the neighbours.",
                                  "insurance", 85, 20))
        actions.append(Action("bank_address", "Update your address on accounts and cards",
                              f"New address: {new}.", "bank", 0, 15))
        actions.append(Action("energy", "Remind me to hand over energy and water meters",
                              "Reminder on moving day with the handover form ready.", "reminder", 0, 25))
        return actions


UTILITIES = r"engie|luminus|bolt energie|eneco|mega|telenet|proximus|orange|pidpa|farys|de watergroep|fluvius"

MOVING = Moving(
    "moving", "Moving house", "🏠",
    signals=[
        Signal("deposit", "Rental deposit paid", 0.45, keyword(r"huurwaarborg|waarborg|rental deposit")),
        Signal("notary", "Notary payment", 0.45, keyword(r"notaris|notaire")),
        Signal("mortgage", "Home loan started", 0.35, keyword(r"woonkrediet|hypothe", new_only=True)),
        Signal("new_rent", "Rent to a new landlord", 0.30,
               keyword(r"huur|loyer", exclude=r"waarborg|bestelwagen", new_only=True)),
        Signal("mover", "Moving company or van rental", 0.40, keyword(r"verhuizing|bestelwagen|déménage")),
        Signal("postal", "Mail forwarding ordered", 0.35, keyword(r"do my move|verhuisdienst")),
        Signal("utility", "New utility or telecom contract", 0.20, keyword(UTILITIES, new_only=True)),
        Signal("furniture", "Furniture and DIY spend spike", 0.15,
               spend_spike(r"ikea|brico|gamma|hubo|leen bakker|jysk", 500)),
    ],
)

# Declared plug-ins (not wired yet): add `match` functions and an `actions` override to go live.
REGISTRY = [
    MOVING,
    LifeEvent("baby", "New baby", "👶", live=False,
              signals=[Signal("s1", "Pharmacy and baby-store spend spike", 0.3),
                       Signal("s2", "Hospital maternity invoice", 0.5),
                       Signal("s3", "Child benefit (Groeipakket) starts", 0.6)],
              example_actions=["Add child to hospitalisation plan", "Review family liability",
                               "Open a savings account for the child"]),
    LifeEvent("car", "New car", "🚗", live=False,
              signals=[Signal("s1", "Payment to a car dealer", 0.5),
                       Signal("s2", "Vehicle registration (DIV) fee", 0.5),
                       Signal("s3", "Road tax for a new plate", 0.4)],
              example_actions=["Car insurance quote ready to sign", "Add assistance cover",
                               "Car loan offer"]),
    LifeEvent("job", "New job", "💼", live=False,
              signals=[Signal("s1", "Salary from a new employer", 0.6),
                       Signal("s2", "Salary amount changes by more than 15%", 0.3),
                       Signal("s3", "Commute spend pattern changes", 0.2)],
              example_actions=["Check income protection", "Adjust pension savings",
                               "Update car insurance mileage"]),
]
