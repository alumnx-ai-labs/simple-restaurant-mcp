"""Restaurant MCP server.

Run over stdio (default, what MCP clients launch):  python mcp_server.py
Run over HTTP for remote agents:                    python mcp_server.py --http [--port 8080]

stdio uses stdout for the protocol, so nothing in this process may print to it;
logging goes to stderr.
"""

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Work from any launch directory: find .env and the sibling modules next to this file.
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

import tools
from agent import ChatRequest, run_turn
from evaluation import evaluate_agent

mcp = MCPServer(
    "restaurant",
    instructions=(
        "Restaurant assistant. Use search_restaurants_by_cuisine, get_restaurant_details, "
        "check_reservation_availability and get_specialities for direct lookups. Use chat_turn "
        "to run the guided booking conversation (pass back the returned `state` each turn). "
        "Supported cuisines: Indian, Italian, Chinese, Mexican. Availability data covers "
        "2024-11-15 to 2024-11-17."
    ),
)

READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


@mcp.tool(annotations=READ_ONLY)
def search_restaurants_by_cuisine(cuisine_type: str) -> list[dict]:
    """Search for restaurants by cuisine type. Supported cuisines: Indian, Italian, Chinese, Mexican."""
    return tools.search_restaurants_by_cuisine.invoke({"cuisine_type": cuisine_type})


@mcp.tool(annotations=READ_ONLY)
def get_restaurant_details(restaurant_name: str) -> dict:
    """Get detailed information about a restaurant, including address, phone, hours and specialties."""
    return tools.get_restaurant_details.invoke({"restaurant_name": restaurant_name})


@mcp.tool(annotations=READ_ONLY)
def check_reservation_availability(restaurant_name: str, date: str, party_size: int) -> str:
    """Check if a restaurant has reservation availability for a date (YYYY-MM-DD) and party size."""
    return tools.check_reservation_availability.invoke(
        {"restaurant_name": restaurant_name, "date": date, "party_size": party_size}
    )


@mcp.tool(annotations=READ_ONLY)
def get_specialities(query: str = "") -> dict:
    """Get speciality dishes and the restaurants serving them. `query` may be a cuisine, a dish name, or empty for all."""
    return tools.get_specialities.invoke({"query": query})


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def chat_turn(message: str, history: list[dict] | None = None, state: dict | None = None) -> dict:
    """Run one turn of the guided booking conversation (cuisine -> restaurant -> date -> party size).

    `message` is the user's answer or a free-text question. `history` is a list of
    {"role", "content"} messages. Pass back the `state` returned by the previous call
    (omit it to start a new conversation). Returns {"jev": {...reply, tool_calls,
    next_question...}, "state": {...}}.
    """
    req = ChatRequest(message=message, history=history or [], state=state)
    return (await run_turn(req)).model_dump()


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
async def evaluate_restaurant_agent(use_judge: bool = False, scenarios: list[str] | None = None) -> dict:
    """Run the scripted evaluation scenarios against the booking agent and return scores.

    Set `use_judge` to also grade replies with an LLM judge (needs a model API key).
    `scenarios` limits the run to the named scenarios.
    """
    return await evaluate_agent(use_judge=use_judge, names=scenarios)


@mcp.tool(annotations=READ_ONLY)
def health() -> dict:
    """Report that the restaurant MCP server is up."""
    return {"status": "ok"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Restaurant MCP server")
    parser.add_argument("--http", action="store_true", help="serve over streamable HTTP instead of stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    if args.http:
        mcp.run("streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()  # stdio transport


if __name__ == "__main__":
    main()
