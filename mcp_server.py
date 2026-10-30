"""A small restaurant MCP server, meant for learning how MCP works.

It exposes the three things an MCP server can offer:
  * tools     - functions the AI can call           (@mcp.tool)
  * resources - read-only data the AI can load      (@mcp.resource)
  * prompts   - reusable prompt templates           (@mcp.prompt)

Run over stdio (default, what MCP clients launch):  python mcp_server.py
Run over HTTP (for remote clients):                 python mcp_server.py --http

stdio uses stdout for the protocol, so never print() in here; log to stderr.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")  # optional: only sets MCP_HOST / MCP_PORT
sys.path.insert(0, str(HERE))  # so `import tools` works from any launch directory

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

import tools

mcp = MCPServer(
    "restaurant",
    instructions=(
        "Restaurant assistant. Find restaurants by cuisine, look up their details and "
        "specialities, and check table availability. Supported cuisines: "
        f"{', '.join(tools.CUISINES)}. Availability covers {tools.DATES[0]} to {tools.DATES[-1]}."
    ),
)

# Tools only read data, so tell the client that (it can skip confirmation prompts).
READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


# --- Tools: the docstring and type hints become the description and schema the AI sees ---

@mcp.tool(annotations=READ_ONLY)
def search_restaurants_by_cuisine(cuisine_type: str) -> list[dict]:
    """Search for restaurants by cuisine type. Supported cuisines: Chinese, Indian, Italian, Mexican."""
    return tools.search_restaurants_by_cuisine(cuisine_type)


@mcp.tool(annotations=READ_ONLY)
def get_restaurant_details(restaurant_name: str) -> dict:
    """Get a restaurant's address, phone, hours and specialities."""
    return tools.get_restaurant_details(restaurant_name)


@mcp.tool(annotations=READ_ONLY)
def check_reservation_availability(restaurant_name: str, date: str, party_size: int) -> str:
    """Check if a restaurant has a table on a date (YYYY-MM-DD) for a party size."""
    return tools.check_reservation_availability(restaurant_name, date, party_size)


@mcp.tool(annotations=READ_ONLY)
def get_specialities(query: str = "") -> dict:
    """Signature dishes and the restaurants serving them. `query` can be a cuisine, a dish name, or empty for all."""
    return tools.get_specialities(query)


@mcp.tool(annotations=READ_ONLY)
def health() -> dict:
    """Report that the server is up."""
    return {"status": "ok"}


# --- Resource: data the client can read by URI, without the AI calling a function ---

@mcp.resource("restaurants://all")
def all_restaurants() -> dict:
    """Every restaurant with its full details."""
    return {name: tools.get_restaurant_details(name) for name in tools.RESTAURANTS}


# --- Prompt: a template the user picks (e.g. a slash command in the client) ---

@mcp.prompt()
def book_a_table(cuisine: str, date: str, party_size: int) -> str:
    """Guide the AI through finding and checking a table."""
    return (
        f"I want a table for {party_size} on {date} serving {cuisine} food. "
        "Search restaurants for that cuisine, check availability for each one on that date, "
        "and recommend the best-rated restaurant that has a table. "
        "If none do, say so and suggest another cuisine."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Restaurant MCP server")
    parser.add_argument("--http", action="store_true", help="serve over streamable HTTP instead of stdio")
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8080")))
    args = parser.parse_args()

    if args.http:
        mcp.run("streamable-http", host=args.host, port=args.port)  # endpoint: /mcp
    else:
        mcp.run()  # stdio


if __name__ == "__main__":
    main()
