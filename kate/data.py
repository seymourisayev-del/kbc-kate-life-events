"""Synthetic personas + 6 months of Belgian transactions.  OWNER: data

Run `python -m kate.data` to regenerate data/personas.json and data/transactions.csv.
Contract: transactions have columns persona_id, date, counterparty, description, amount.
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
START, END = date(2026, 4, 1), date(2026, 9, 30)

PERSONAS = [
    {
        "id": "lotte",
        "name": "Lotte Peeters",
        "first_name": "Lotte",
        "age": 26,
        "segment": "Young professional, first-time renter",
        "address": "Naamsestraat 80, 3000 Leuven",
        "start_balance": 3200,
        "tone": "Informal and warm, short sentences, first-name basis. She is new to insurance: "
        "explain in plain words, no jargon.",
        "products": [{"type": "account", "name": "KBC Plus Account"}],
    },
    {
        "id": "janssens",
        "name": "Tom & Sara Janssens",
        "first_name": "Tom",
        "age": 38,
        "segment": "Family with two kids, buying a first house",
        "address": "Bruul 22, 2800 Mechelen",
        "start_balance": 9400,
        "tone": "Friendly but efficient and structured. Busy parents: lead with what matters, "
        "be precise about cover and amounts.",
        "products": [
            {"type": "account", "name": "KBC Plus Account (joint)"},
            {"type": "home", "name": "KBC Home Insurance (tenant)", "annual_premium": 210},
            {"type": "car", "name": "KBC Car Insurance", "annual_premium": 640},
            {"type": "family", "name": "KBC Family Liability", "annual_premium": 95},
        ],
    },
    {
        "id": "marc",
        "name": "Marc De Smet",
        "first_name": "Marc",
        "age": 54,
        "segment": "Homeowner, stable (control: no life event)",
        "address": "Langestraat 101, 8000 Brugge",
        "start_balance": 12800,
        "tone": "Polite and to the point.",
        "products": [
            {"type": "account", "name": "KBC Plus Account"},
            {"type": "home", "name": "KBC Home Insurance (owner)", "annual_premium": 460},
            {"type": "car", "name": "KBC Car Insurance", "annual_premium": 590},
            {"type": "family", "name": "KBC Family Liability", "annual_premium": 95},
        ],
    },
]

# (day of month, counterparty, description, amount, last month it occurs or None)
RECURRING = {
    "lotte": [
        (25, "Studio Nova BV", "Loon", 2450, None),
        (1, "Dhr. Maes", "Huur kot Naamsestraat 80, 3000 Leuven", -540, 8),
        (5, "Orange Belgium", "Abonnement mobiel", -22, None),
        (12, "Spotify", "Premium", -11.99, None),
        (15, "NMBS", "Abonnement trein", -49, None),
        (18, "Basic-Fit", "Lidmaatschap", -29.99, None),
    ],
    "janssens": [
        (25, "Atlas Engineering NV", "Loon Tom", 3450, None),
        (27, "AZ Sint-Maarten", "Loon Sara", 2890, None),
        (1, "Immo Dijle", "Huur appartement Bruul 22, 2800 Mechelen", -1150, None),
        (3, "Engie", "Voorschot elektriciteit en gas", -145, None),
        (6, "Proximus", "Flex pack", -89, None),
        (10, "KBC Verzekeringen", "Premie brand, auto, familiale", -78.75, None),
        (15, "Kinderopvang De Zonnebloem", "Opvang", -480, None),
        (20, "Netflix", "Abonnement", -13.99, None),
    ],
    "marc": [
        (25, "Stad Brugge", "Loon", 3900, None),
        (3, "Engie", "Voorschot elektriciteit en gas", -130, None),
        (6, "Telenet", "Internet en tv", -75, None),
        (10, "KBC Verzekeringen", "Premie brand, auto, familiale", -95.42, None),
    ],
}

# (date, counterparty, description, amount) — the life-event story lives here
ONE_OFF = {
    "lotte": [
        ("2026-08-21", "KBC Huurwaarborg", "Huurwaarborg Korenmarkt 12, 9000 Gent", -1700),
        ("2026-09-01", "Immo Gent Centrum", "Huur appartement Korenmarkt 12, 9000 Gent", -850),
        ("2026-09-03", "bpost", "Do My Move verhuisdienst", -29.5),
        ("2026-09-05", "Europcar Gent", "Huur bestelwagen", -89),
        ("2026-09-06", "IKEA Gent", "Aankoop", -612.4),
        ("2026-09-08", "Telenet", "Installatie internet Korenmarkt 12", -50),
        ("2026-09-10", "Bolt Energie", "Voorschot elektriciteit", -65),
        ("2026-09-13", "Brico Gent", "Aankoop", -84.3),
    ],
    "janssens": [
        ("2026-07-10", "Notaris Vermeulen", "Voorschot compromis Kerkstraat 45, 2500 Lier", -5000),
        ("2026-08-28", "Spaarrekening Janssens", "Overschrijving eigen inbreng", 45000),
        ("2026-09-04", "Notaris Vermeulen", "Akte aankoop woning Kerkstraat 45, 2500 Lier", -41200),
        ("2026-09-09", "bpost", "Do My Move verhuisdienst", -29.5),
        ("2026-09-10", "KBC Woonkrediet", "Aflossing woonkrediet Kerkstraat 45, 2500 Lier", -1480),
        ("2026-09-12", "Verhuizingen Dockx", "Verhuizing Mechelen - Lier", -1250),
        ("2026-09-13", "IKEA Wilrijk", "Aankoop", -1890),
        ("2026-09-14", "Brico Lier", "Aankoop", -420),
        ("2026-09-15", "Pidpa", "Aansluiting water Kerkstraat 45", -75),
    ],
    "marc": [("2026-09-12", "IKEA Gent", "Aankoop zetel", -689)],
}

# (counterparties, payments per week, min, max)
EVERYDAY = [
    (["Colruyt", "Delhaize", "Albert Heijn", "Lidl"], 2.0, 15, 75),
    (["Takeaway.com", "Deliveroo", "Panos", "Exki"], 1.0, 8, 35),
    (["bol.com", "Zalando", "HEMA", "Kruidvat"], 0.5, 12, 90),
    (["Q8", "TotalEnergies", "De Lijn"], 0.5, 3, 70),
]


def generate(seed: int = 7) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for persona in PERSONAS:
        pid = persona["id"]
        month = START
        while month <= END:
            for day, cp, desc, amount, last_month in RECURRING[pid]:
                if last_month is None or month.month <= last_month:
                    rows.append((pid, month.replace(day=day), cp, desc, amount))
            month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
        for d, cp, desc, amount in ONE_OFF[pid]:
            rows.append((pid, date.fromisoformat(d), cp, desc, amount))
        day = START
        while day <= END:
            for shops, per_week, low, high in EVERYDAY:
                if rng.random() < per_week / 7:
                    rows.append((pid, day, rng.choice(shops), "Bancontact", -round(rng.uniform(low, high), 2)))
            day += timedelta(days=1)
    df = pd.DataFrame(rows, columns=["persona_id", "date", "counterparty", "description", "amount"])
    return df.sort_values(["persona_id", "date"]).reset_index(drop=True)


def load_personas() -> list[dict]:
    return json.loads((DATA / "personas.json").read_text(encoding="utf-8"))


def load_transactions() -> pd.DataFrame:
    return pd.read_csv(DATA / "transactions.csv", parse_dates=["date"])


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    (DATA / "personas.json").write_text(json.dumps(PERSONAS, indent=2, ensure_ascii=False), encoding="utf-8")
    df = generate()
    df.to_csv(DATA / "transactions.csv", index=False)
    print(f"{len(PERSONAS)} personas, {len(df)} transactions -> {DATA}")
