"""Trip cover check: "are we covered for this trip?"  OWNER: kate

Reads an upcoming trip from the transactions and checks it against the customer's products.
Cover rules and premiums are illustrative placeholders, not KBC policy terms.
"""
import re
from dataclasses import dataclass

import pandas as pd

BOOKING = re.compile(r"verblijf|camping|hotel|airbnb|booking\.com|pierre & vacances", re.I)
TRIP_DETAILS = re.compile(r"Verblijf (\w+) (\d{2}/\d{2}) - (\d{2}/\d{2})")


@dataclass
class Check:
    risk: str
    covered: bool
    by: str
    fix: str | None = None
    fix_premium: float = 0  # € per year


def find_trip(txs: pd.DataFrame, today) -> dict | None:
    """Most recent holiday booking in the last 60 days whose stay is still ahead."""
    today = pd.Timestamp(today)
    recent = txs[(txs["date"] <= today) & (txs["date"] >= today - pd.Timedelta(days=60))]
    for row in recent[recent["description"].str.contains(BOOKING)].iloc[::-1].to_dict("records"):
        if m := TRIP_DETAILS.search(row["description"]):
            return {"destination": m.group(1), "from": m.group(2), "to": m.group(3),
                    "booked_with": row["counterparty"], "cost": -row["amount"], "booked_on": row["date"]}
    return None


def check(profile: dict, txs: pd.DataFrame, trip: dict) -> list[Check]:
    has = {p["type"] for p in profile["products"]}
    drives = "car" in has and txs["subcategory"].eq("Fuel").any()
    checks = [
        Check("Medical costs and repatriation abroad", "travel" in has,
              "KBC Travel Insurance" if "travel" in has else "Only the basics via your mutuality (EHIC card)",
              "KBC Travel Insurance, whole family, all year", 119),
        Check(f"Cancelling the €{trip['cost']:.0f} booking with {trip['booked_with']}", "travel" in has,
              "KBC Travel Insurance" if "travel" in has else "Not covered", "Included in KBC Travel Insurance", 0),
    ]
    if drives:
        checks.append(Check("Car breakdown on the way to " + trip["destination"], "assistance" in has,
                            "KBC Car Assistance" if "assistance" in has else "Your car policy has no assistance",
                            "Add Car Assistance incl. abroad to your KBC Car Insurance", 84))
    checks += [
        Check("Damage you or your child cause to others", "family" in has, "KBC Family Liability, worldwide"),
        Check("Burglary at home while you are away", "home" in has, "KBC Home Insurance"),
    ]
    return checks


def gaps(checks: list[Check]) -> list[Check]:
    return [c for c in checks if not c.covered]
