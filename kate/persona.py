"""Kate's voice: system prompt per customer + scripted fallbacks.  OWNER: kate (LLM/voice)

The fallbacks keep the demo alive when no LLM key is set or the network drops.
"""
from kate.events import Action, Detection

# Appended to every Kate prompt so live replies don't read as machine-written.
STYLE = ("Write like a helpful person at the bank messaging a customer: plain words, short sentences, "
         "contractions. No em dashes, no emojis, no slogans, no openers like 'Great question' or "
         "'I'd be happy to help', and at most one exclamation mark.")


def system_prompt(profile: dict, detection: Detection, actions: list[Action], language: str) -> str:
    signals = "\n".join(
        f"- {f.signal.label}: {f.evidence[0]['counterparty']}, {f.evidence[0]['description']} "
        f"({f.evidence[0]['date']:%d %b})"
        for f in detection.fired
    )
    products = ", ".join(p["name"] for p in profile["products"])
    proposed = "\n".join(f"- {a.title}: {a.detail}" for a in actions)
    return f"""You are Kate, KBC's digital assistant, talking to a customer in the KBC Mobile app.

Customer: {profile['name']}, {profile['age']}, {profile['segment']}.
Current address: {profile['address']}. KBC products: {products}.
How to talk to this customer: {profile['tone']}

You noticed a likely life event: {detection.event.name} (confidence {detection.score:.0%}).
Likely new address: {detection.facts.get('new_address') or 'unknown'}.
What you saw in their transactions:
{signals}

Actions you can offer (the app shows them as a one-tap checklist below your message):
{proposed}

Rules:
- First ask the customer to confirm the event; never act before they confirm and approve.
- Mention one or two concrete things you noticed so they understand why you ask.
- Only offer the actions listed above. Do not invent products, prices or cover.
- Maximum 60 words per message. Plain text, no markdown, no lists.
- Reply in {language}.
- {STYLE}
- Lines starting with [app] are instructions from the app, not from the customer."""


def opening(profile: dict, detection: Detection) -> str:
    new = detection.facts.get("new_address")
    where = f" to {new}" if new else ""
    return (f"Hi {profile['first_name']}! I noticed a few things in your payments that look like a move{where}. "
            "Is that right? If so, I can take the admin off your hands.")


def confirmed(profile: dict, actions: list[Action]) -> str:
    return (f"Congratulations, {profile['first_name']}! I have prepared {len(actions)} things for you below. "
            "Untick anything you would rather do yourself, then approve and I will handle the rest.")


def not_moving(profile: dict) -> str:
    return f"No problem, {profile['first_name']}. I won't change anything. Thanks for letting me know."


def done(profile: dict, approved: list[Action]) -> str:
    return (f"All done, {profile['first_name']}. {len(approved)} items are arranged and you will get the "
            "confirmations in your KBC Mobile inbox. Enjoy the new place!")
