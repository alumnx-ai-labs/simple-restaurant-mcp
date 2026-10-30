# Restaurant MCP Server

An MCP server for finding restaurants and booking a table.

## Tools
| Tool | What it does |
|---|---|
| `search_restaurants_by_cuisine` | Restaurants for Indian, Italian, Chinese or Mexican |
| `get_restaurant_details` | Address, phone, hours, specialities |
| `check_reservation_availability` | Availability for a date (YYYY-MM-DD) and party size |
| `get_specialities` | Signature dishes and who serves them |
| `chat_turn` | One step of the guided booking flow (pass back the returned `state`) |
| `evaluate_restaurant_agent` | Run the scripted evaluation scenarios |
| `health` | Liveness check |

## Setup
```
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
copy .env.example .env          # optional: only needed for free-text understanding
```

## Run
- stdio (what MCP clients launch): `python mcp_server.py`
- HTTP for remote agents: `python mcp_server.py --http --port 8080` (endpoint: `/mcp`)

## Connect a client
Claude Code:
```
claude mcp add restaurant -- <path-to>/.venv/Scripts/python.exe <path-to>/mcp_server.py
```
Claude Desktop / Cursor (`mcpServers` in their JSON config):
```json
{ "mcpServers": { "restaurant": { "command": "<path-to>/.venv/Scripts/python.exe", "args": ["<path-to>/mcp_server.py"] } } }
```

## Test
`python -m pytest tests -q` launches the server over stdio and exercises every tool.
Visual check: `npx @modelcontextprotocol/inspector python mcp_server.py`.
