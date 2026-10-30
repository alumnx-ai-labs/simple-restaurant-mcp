"""End-to-end MCP test: launch mcp_server.py as a subprocess and talk to it over stdio,
exactly as an MCP client (Claude Code, Claude Desktop, a LangChain agent) would."""

import json
import sys
from pathlib import Path

import anyio
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parent.parent / "mcp_server.py"

EXPECTED_TOOLS = {
    "search_restaurants_by_cuisine",
    "get_restaurant_details",
    "check_reservation_availability",
    "get_specialities",
    "chat_turn",
    "evaluate_restaurant_agent",
    "health",
}


async def _with_session(fn):
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await fn(session)


def _payload(result):
    """The tool result as Python data (structured output if present, else the text)."""
    assert not result.is_error, result
    if result.structured_content is not None:
        data = result.structured_content
        return data.get("result", data) if isinstance(data, dict) else data
    text = result.content[0].text
    try:
        return json.loads(text)
    except ValueError:
        return text


def run(fn):
    return anyio.run(_with_session, fn)


def test_lists_all_tools_with_schemas():
    async def go(session):
        return (await session.list_tools()).tools

    tools = run(go)
    assert {t.name for t in tools} == EXPECTED_TOOLS
    for t in tools:
        assert t.description, f"{t.name} has no description"
        assert t.input_schema["type"] == "object"


def test_health():
    async def go(session):
        return _payload(await session.call_tool("health", {}))

    assert run(go) == {"status": "ok"}


def test_search_and_details():
    async def go(session):
        found = _payload(await session.call_tool("search_restaurants_by_cuisine", {"cuisine_type": "Indian"}))
        details = _payload(await session.call_tool("get_restaurant_details", {"restaurant_name": "Spice Palace"}))
        return found, details

    found, details = run(go)
    assert {r["name"] for r in found} == {"Spice Palace", "Curry House", "Taj Flavors"}
    assert details["cuisine"] == "Indian"


def test_unknown_cuisine_returns_empty_list():
    async def go(session):
        return _payload(await session.call_tool("search_restaurants_by_cuisine", {"cuisine_type": "Martian"}))

    assert run(go) == []


def test_availability_true_and_false():
    async def go(session):
        args = {"restaurant_name": "Spice Palace", "party_size": 2}
        ok = _payload(await session.call_tool("check_reservation_availability", {**args, "date": "2024-11-15"}))
        full = _payload(await session.call_tool("check_reservation_availability", {**args, "date": "2024-11-16"}))
        return ok, full

    ok, full = run(go)
    assert "has availability" in ok
    assert "fully booked" in full


def test_unknown_restaurant_is_handled():
    async def go(session):
        return _payload(await session.call_tool("get_restaurant_details", {"restaurant_name": "Nope"}))

    assert "error" in run(go)


def test_bad_arguments_are_rejected():
    async def go(session):
        # party_size must be an integer
        return await session.call_tool(
            "check_reservation_availability",
            {"restaurant_name": "Spice Palace", "date": "2024-11-15", "party_size": "many"},
        )

    try:
        result = run(go)
    except Exception:
        return  # a protocol-level error is also an acceptable rejection
    assert result.is_error


def test_specialities():
    async def go(session):
        return _payload(await session.call_tool("get_specialities", {"query": "Biryani"}))

    assert run(go)["matched_dish"] == "Biryani"


def test_chat_turn_walks_the_booking_flow():
    """Exact button labels take the deterministic path, so no LLM key is needed."""

    async def go(session):
        state, replies = None, []
        for say in ["Indian", "Spice Palace", "2024-11-15", "2 people"]:
            out = _payload(await session.call_tool("chat_turn", {"message": say, "state": state}))
            state = out["state"]
            replies.append(out["jev"])
        return state, replies

    state, replies = run(go)
    assert [r["tool_calls"][0]["name"] if r["tool_calls"] else None for r in replies] == [
        "search_restaurants_by_cuisine",
        "get_restaurant_details",
        None,
        "check_reservation_availability",
    ]
    assert "has availability" in replies[-1]["tool_calls"][0]["output"]
    assert state == {"asking": "cuisine"}
