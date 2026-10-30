# Restaurant MCP Server

A small, working [Model Context Protocol](https://modelcontextprotocol.io) server for learning how MCP works. Clone it, run it, connect it to an AI client, then read the ~100 lines in `mcp_server.py` to see how it's built.

**No API keys, no LLM, no Gemini needed.** An MCP server only *offers* tools; the AI client you connect (Claude, Cursor, ...) is what thinks and decides when to call them.

## What it exposes

MCP servers can offer three kinds of things. This one has all three:

| Kind | Name | What it does |
|---|---|---|
| Tool | `search_restaurants_by_cuisine` | Restaurants for Indian, Italian, Chinese or Mexican |
| Tool | `get_restaurant_details` | Address, phone, hours, specialities |
| Tool | `check_reservation_availability` | Table availability for a date (YYYY-MM-DD) and party size |
| Tool | `get_specialities` | Signature dishes and who serves them |
| Tool | `health` | Liveness check |
| Resource | `restaurants://all` | Every restaurant with full details |
| Prompt | `book_a_table` | Template that guides the AI through finding a table |

The data is made up and lives in `tools.py`. Availability only covers 2024-11-15 to 2024-11-17.

## Setup

Requires Python 3.10+.

```
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

`.env` is optional. Copy `.env.example` to `.env` only if you want to change the HTTP host/port.

## Run

- stdio (what MCP clients launch for you): `python mcp_server.py`
- HTTP, for remote clients: `python mcp_server.py --http` (endpoint: `http://127.0.0.1:8080/mcp`)

Running it by hand over stdio just sits there waiting for a client; that's normal.

## Try it

**MCP Inspector** (a web UI to call tools yourself, needs Node):
```
npx @modelcontextprotocol/inspector python mcp_server.py
```

**Claude Code:**
```
claude mcp add restaurant -- <path-to>/.venv/Scripts/python.exe <path-to>/mcp_server.py
```
Then ask: *"Find an Italian restaurant for 4 people on 2024-11-16."*

**Claude Desktop / Cursor** (add to their `mcpServers` JSON config):
```json
{ "mcpServers": { "restaurant": { "command": "<path-to>/.venv/Scripts/python.exe", "args": ["<path-to>/mcp_server.py"] } } }
```

## How it's organised

| File | Role |
|---|---|
| `tools.py` | The data and plain Python functions. No MCP in here. |
| `mcp_server.py` | Wraps those functions with `@mcp.tool`, `@mcp.resource`, `@mcp.prompt` and starts the server. |
| `tests/test_tools.py` | Unit tests for the functions. |
| `tests/test_mcp_server.py` | Starts the real server over stdio and calls it like a client would. |

Things to notice in `mcp_server.py`: the docstring and type hints become the tool description and input schema the AI sees; stdout belongs to the protocol in stdio mode, so logging goes to stderr.

## Test

```
pip install -r requirements-dev.txt
python -m pytest tests -q
```

## Exercises

1. Add a tool `get_top_rated(cuisine_type)`.
2. Add a `book_table` tool that records a booking (and think about why it shouldn't be marked read-only).
3. Add a resource template such as `restaurants://{name}`.
