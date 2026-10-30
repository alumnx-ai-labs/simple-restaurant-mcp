"""Unit tests for tools.py: plain Python, no MCP involved."""

import tools


def test_search_is_case_insensitive():
    names = {r["name"] for r in tools.search_restaurants_by_cuisine("  indian ")}
    assert names == {"Spice Palace", "Curry House", "Taj Flavors"}


def test_unknown_cuisine_returns_empty_list():
    assert tools.search_restaurants_by_cuisine("Martian") == []


def test_details_and_not_found():
    assert tools.get_restaurant_details("spice palace")["cuisine"] == "Indian"
    assert "error" in tools.get_restaurant_details("Nope")


def test_availability():
    ok = tools.check_reservation_availability("Spice Palace", "2024-11-15", 2)
    full = tools.check_reservation_availability("Spice Palace", "2024-11-16", 2)
    assert "has availability" in ok
    assert "fully booked" in full


def test_availability_edge_cases():
    assert "not found" in tools.check_reservation_availability("Nope", "2024-11-15", 2)
    assert "No availability data" in tools.check_reservation_availability("Spice Palace", "2030-01-01", 2)
    assert "at least 1" in tools.check_reservation_availability("Spice Palace", "2024-11-15", 0)


def test_every_restaurant_has_one_availability_flag_per_date():
    for name, r in tools.RESTAURANTS.items():
        assert len(r["available"]) == len(tools.DATES), name


def test_specialities():
    by_cuisine = tools.get_specialities("Italian")["dishes"]
    assert "Lasagna" in by_cuisine and "Biryani" not in by_cuisine
    assert set(tools.get_specialities("Biryani")["dishes"]["Biryani"]) == {"Spice Palace", "Taj Flavors"}
    assert "Margherita Pizza" in tools.get_specialities("pizza")["dishes"]
    assert "error" in tools.get_specialities("zzz")
