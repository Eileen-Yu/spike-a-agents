"""Order-status agent built with the OpenAI Agents SDK, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import os

import uvicorn
from agents import Agent, Runner, function_tool
from fastapi import FastAPI
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@function_tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id."""
    return f"Order {order_id}: shipped, arriving Friday."


agent = Agent(
    name="Order agent",
    instructions="You are a customer support agent. Use your tools to answer questions about orders.",
    model=MODEL,
    tools=[get_order_status],
)


async def ask(prompt: str) -> str:
    result = await Runner.run(agent, prompt)
    return result.final_output


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
