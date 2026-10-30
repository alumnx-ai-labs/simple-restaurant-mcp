"""The guided booking conversation, asked as Jev-style Choice questions.

Q1 cuisine (tool 1) -> Q2 restaurant -> Q3 date -> Q4 party size -> booking.
If the user dislikes the options, or the table is fully booked, the flow
restarts at Q1. The server is stateless: `state` travels with each request.
"""

import json

from tools import (
    check_reservation_availability,
    get_restaurant_details,
    get_specialities,
    search_restaurants_by_cuisine,
)

CUISINES = ["Indian", "Italian", "Chinese", "Mexican"]

# Dates that exist in the sample availability data in tools.py.
DATES = [
    ("15 Nov 2024", "2024-11-15"),
    ("16 Nov 2024", "2024-11-16"),
    ("17 Nov 2024", "2024-11-17"),
]

PARTY_SIZES = [2, 4, 6]

START = {"asking": "cuisine"}

RESTART_LABEL = "None of these - start over"
RESTART_DESCRIPTION = (
    "The user dislikes these options, wants something different, "
    "or wants to start over"
)


def _choice(key: str, label: str, description: str) -> dict:
    # `message` is what the frontend sends when the user clicks the choice.
    return {"key": key, "label": label, "description": description, "message": label}


SPECIALITY_ALL = _choice(
    "speciality_all",
    "Show all special dishes",
    "The user wants to see the special dishes of all cuisines",
)


def _question(qid: str, text: str, choices: list[dict], restartable: bool = True) -> dict:
    choices = choices + [SPECIALITY_ALL]
    if restartable:
        choices = choices + [
            _choice("restart", RESTART_LABEL, RESTART_DESCRIPTION)
        ]
    return {"id": qid, "type": "choice", "text": text, "choices": choices}


def restaurants_for(cuisine: str) -> list[str]:
    found = search_restaurants_by_cuisine.invoke({"cuisine_type": cuisine})
    return [r["name"] for r in found]


def _base(state: dict) -> dict:
    """The booking position, even while the user is browsing dishes."""
    return state.get("resume", START) if state.get("asking") == "browse" else state


def _cuisine_now(state: dict) -> str | None:
    """The cuisine "this cuisine" refers to: the dish just asked about, else the booking's."""
    return state.get("dish_cuisine") or _base(state).get("cuisine")


def _browse(state: dict, dish: str | None = None, cuisine: str | None = None, restaurants: list[str] | None = None) -> dict:
    """Look at dishes without moving the booking; remember where to resume.

    After a single-dish answer, `restaurants` are the places serving it, which
    become the next question's choices.
    """
    browse = {"asking": "browse", "resume": _base(state)}
    if restaurants:
        browse.update({"dish": dish, "dish_cuisine": cuisine, "restaurants": restaurants})
    return browse


def question_for(state: dict) -> dict:
    """The Jev-format question the user is being asked right now."""
    question = _question_for_state(state)
    cuisine = _cuisine_now(state)
    if cuisine:
        # A cuisine is already chosen: offer just that cuisine's special dishes.
        chip = _choice(
            "speciality_cuisine",
            f"Show {cuisine} special dishes",
            f"The user wants to see only the special dishes of {cuisine} cuisine",
        )
        at = next(i for i, c in enumerate(question["choices"]) if c["key"] == "speciality_all")
        question["choices"].insert(at, chip)
    return question


def _question_for_state(state: dict) -> dict:
    asking = state.get("asking", "cuisine")

    if asking == "browse":
        base = _base(state)
        resume = _choice("resume", "Continue booking", "The user wants to go back to booking")
        restartable = base.get("asking", "cuisine") != "cuisine"
        if state.get("restaurants"):
            return _question(
                "browse",
                f"Which restaurant serving {state['dish']} would you like? Or ask about another dish.",
                [_choice(n, n, f"The restaurant {n}") for n in state["restaurants"]] + [resume],
                restartable=restartable,
            )
        return _question(
            "browse",
            "Ask about any dish, or go back to booking.",
            [resume],
            restartable=restartable,
        )

    if asking == "restaurant":
        cuisine = state["cuisine"]
        return _question(
            "restaurant",
            f"Which {cuisine} restaurant would you like?",
            [_choice(n, n, f"The restaurant {n}") for n in restaurants_for(cuisine)],
        )

    if asking == "date":
        return _question(
            "date",
            f"When would you like to book {state['restaurant']}?",
            [_choice(iso, label, f"The date {label}") for label, iso in DATES],
        )

    if asking == "party":
        return _question(
            "party",
            "How many people?",
            [_choice(str(n), f"{n} people", f"A party of {n}") for n in PARTY_SIZES],
        )

    return _question(
        "cuisine",
        "What cuisine would you like?",
        [_choice(c.lower(), c, f"{c} cuisine") for c in CUISINES],
        restartable=False,
    )


def _dish_names() -> list[str]:
    found = get_specialities.invoke({"query": ""})
    return sorted({d["dish"] for c in found["cuisines"] for d in c["dishes"]})


# Things the user may ask at any point. They are not buttons; Jev is told about
# them so it can recognise them in free text.
INTENTS = (
    [
        {
            "key": "speciality",
            "description": (
                "The user asks about specialities or signature dishes in general, "
                "without naming a cuisine or a specific dish"
            ),
        }
    ]
    + [
        {
            "key": f"speciality:{c}",
            "description": f"The user asks about the specialities or signature dishes of {c} cuisine",
        }
        for c in CUISINES
    ]
    + [
        {"key": f"dish:{d}", "description": f"The user asks about the dish {d}, or where to eat it"}
        for d in _dish_names()
    ]
)


def match_label(question: dict, message: str) -> str | None:
    """Fallback when Jev is unavailable: match the text against the choices."""
    text = message.strip().lower()
    for c in question["choices"]:
        if text in (c["label"].lower(), c["key"].lower()):
            return c["key"]
    return None


def _run(tool, **args) -> dict:
    """Run a tool directly and package it the way the frontend renders tool results."""
    out = tool.invoke(args)
    return {
        "name": tool.name,
        "args": args,
        "output": out if isinstance(out, str) else json.dumps(out, ensure_ascii=False),
    }


OTHER_REPLY = (
    "I can only help with restaurant bookings here. "
    "Pick one of the options below, or tell me which one you want."
)


def step(state: dict, choice: str | None) -> dict:
    """Advance the flow by one answer.

    Returns {state, tools, reply, notice}. `tools` are the tool calls Jev's
    decision triggers (maybe none), `reply` is the line shown with it, and
    `notice` is a line shown before the next question.
    """
    asking = state.get("asking", "cuisine")
    stay = {"state": state, "tools": [], "reply": OTHER_REPLY, "notice": None}

    if choice in (None, "other"):
        return stay

    # Speciality and dish questions can be asked at any point. They never move
    # the booking: the user stays in "browse" (so they can ask about another dish)
    # until they pick "Continue booking".
    if choice == "resume" and asking == "browse":
        return {"state": _base(state), "tools": [], "reply": "Okay, back to your booking.", "notice": None}

    cuisine_now = _cuisine_now(state)

    if choice == "speciality_all":
        return {
            "state": _browse(state),
            "tools": [_run(get_specialities, query="")],
            "reply": "Here are the special dishes of every cuisine, with the restaurants that serve them.",
            "notice": None,
        }

    if choice == "speciality_cuisine" and cuisine_now:
        return {
            "state": _browse(state),
            "tools": [_run(get_specialities, query=cuisine_now)],
            "reply": f"Here are the {cuisine_now} special dishes, with the restaurants that serve them.",
            "notice": None,
        }

    if choice == "speciality" or choice.startswith("speciality:"):
        cuisine = choice.split(":", 1)[1] if ":" in choice else cuisine_now
        if cuisine is None:
            return {
                "state": _browse(state),
                "tools": [_run(get_specialities, query="")],
                "reply": "Here are the special dishes of every cuisine, with the restaurants that serve them.",
                "notice": None,
            }
        return {
            "state": _browse(state),
            "tools": [
                _run(search_restaurants_by_cuisine, cuisine_type=cuisine),
                _run(get_specialities, query=cuisine),
            ],
            "reply": f"Here are the {cuisine} restaurants and the dishes they are known for.",
            "notice": None,
        }

    if choice.startswith("dish:"):
        dish = choice.split(":", 1)[1]
        call = _run(get_specialities, query=dish)
        found = json.loads(call["output"])
        if "cuisines" not in found:
            return {"state": _browse(state), "tools": [call], "reply": f"Sorry, I couldn't find {dish}.", "notice": None}
        first = found["cuisines"][0]
        names = [r["name"] for r in first["dishes"][0]["restaurants"]]
        return {
            "state": _browse(state, dish, first["cuisine"], names),
            "tools": [call],
            "reply": f"{dish} is on the {first['cuisine']} speciality list, served at {', '.join(names)}.",
            "notice": None,
        }

    if choice == "restart" and asking != "cuisine":
        return {
            "state": dict(START),
            "tools": [],
            "reply": "No problem, let's begin again!",
            "notice": "Okay, let's start over.",
        }

    if asking == "browse":
        if choice in state.get("restaurants", []):
            # They picked a restaurant serving the dish: carry on to booking it.
            return {
                "state": {"asking": "date", "cuisine": state["dish_cuisine"], "restaurant": choice},
                "tools": [_run(get_restaurant_details, restaurant_name=choice)],
                "reply": f"Here are the details for {choice}.",
                "notice": None,
            }
        return stay

    if asking == "cuisine":
        cuisine = next((c for c in CUISINES if c.lower() == choice), None)
        if cuisine is None:
            return stay
        return {
            "state": {"asking": "restaurant", "cuisine": cuisine},
            "tools": [_run(search_restaurants_by_cuisine, cuisine_type=cuisine)],
            "reply": f"Here are some {cuisine} restaurants you might like.",
            "notice": None,
        }

    if asking == "restaurant":
        return {
            "state": {**state, "asking": "date", "restaurant": choice},
            "tools": [_run(get_restaurant_details, restaurant_name=choice)],
            "reply": f"Here are the details for {choice}.",
            "notice": None,
        }

    if asking == "date":
        return {
            "state": {**state, "asking": "party", "date": choice},
            "tools": [],
            "reply": f"Great, {choice} it is.",
            "notice": None,
        }

    if asking == "party":
        party = int(choice)
        call = _run(
            check_reservation_availability,
            restaurant_name=state["restaurant"],
            date=state["date"],
            party_size=party,
        )
        booked = "has availability" in call["output"]
        return {
            "state": dict(START),
            "tools": [call],
            "reply": (
                f"Good news, {state['restaurant']} has a table for {party} on {state['date']}."
                if booked
                else f"Sorry, {state['restaurant']} is fully booked on {state['date']}."
            ),
            "notice": (
                "Good news, that table is available! Want to look for another?"
                if booked
                else "Sorry, that table isn't available. Let's start over."
            ),
        }

    return {"state": dict(START), "tools": [], "reply": OTHER_REPLY, "notice": None}
