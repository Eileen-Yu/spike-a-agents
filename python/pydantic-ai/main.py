"""Order-status agent built with Pydantic AI, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

agent = Agent(
    f"openai:{MODEL}",
    instructions="You are a customer support agent. Use your tools to answer questions about orders.",
)


@agent.tool_plain
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id."""
    return f"Order {order_id}: shipped, arriving Friday."


async def ask(prompt: str) -> str:
    result = await agent.run(prompt)
    return result.output


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
