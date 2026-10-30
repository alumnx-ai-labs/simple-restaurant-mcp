from langchain_core.tools import tool

# ============================================================
# TOOL 1: Search Restaurants by Cuisine
# ============================================================

@tool
def search_restaurants_by_cuisine(cuisine_type: str) -> list:
    """
    Search for restaurants by cuisine type.
    Supported cuisines: Indian, Italian, Chinese, Mexican.
    """

    restaurants = {
        "indian": [
            {"name": "Spice Palace", "rating": 4.5, "price": "₹₹"},
            {"name": "Curry House", "rating": 4.3, "price": "₹₹"},
            {"name": "Taj Flavors", "rating": 4.7, "price": "₹₹₹"}
        ],
        "italian": [
            {"name": "Pizza Bella", "rating": 4.4, "price": "₹₹"},
            {"name": "Pasta Dreams", "rating": 4.6, "price": "₹₹₹"},
            {"name": "Roma Kitchen", "rating": 4.2, "price": "₹₹"}
        ],
        "chinese": [
            {"name": "Dragon House", "rating": 4.5, "price": "₹₹"},
            {"name": "Ming's Kitchen", "rating": 4.3, "price": "₹₹"},
            {"name": "Golden Wok", "rating": 4.8, "price": "₹₹₹"}
        ],
        "mexican": [
            {"name": "Taco Fiesta", "rating": 4.4, "price": "₹₹"},
            {"name": "Salsa Nights", "rating": 4.6, "price": "₹₹₹"},
            {"name": "Burrito House", "rating": 4.2, "price": "₹₹"}
        ]
    }

    cuisine_lower = cuisine_type.lower().strip()

    return restaurants.get(cuisine_lower, [])


# ============================================================
# TOOL 2: Get Restaurant Details
# ============================================================

@tool
def get_restaurant_details(restaurant_name: str) -> dict:
    """
    Get detailed information about a restaurant,
    including address, phone, hours and specialties.
    """

    details = {
        "Spice Palace": {
            "cuisine": "Indian",
            "rating": 4.5,
            "address": "123 Food Street, City Center",
            "phone": "9876543210",
            "hours": "11 AM - 11 PM",
            "speciality": "Butter Chicken, Biryani"
        },

        "Pizza Bella": {
            "cuisine": "Italian",
            "rating": 4.4,
            "address": "456 Dine Avenue, Downtown",
            "phone": "9123456789",
            "hours": "12 PM - 10:30 PM",
            "speciality": "Margherita Pizza, Tiramisu"
        },

        "Dragon House": {
            "cuisine": "Chinese",
            "rating": 4.5,
            "address": "789 Noodle Lane, Market Area",
            "phone": "9111222333",
            "hours": "11:30 AM - 11 PM",
            "speciality": "Hakka Noodles, Fried Rice"
        },

        "Taco Fiesta": {
            "cuisine": "Mexican",
            "rating": 4.4,
            "address": "321 Spice Row, Hip District",
            "phone": "9222333444",
            "hours": "1 PM - 12 AM",
            "speciality": "Fish Tacos, Guacamole"
        },

        "Curry House": {
            "cuisine": "Indian",
            "rating": 4.3,
            "address": "555 Flavor Street, Old Town",
            "phone": "9333444555",
            "hours": "11 AM - 10 PM",
            "speciality": "Paneer Tikka, Dal Makhani"
        },

        "Taj Flavors": {
            "cuisine": "Indian",
            "rating": 4.7,
            "address": "999 Taste Lane, Premium Zone",
            "phone": "9444555666",
            "hours": "12 PM - 11 PM",
            "speciality": "Biryani, Tandoori Chicken"
        },

        "Golden Wok": {
            "cuisine": "Chinese",
            "rating": 4.8,
            "address": "777 Wok Street, Central Market",
            "phone": "9555666777",
            "hours": "11 AM - 11 PM",
            "speciality": "Szechuan Noodles, Dim Sum"
        },

        "Pasta Dreams": {
            "cuisine": "Italian",
            "rating": 4.6,
            "address": "12 Olive Road, Riverside",
            "phone": "9666777888",
            "hours": "12 PM - 11 PM",
            "speciality": "Truffle Pasta, Lasagna"
        },

        "Roma Kitchen": {
            "cuisine": "Italian",
            "rating": 4.2,
            "address": "34 Piazza Lane, Old Town",
            "phone": "9777888999",
            "hours": "11:30 AM - 10:30 PM",
            "speciality": "Risotto, Wood-fired Pizza"
        },

        "Ming's Kitchen": {
            "cuisine": "Chinese",
            "rating": 4.3,
            "address": "56 Lantern Street, Chinatown",
            "phone": "9888999000",
            "hours": "12 PM - 11 PM",
            "speciality": "Manchurian, Hot and Sour Soup"
        },

        "Salsa Nights": {
            "cuisine": "Mexican",
            "rating": 4.6,
            "address": "78 Fiesta Avenue, Hip District",
            "phone": "9999000111",
            "hours": "2 PM - 12:30 AM",
            "speciality": "Enchiladas, Churros"
        },

        "Burrito House": {
            "cuisine": "Mexican",
            "rating": 4.2,
            "address": "90 Cantina Road, Market Area",
            "phone": "9000111222",
            "hours": "11 AM - 10 PM",
            "speciality": "Loaded Burritos, Nachos"
        }
    }

    return details.get(
        restaurant_name.strip(),
        {"error": f"Restaurant '{restaurant_name}' not found"}
    )


# ============================================================
# TOOL 3: Check Reservation Availability
# ============================================================

@tool
def check_reservation_availability(
    restaurant_name: str,
    date: str,
    party_size: int
) -> str:
    """
    Check if a restaurant has reservation availability
    for a specific date and number of people.
    """

    available_slots = {
        "Spice Palace": {
            "2024-11-15": True,
            "2024-11-16": False,
            "2024-11-17": True
        },

        "Pizza Bella": {
            "2024-11-15": False,
            "2024-11-16": True,
            "2024-11-17": True
        },

        "Dragon House": {
            "2024-11-15": True,
            "2024-11-16": True,
            "2024-11-17": False
        },

        "Taco Fiesta": {
            "2024-11-15": True,
            "2024-11-16": True,
            "2024-11-17": True
        },

        "Curry House": {
            "2024-11-15": True,
            "2024-11-16": False,
            "2024-11-17": True
        },

        "Taj Flavors": {
            "2024-11-15": False,
            "2024-11-16": True,
            "2024-11-17": True
        },

        "Golden Wok": {
            "2024-11-15": True,
            "2024-11-16": False,
            "2024-11-17": True
        },

        "Pasta Dreams": {
            "2024-11-15": True,
            "2024-11-16": True,
            "2024-11-17": False
        },

        "Roma Kitchen": {
            "2024-11-15": False,
            "2024-11-16": True,
            "2024-11-17": True
        },

        "Ming's Kitchen": {
            "2024-11-15": True,
            "2024-11-16": True,
            "2024-11-17": True
        },

        "Salsa Nights": {
            "2024-11-15": False,
            "2024-11-16": False,
            "2024-11-17": True
        },

        "Burrito House": {
            "2024-11-15": True,
            "2024-11-16": True,
            "2024-11-17": False
        }
    }

    if restaurant_name not in available_slots:
        return f"Restaurant '{restaurant_name}' not found."

    is_available = available_slots[restaurant_name].get(
        date,
        False
    )

    if is_available:
        return (
            f"✓ {restaurant_name} has availability "
            f"for {party_size} people on {date}"
        )

    return (
        f"✗ {restaurant_name} is fully booked "
        f"for {date}"
    )


# ============================================================
# TOOL 4: Specialities (signature dishes and who serves them)
# ============================================================

SPECIALITY_CUISINES = ["Indian", "Italian", "Chinese", "Mexican"]


@tool
def get_specialities(query: str = "") -> dict:
    """
    Get the speciality (signature) dishes and the restaurants that serve them.
    `query` can be a cuisine (Indian, Italian, Chinese, Mexican) for that
    cuisine's special dishes, a dish name (e.g. Biryani) for that dish plus
    the other specialities of its cuisine, or empty for every cuisine.
    """

    q = query.strip().lower()

    # cuisine -> dish -> restaurants serving it, built from the restaurant data above
    catalogue = {}
    for cuisine in SPECIALITY_CUISINES:
        dishes = {}
        for r in search_restaurants_by_cuisine.invoke({"cuisine_type": cuisine}):
            info = get_restaurant_details.invoke({"restaurant_name": r["name"]})
            for dish in info["speciality"].split(","):
                dishes.setdefault(dish.strip(), []).append(
                    {**r, "address": info["address"], "hours": info["hours"]}
                )
        catalogue[cuisine] = dishes

    def brief(r):
        return {k: r[k] for k in ("name", "rating", "price")}

    def section(cuisine):
        return {
            "cuisine": cuisine,
            "dishes": [
                {"dish": d, "restaurants": [brief(r) for r in rs]}
                for d, rs in catalogue[cuisine].items()
            ],
        }

    if not q:
        return {"query": "", "matched_dish": None,
                "cuisines": [section(c) for c in SPECIALITY_CUISINES]}

    for cuisine in SPECIALITY_CUISINES:
        if q == cuisine.lower():
            return {"query": query, "matched_dish": None, "cuisines": [section(cuisine)]}

    # A single dish: only that dish, with full details of the restaurants serving it.
    # An exact name wins; otherwise every dish whose name contains the query (e.g. "pizza").
    def dish_hits(match):
        return [
            {
                "cuisine": cuisine,
                "dishes": [{"dish": d, "restaurants": rs}],
            }
            for cuisine, dishes in catalogue.items()
            for d, rs in dishes.items()
            if match(d.lower())
        ]

    hits = dish_hits(lambda d: d == q) or dish_hits(lambda d: q in d)
    if hits:
        return {
            "query": query,
            "matched_dish": hits[0]["dishes"][0]["dish"],
            "cuisines": hits,
        }

    return {"error": f"No cuisine or dish matching '{query}' found"}


tools = [
    search_restaurants_by_cuisine,
    get_restaurant_details,
    check_reservation_availability,
    get_specialities,
]
