"""Three months of categorised transactions for a typical Belgian household.  OWNER: data

Run `python -m kate.avg_belgian` to write data/avg_belgian_transactions.csv and
data/avg_belgian_profile.json. Amounts are plausible for 2026, not official statistics.
"""
import json
import random
from datetime import date, timedelta

import pandas as pd

from kate.data import DATA

START, END = date(2026, 7, 1), date(2026, 9, 30)
HOLIDAY = (date(2026, 7, 6), date(2026, 7, 13))  # a week in France

PROFILE = {
    "id": "avg",
    "name": "Sofie Claes",
    "first_name": "Sofie",
    "age": 41,
    "segment": "Typical Belgian household: couple, one child (9), owner with a mortgage, one car",
    "address": "Edegemsestraat 58, 2640 Mortsel",
    "start_balance": 4850,
    "tone": "Friendly and practical. Busy, likes quick answers with one concrete number.",
    "products": [
        {"type": "account", "name": "KBC Plus Account (joint)"},
        {"type": "savings", "name": "KBC Start2Save"},
        {"type": "mortgage", "name": "KBC Home Loan"},
        {"type": "home", "name": "KBC Home Insurance (owner)", "annual_premium": 520},
        {"type": "car", "name": "KBC Car Insurance", "annual_premium": 690},
        {"type": "family", "name": "KBC Family Liability", "annual_premium": 95},
    ],
}

# (day, counterparty, description, amount, category, subcategory, method)
MONTHLY = [
    (25, "Brightfield NV", "Loon Sofie", 2940.12, "Income", "Salary", "Transfer"),
    (27, "Colruyt Group", "Loon Pieter", 2610.55, "Income", "Salary", "Transfer"),
    (5, "Infino", "Groeipakket", 187.13, "Income", "Child benefit", "Transfer"),
    (1, "KBC Woonkrediet", "Aflossing woonkrediet", -1045.60, "Housing", "Mortgage", "Direct debit"),
    (2, "KBC Start2Save", "Maandelijkse spaaropdracht", -300, "Savings", "Savings plan", "Standing order"),
    (8, "Engie", "Voorschot elektriciteit", -94.00, "Energy", "Electricity", "Direct debit"),
    (8, "Engie", "Voorschot aardgas", -118.00, "Energy", "Gas", "Direct debit"),
    (12, "water-link", "Voorschot water", -36.50, "Utilities", "Water", "Direct debit"),
    (15, "Telenet", "Internet en tv", -89.00, "Utilities", "Internet & TV", "Direct debit"),
    (17, "Orange Belgium", "Mobiel 2 abonnementen", -44.00, "Utilities", "Mobile", "Direct debit"),
    (10, "KBC Verzekeringen", "Premie woning, auto, familiale", -108.75, "Insurance", "Home, car & family",
     "Direct debit"),
    (20, "Netflix", "Abonnement", -13.99, "Entertainment", "Streaming", "Card"),
    (21, "Spotify", "Premium Family", -17.99, "Entertainment", "Streaming", "Card"),
    (23, "Disney+", "Abonnement", -9.99, "Entertainment", "Streaming", "Card"),
    (3, "Basic-Fit", "Lidmaatschap", -29.99, "Hobbies", "Sports", "Direct debit"),
    (14, "Tennisclub Mortsel", "Lidgeld jeugd", -22.00, "Hobbies", "Sports", "Direct debit"),
]

# (date, counterparty, description, amount, category, subcategory, method)
ONE_OFF = [
    ("2026-07-06", "Sanef", "Péage A26", -38.20, "Transport", "Tolls & parking", "Card"),
    ("2026-07-06", "Camping Les Pins", "Verblijf 7 nachten", -640.00, "Travel", "Accommodation", "Card"),
    ("2026-07-07", "Carrefour Market Annecy", "Courses", -84.35, "Travel", "Food abroad", "Card"),
    ("2026-07-09", "Restaurant Le Lac", "Repas", -96.50, "Travel", "Food abroad", "Card"),
    ("2026-07-10", "Intermarché Annecy", "Courses", -61.10, "Travel", "Food abroad", "Card"),
    ("2026-07-11", "TotalEnergies Chambéry", "Carburant", -78.40, "Transport", "Fuel", "Card"),
    ("2026-07-13", "Sanef", "Péage A26", -38.20, "Transport", "Tolls & parking", "Card"),
    ("2026-07-20", "Sportkamp Sporty", "Sportkamp week 30", -135.00, "Children", "Holiday camps", "Transfer"),
    ("2026-07-28", "Garage Verhaegen", "Onderhoud auto", -289.00, "Transport", "Car maintenance", "Bancontact"),
    ("2026-08-03", "Speelplein Mortsel", "Speelpleinwerking", -45.00, "Children", "Holiday camps", "Transfer"),
    ("2026-08-15", "Ticketmaster", "Concert Sportpaleis", -118.00, "Entertainment", "Concerts & events", "Card"),
    ("2026-08-24", "Standaard Boekhandel", "Schoolgerief", -86.40, "Children", "School", "Bancontact"),
    ("2026-08-26", "Zeeman", "Kinderkleding", -54.90, "Shopping", "Clothing", "Bancontact"),
    ("2026-09-02", "Sint-Jozefschool", "Schoolfactuur september", -62.00, "Children", "School", "Transfer"),
    ("2026-09-12", "Kinepolis Antwerpen", "Tickets", -38.50, "Entertainment", "Cinema", "Card"),
    ("2026-09-18", "Pierre & Vacances", "Verblijf Normandie 26/10 - 01/11", -690.00, "Travel", "Accommodation",
     "Card"),
    ("2026-09-19", "Engie", "Jaarafrekening energie", -212.37, "Energy", "Annual settlement", "Direct debit"),
    ("2026-09-23", "CM Mutualiteit", "Ledenbijdrage Q4", -39.00, "Health", "Health insurance", "Direct debit"),
]

# (counterparties, payments per week, min, max, category, subcategory)
EVERYDAY = [
    (["Colruyt", "Delhaize", "Aldi", "Lidl", "Albert Heijn", "Carrefour"], 3.0, 18, 120, "Groceries", "Supermarket"),
    (["Bakkerij Van Loock", "Slagerij De Wit"], 1.5, 4, 18, "Groceries", "Bakery & butcher"),
    (["Action", "HEMA", "Kruidvat", "Brico", "Hubo"], 1.0, 6, 70, "Household", "Household items"),
    (["Q8", "TotalEnergies", "Esso"], 0.6, 45, 80, "Transport", "Fuel"),
    (["De Lijn", "NMBS", "Interparking"], 0.3, 3, 20, "Transport", "Public transport & parking"),
    (["Takeaway.com", "Frituur 't Hoekske", "Pizza Hut", "Panos"], 1.0, 12, 48, "Entertainment", "Eating out"),
    (["Decathlon", "Club", "Game Mania", "Standaard Boekhandel"], 0.25, 10, 65, "Hobbies", "Hobby shops"),
    (["bol.com", "Coolblue", "Zalando", "C&A"], 0.6, 12, 110, "Shopping", "Products online & clothing"),
    (["Apotheek Mortsel", "Huisarts Dr. Wouters"], 0.3, 8, 40, "Health", "Pharmacy & doctor"),
    (["Batopin"], 0.3, 40, 60, "Cash", "ATM withdrawal"),
]


def generate(seed: int = 11) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    month = START
    while month <= END:
        for day, cp, desc, amount, cat, sub, method in MONTHLY:
            rows.append((month.replace(day=day), cp, desc, amount, cat, sub, method))
        month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    for d, cp, desc, amount, cat, sub, method in ONE_OFF:
        rows.append((date.fromisoformat(d), cp, desc, amount, cat, sub, method))
    day = START
    while day <= END:
        if not HOLIDAY[0] <= day <= HOLIDAY[1]:
            for shops, per_week, low, high, cat, sub in EVERYDAY:
                if rng.random() < per_week / 7:
                    amount = rng.uniform(low, high)
                    amount = round(amount, -1) if cat == "Cash" else round(amount, 2)
                    method = "Cash withdrawal" if cat == "Cash" else rng.choice(["Bancontact", "Bancontact", "Payconiq"])
                    rows.append((day, rng.choice(shops), "Aankoop" if cat != "Cash" else "Geldafhaling", -amount,
                                 cat, sub, method))
        day += timedelta(days=1)
    columns = ["date", "counterparty", "description", "amount", "category", "subcategory", "payment_method"]
    df = pd.DataFrame(rows, columns=columns).sort_values("date").reset_index(drop=True)
    df.insert(0, "persona_id", PROFILE["id"])
    return df


def load() -> tuple[dict, pd.DataFrame]:
    profile = json.loads((DATA / "avg_belgian_profile.json").read_text(encoding="utf-8"))
    return profile, pd.read_csv(DATA / "avg_belgian_transactions.csv", parse_dates=["date"])


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    (DATA / "avg_belgian_profile.json").write_text(json.dumps(PROFILE, indent=2, ensure_ascii=False), encoding="utf-8")
    df = generate()
    df.to_csv(DATA / "avg_belgian_transactions.csv", index=False, encoding="utf-8-sig")
    month = pd.to_datetime(df["date"]).dt.strftime("%b")
    summary = df.pivot_table(index="category", columns=month, values="amount", aggfunc="sum", sort=False)
    print(f"{len(df)} transactions -> {DATA / 'avg_belgian_transactions.csv'}\n")
    print(summary[["Jul", "Aug", "Sep"]].round(0).to_string())
