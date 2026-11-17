"""Order-status agent built with the Claude Agent SDK, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs ANTHROPIC_API_KEY. Run: uv run main.py
"""

import os

import uvicorn
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, ResultMessage, create_sdk_mcp_server, tool
from fastapi import FastAPI
from pydantic import BaseModel


@tool("get_order_status", "Look up the shipping status of an order by its id", {"order_id": str})
async def get_order_status(args: dict) -> dict:
    text = f"Order {args['order_id']}: shipped, arriving Friday."
    return {"content": [{"type": "text", "text": text}]}


orders = create_sdk_mcp_server(name="orders", version="1.0.0", tools=[get_order_status])
options = ClaudeAgentOptions(
    system_prompt="You are a customer support agent. Use your tools to answer questions about orders.",
    model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
    mcp_servers={"orders": orders},
    allowed_tools=["mcp__orders__get_order_status"],
    max_turns=5,
)


async def ask(prompt: str) -> str:
    answer = ""
    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                answer = message.result or ""
    return answer


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
