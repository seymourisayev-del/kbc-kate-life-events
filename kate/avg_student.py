"""Three months of categorised transactions for a typical Belgian student.  OWNER: data

Run `python -m kate.avg_student` to write data/avg_student_transactions.csv and
data/avg_student_profile.json. Amounts are plausible for 2026, not official statistics.

Story: summer at his parents' in Hasselt with a student job (Jul - mid Sep), festivals,
then into his kot in Leuven on 14 Sep; the academic year starts 21 Sep.
"""
import json
import random
from datetime import date, datetime, time, timedelta

import pandas as pd

from kate.data import DATA

START, END = date(2026, 7, 1), date(2026, 9, 30)
KOT_FROM, TERM_FROM = date(2026, 9, 14), date(2026, 9, 21)

PROFILE = {
    "id": "student",
    "name": "Arne Wouters",
    "first_name": "Arne",
    "age": 20,
    "segment": "Student, 2nd year engineering at KU Leuven, student job in summer",
    "address": "Tiensestraat 112, 3000 Leuven (kot); parents in Hasselt",
    "start_balance": 640,
    "tone": "Casual, short, a bit of humour, never preachy about drinking or spending.",
    "products": [
        {"type": "account", "name": "KBC Student Account"},
        {"type": "card", "name": "KBC Debit Card"},
    ],
    "notes": "No insurance of his own: relies on his parents' family liability and home insurance.",
    # Illustrative: what a linked Basic-Fit account would show. Premium = all clubs + bring a buddy.
    "gym_usage": {"tier": "Premium", "price": 29.99, "basic_price": 19.99, "clubs_used": 1, "buddy_visits": 0,
                  "visits_30d": 3},
}

# (date, time, counterparty, description, amount, category, subcategory, method)
ONE_OFF = [
    ("2026-07-02", "14:10", "Rock Werchter", "Tokens", -62.00, "Drinks & nightlife", "Festivals", "Card"),
    ("2026-07-03", "22:40", "Rock Werchter", "Tokens", -48.00, "Drinks & nightlife", "Festivals", "Card"),
    ("2026-07-04", "18:05", "Rock Werchter", "Tokens", -55.00, "Drinks & nightlife", "Festivals", "Card"),
    ("2026-08-13", "16:30", "Pukkelpop", "Tokens", -70.00, "Drinks & nightlife", "Festivals", "Card"),
    ("2026-08-14", "21:15", "Pukkelpop", "Tokens", -64.00, "Drinks & nightlife", "Festivals", "Card"),
    ("2026-08-15", "19:45", "Pukkelpop", "Tokens", -58.00, "Drinks & nightlife", "Festivals", "Card"),
    ("2026-08-21", "10:02", "Acco", "Studiemateriaal herexamen", -18.50, "Education", "Books & courses", "Card"),
    ("2026-09-01", "09:12", "Immo Tiensepoort", "Huur kot september", -495.00, "Housing", "Kot rent", "Transfer"),
    ("2026-09-08", "11:30", "KU Leuven", "Inschrijvingsgeld 2026-2027", -1150.00, "Education", "Tuition", "Transfer"),
    ("2026-09-14", "15:20", "Action Leuven", "Spullen kot", -46.80, "Household", "Kot supplies", "Bancontact"),
    ("2026-09-14", "17:05", "IKEA Zaventem", "Bureaulamp, rek", -79.00, "Household", "Kot supplies", "Bancontact"),
    ("2026-09-22", "13:40", "Acco", "Cursussen semester 1", -142.60, "Education", "Books & courses", "Bancontact"),
    ("2026-09-24", "20:10", "VTK Leuven", "Lidkaart studentenvereniging", -15.00, "Drinks & nightlife",
     "Student club", "Payconiq"),
    ("2026-09-29", "21:30", "VTK Leuven", "Cantus", -12.00, "Drinks & nightlife", "Student club", "Payconiq"),
]

# (day, counterparty, description, amount, category, subcategory, method)
MONTHLY = [
    (1, "Ouders Wouters", "Zakgeld", 250.00, "Income", "Allowance", "Transfer"),
    (4, "Spotify", "Premium Student", -5.99, "Subscriptions", "Music", "Card"),
    (9, "Netflix", "Standard met reclame", -7.99, "Subscriptions", "Streaming", "Card"),
    (11, "Mobile Vikings", "Abonnement", -15.00, "Subscriptions", "Mobile", "Direct debit"),
    (13, "Apple", "iCloud+ 50 GB", -0.99, "Subscriptions", "Apps & cloud", "Card"),
    (17, "Basic-Fit", "Premium lidmaatschap", -29.99, "Hobbies", "Gym", "Direct debit"),
]

# Student job: weekly pay in summer, weekend job at the supermarket once in Leuven.
WEEKLY_PAY = [("Randstad Belgium", "Loon studentenjob", 310, 380, START, date(2026, 8, 31)),
              ("Delhaize Leuven", "Loon weekendjob", 105, 135, KOT_FROM, END)]


# (counterparties, chance per eligible day, weekdays, hours, min, max, category, subcategory, period)
# weekdays: 0=Mon ... 6=Sun; period: "summer" (Hasselt), "kot" (Leuven), "all"
EVERYDAY = [
    # Nights out: weekends at home, Wednesday/Thursday once on kot in Leuven
    (["Café Hemingway Hasselt", "Den Ouden Brouwer", "Café Paris Hasselt"], 0.55, {4, 5}, (21, 25), 9, 48,
     "Drinks & nightlife", "Bars", "summer"),
    (["Café Commerce", "De Giraf", "Café Belge", "Den Bittere Pint", "Café Entrepot"], 0.8, {2, 3}, (21, 27), 10, 55,
     "Drinks & nightlife", "Bars", "kot"),
    (["Nachtwinkel Naamsestraat", "Carrefour Express Leuven"], 0.35, {2, 3, 4}, (20, 24), 6, 22,
     "Drinks & nightlife", "Beer & night shop", "kot"),
    (["Colruyt", "Carrefour Market"], 0.15, {4, 5}, (15, 19), 14, 24,
     "Drinks & nightlife", "Beer & night shop", "summer"),
    # Food delivery: lazy evenings, plus late-night orders after going out (see below)
    (["Uber Eats"], 0.14, {0, 1, 2, 3, 4, 5, 6}, (18, 22), 14, 29, "Food delivery", "Uber Eats", "all"),
    (["Delhaize Leuven", "Aldi Leuven", "Carrefour Express Leuven"], 0.3, {0, 1, 2, 3, 4, 5, 6}, (11, 20), 6, 38,
     "Groceries", "Supermarket", "kot"),
    (["Alma", "Alma 2"], 0.45, {0, 1, 2, 3, 4}, (12, 14), 3, 6, "Eating out", "Student restaurant", "kot"),
    (["Frituur De Pits", "Panos", "Quick"], 0.12, {0, 1, 2, 3, 4, 5, 6}, (12, 21), 6, 14, "Eating out",
     "Snacks & fast food", "all"),
    (["NMBS"], 0.12, {4, 6}, (8, 20), 6, 12, "Transport", "Train", "all"),
    (["Uber"], 0.06, {4, 5, 6}, (24, 27), 9, 19, "Transport", "Taxi rides", "all"),
    (["Zalando", "Primark", "JBC"], 0.03, {0, 1, 2, 3, 4, 5, 6}, (10, 22), 18, 70, "Shopping", "Clothing", "all"),
    (["Payconiq: Lukas", "Payconiq: Emma", "Payconiq: Jonas"], 0.1, {0, 1, 2, 3, 4, 5, 6}, (12, 24), 4, 30,
     "Transfers to friends", "Splitting bills", "all"),
    (["Batopin"], 0.05, {0, 1, 2, 3, 4, 5, 6}, (10, 23), 20, 40, "Cash", "ATM withdrawal", "all"),
]


def _period(day: date) -> str:
    return "kot" if day >= KOT_FROM else "summer"


def _at(rng, day: date, hours: tuple[int, int]) -> datetime:
    """Random timestamp; hours past 24 roll over into the next night."""
    minutes = rng.randint(hours[0] * 60, hours[1] * 60 - 1)
    return datetime.combine(day, time()) + timedelta(minutes=minutes)


def generate(seed: int = 23) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []

    def add(ts, cp, desc, amount, cat, sub, method):
        rows.append((ts, cp, desc, round(amount, 2), cat, sub, method))

    month = START
    while month <= END:
        for day, cp, desc, amount, cat, sub, method in MONTHLY:
            add(_at(rng, month.replace(day=day), (7, 10)), cp, desc, amount, cat, sub, method)
        month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    for d, t, cp, desc, amount, cat, sub, method in ONE_OFF:
        add(datetime.combine(date.fromisoformat(d), time.fromisoformat(t)), cp, desc, amount, cat, sub, method)

    day = START
    while day <= END:
        for cp, desc, low, high, first, last in WEEKLY_PAY:
            if first <= day <= last and day.weekday() == 4:
                add(_at(rng, day, (6, 9)), cp, desc, rng.uniform(low, high), "Income", "Student job", "Transfer")
        for shops, chance, weekdays, hours, low, high, cat, sub, period in EVERYDAY:
            if day.weekday() in weekdays and period in ("all", _period(day)) and rng.random() < chance:
                cp = rng.choice(shops)
                if cat == "Transfers to friends":
                    method, desc = "Payconiq", "Terugbetaling"
                elif cp.startswith("Uber"):
                    method, desc = "Card", "Bestelling" if cp == "Uber Eats" else "Rit"
                elif cat == "Cash":
                    method, desc = "Cash withdrawal", "Geldafhaling"
                else:
                    method, desc = rng.choice(["Card", "Bancontact", "Payconiq"]), "Aankoop"
                amount = rng.uniform(low, high)
                amount = round(amount, -1) if cat == "Cash" else amount
                add(_at(rng, day, hours), cp, desc, -amount, cat, sub, method)
                if sub == "Bars" and rng.random() < 0.45:  # the 1 AM order on the way home
                    add(_at(rng, day, (25, 27)), "Uber Eats", "Bestelling", -rng.uniform(16, 32),
                        "Food delivery", "Uber Eats", "Card")
        day += timedelta(days=1)

    df = pd.DataFrame(rows, columns=["ts", "counterparty", "description", "amount", "category", "subcategory",
                                     "payment_method"])
    df = df[df["ts"].dt.date <= END].sort_values("ts").reset_index(drop=True)
    df.insert(0, "time", df["ts"].dt.strftime("%H:%M"))
    df.insert(0, "date", df.pop("ts").dt.date)  # after-midnight orders book on the next day, as in a real statement
    df.insert(0, "persona_id", PROFILE["id"])
    return df


def load() -> tuple[dict, pd.DataFrame]:
    profile = json.loads((DATA / "avg_student_profile.json").read_text(encoding="utf-8"))
    return profile, pd.read_csv(DATA / "avg_student_transactions.csv", parse_dates=["date"])


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    (DATA / "avg_student_profile.json").write_text(json.dumps(PROFILE, indent=2, ensure_ascii=False), encoding="utf-8")
    df = generate()
    df.to_csv(DATA / "avg_student_transactions.csv", index=False, encoding="utf-8-sig")
    month = pd.to_datetime(df["date"]).dt.strftime("%b")
    summary = df.pivot_table(index="category", columns=month, values="amount", aggfunc="sum", sort=False)
    print(f"{len(df)} transactions -> {DATA / 'avg_student_transactions.csv'}\n")
    print(summary[["Jul", "Aug", "Sep"]].round(0).to_string())
