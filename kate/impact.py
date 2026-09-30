"""The business number.  OWNER: pitch

Every value in ASSUMPTIONS is an illustrative placeholder: replace with sourced figures
before the pitch and be ready to defend each one.
"""

# key: (label, default, min, max, step)
ASSUMPTIONS = {
    "move_rate": ("Customers who move per year (%)", 9.0, 1.0, 20.0, 0.5),
    "detect_rate": ("Movers Kate detects (%)", 70.0, 10.0, 100.0, 5.0),
    "kbc_home_share": ("Movers with KBC home insurance (%)", 35.0, 5.0, 90.0, 5.0),
    "churn_today": ("Policy churn at a move today (%)", 20.0, 0.0, 60.0, 1.0),
    "churn_with_kate": ("Policy churn at a move with Kate (%)", 8.0, 0.0, 60.0, 1.0),
    "convert_rate": ("Other movers who take a KBC policy (%)", 12.0, 0.0, 50.0, 1.0),
    "premium": ("Average home premium (€ / year)", 380.0, 100.0, 1000.0, 10.0),
    "underinsured": ("Movers un- or underinsured after moving (%)", 30.0, 0.0, 80.0, 5.0),
    "hours_saved": ("Admin hours saved per mover", 3.0, 0.5, 10.0, 0.5),
}

DEFAULTS = {key: spec[1] for key, spec in ASSUMPTIONS.items()}


def compute(a: dict, customers: int = 10_000) -> dict:
    detected = customers * a["move_rate"] / 100 * a["detect_rate"] / 100
    kbc = detected * a["kbc_home_share"] / 100
    retained = kbc * (a["churn_today"] - a["churn_with_kate"]) / 100
    won = (detected - kbc) * a["convert_rate"] / 100
    return {
        "detected": detected,
        "retained": retained,
        "won": won,
        "premium": (retained + won) * a["premium"],
        "underinsured_caught": detected * a["underinsured"] / 100,
        "hours_saved": detected * a["hours_saved"],
    }
