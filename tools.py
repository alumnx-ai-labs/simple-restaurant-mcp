"""Restaurant data and the plain Python functions behind the MCP tools.

Nothing here knows about MCP, so you can read and test it like any normal module.
mcp_server.py is the thin layer that exposes these functions to an MCP client.
"""

DATES = ("2024-11-15", "2024-11-16", "2024-11-17")  # the days we have availability for

# name -> details. `available` lines up with DATES (True = tables free that day).
RESTAURANTS = {
    "Spice Palace": {
        "cuisine": "Indian", "rating": 4.5, "price": "₹₹",
        "address": "123 Food Street, City Center", "phone": "9876543210", "hours": "11 AM - 11 PM",
        "specialities": ["Butter Chicken", "Biryani"], "available": (True, False, True),
    },
    "Curry House": {
        "cuisine": "Indian", "rating": 4.3, "price": "₹₹",
        "address": "555 Flavor Street, Old Town", "phone": "9333444555", "hours": "11 AM - 10 PM",
        "specialities": ["Paneer Tikka", "Dal Makhani"], "available": (True, False, True),
    },
    "Taj Flavors": {
        "cuisine": "Indian", "rating": 4.7, "price": "₹₹₹",
        "address": "999 Taste Lane, Premium Zone", "phone": "9444555666", "hours": "12 PM - 11 PM",
        "specialities": ["Biryani", "Tandoori Chicken"], "available": (False, True, True),
    },
    "Pizza Bella": {
        "cuisine": "Italian", "rating": 4.4, "price": "₹₹",
        "address": "456 Dine Avenue, Downtown", "phone": "9123456789", "hours": "12 PM - 10:30 PM",
        "specialities": ["Margherita Pizza", "Tiramisu"], "available": (False, True, True),
    },
    "Pasta Dreams": {
        "cuisine": "Italian", "rating": 4.6, "price": "₹₹₹",
        "address": "12 Olive Road, Riverside", "phone": "9666777888", "hours": "12 PM - 11 PM",
        "specialities": ["Truffle Pasta", "Lasagna"], "available": (True, True, False),
    },
    "Roma Kitchen": {
        "cuisine": "Italian", "rating": 4.2, "price": "₹₹",
        "address": "34 Piazza Lane, Old Town", "phone": "9777888999", "hours": "11:30 AM - 10:30 PM",
        "specialities": ["Risotto", "Wood-fired Pizza"], "available": (False, True, True),
    },
    "Dragon House": {
        "cuisine": "Chinese", "rating": 4.5, "price": "₹₹",
        "address": "789 Noodle Lane, Market Area", "phone": "9111222333", "hours": "11:30 AM - 11 PM",
        "specialities": ["Hakka Noodles", "Fried Rice"], "available": (True, True, False),
    },
    "Ming's Kitchen": {
        "cuisine": "Chinese", "rating": 4.3, "price": "₹₹",
        "address": "56 Lantern Street, Chinatown", "phone": "9888999000", "hours": "12 PM - 11 PM",
        "specialities": ["Manchurian", "Hot and Sour Soup"], "available": (True, True, True),
    },
    "Golden Wok": {
        "cuisine": "Chinese", "rating": 4.8, "price": "₹₹₹",
        "address": "777 Wok Street, Central Market", "phone": "9555666777", "hours": "11 AM - 11 PM",
        "specialities": ["Szechuan Noodles", "Dim Sum"], "available": (True, False, True),
    },
    "Taco Fiesta": {
        "cuisine": "Mexican", "rating": 4.4, "price": "₹₹",
        "address": "321 Spice Row, Hip District", "phone": "9222333444", "hours": "1 PM - 12 AM",
        "specialities": ["Fish Tacos", "Guacamole"], "available": (True, True, True),
    },
    "Salsa Nights": {
        "cuisine": "Mexican", "rating": 4.6, "price": "₹₹₹",
        "address": "78 Fiesta Avenue, Hip District", "phone": "9999000111", "hours": "2 PM - 12:30 AM",
        "specialities": ["Enchiladas", "Churros"], "available": (False, False, True),
    },
    "Burrito House": {
        "cuisine": "Mexican", "rating": 4.2, "price": "₹₹",
        "address": "90 Cantina Road, Market Area", "phone": "9000111222", "hours": "11 AM - 10 PM",
        "specialities": ["Loaded Burritos", "Nachos"], "available": (True, True, False),
    },
}

CUISINES = sorted({r["cuisine"] for r in RESTAURANTS.values()})


def _find(restaurant_name: str) -> tuple[str, dict] | None:
    """Look a restaurant up ignoring case and surrounding spaces."""
    wanted = restaurant_name.strip().lower()
    for name, info in RESTAURANTS.items():
        if name.lower() == wanted:
            return name, info
    return None


def search_restaurants_by_cuisine(cuisine_type: str) -> list[dict]:
    """Restaurants of a cuisine (name, rating, price). Unknown cuisine -> empty list."""
    wanted = cuisine_type.strip().lower()
    return [
        {"name": name, "rating": r["rating"], "price": r["price"]}
        for name, r in RESTAURANTS.items()
        if r["cuisine"].lower() == wanted
    ]


def get_restaurant_details(restaurant_name: str) -> dict:
    """Address, phone, hours and specialities, or {"error": ...} if not found."""
    found = _find(restaurant_name)
    if not found:
        return {"error": f"Restaurant '{restaurant_name}' not found"}
    name, r = found
    return {
        "name": name,
        **{k: r[k] for k in ("cuisine", "rating", "price", "address", "phone", "hours", "specialities")},
    }


def check_reservation_availability(restaurant_name: str, date: str, party_size: int) -> str:
    """Whether the restaurant has a table on `date` (YYYY-MM-DD) for `party_size` people."""
    found = _find(restaurant_name)
    if not found:
        return f"Restaurant '{restaurant_name}' not found."
    name, r = found
    if party_size < 1:
        return "party_size must be at least 1."
    if date not in DATES:
        return f"No availability data for {date}. We only cover {DATES[0]} to {DATES[-1]}."
    if r["available"][DATES.index(date)]:
        return f"{name} has availability for {party_size} people on {date}."
    return f"{name} is fully booked on {date}."


def get_specialities(query: str = "") -> dict:
    """Signature dishes and who serves them.

    `query` may be a cuisine (Indian), a dish name (Biryani, or part of one such as
    "pizza"), or empty for every dish.
    """
    q = query.strip().lower()
    dishes: dict[str, list[str]] = {}  # dish -> restaurants serving it
    for name, r in RESTAURANTS.items():
        cuisine_ok = not q or q == r["cuisine"].lower()
        for dish in r["specialities"]:
            if cuisine_ok or q in dish.lower():
                dishes.setdefault(dish, []).append(name)
    if not dishes:
        return {"error": f"No cuisine or dish matching '{query}' found"}
    return {"query": query, "dishes": dishes}
