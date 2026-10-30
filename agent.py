"""The Jev agent turn, shared by the FastAPI app (main.py) and the MCP server (mcp_server.py)."""

from langsmith import traceable
from pydantic import BaseModel, Field

import flow
from jev_decision import safe_interpret_answer


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = Field(default_factory=list)
    state: dict | None = None  # echo back the `state` from the last response


class ChatResponse(BaseModel):
    # Jev is the agent: source, available, understood, reply, tool_calls, next_question
    jev: dict
    state: dict  # send this back with the next request


@traceable(name="Jev Agent Turn", run_type="chain")
async def run_turn(req: ChatRequest) -> ChatResponse:
    history = [m.model_dump() for m in req.history]
    state = req.state or dict(flow.START)

    # Jev reads the user's answer to the question it asked last turn.
    asked = flow.question_for(state)
    clicked = flow.match_label(asked, req.message)
    if clicked is not None:
        # An exact button click is unambiguous; Jev is only needed for free text.
        jev_result = {"choice": clicked, "confidence": 1.0, "available": True}
    else:
        jev_result = await safe_interpret_answer(
            {**asked, "intents": flow.INTENTS}, req.message, history
        )
    if clicked is not None:
        method = "button"
        choice = clicked
    elif jev_result["available"]:
        method = "jev"
        choice = jev_result["choice"]
    else:
        method = "fallback"
        choice = flow.match_label(asked, req.message)

    # The decision drives the tools and the reply; no other model is involved.
    advance = flow.step(state, choice)

    new_state = advance["state"]
    next_question = flow.question_for(new_state)
    if advance["notice"]:
        next_question["text"] = f"{advance['notice']} {next_question['text']}"

    return ChatResponse(
        jev={
            "source": "Jev",
            "available": jev_result["available"],
            "understood": {
                "question_id": asked["id"],
                "choice": choice,
                "confidence": jev_result["confidence"],
                "method": method,
            },
            "reply": advance["reply"],
            "tool_calls": advance["tools"],
            "next_question": next_question,
        },
        state=new_state,
    )
