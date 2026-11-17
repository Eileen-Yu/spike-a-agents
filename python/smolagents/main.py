"""Order-status agent built with smolagents, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import asyncio
import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id.

    Args:
        order_id: The order id.
    """
    return f"Order {order_id}: shipped, arriving Friday."


model = OpenAIServerModel(model_id=MODEL)


def ask_sync(prompt: str) -> str:
    # An agent holds its run's memory, so each request gets its own.
    agent = ToolCallingAgent(
        model=model,
        tools=[get_order_status],
        instructions="You are a customer support agent. Use your tools to answer questions about orders.",
    )
    return str(agent.run(prompt))


async def ask(prompt: str) -> str:
    return await asyncio.to_thread(ask_sync, prompt)


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
