"""Order-status agent built with Strands Agents, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from strands import Agent, tool
from strands.models.openai import OpenAIModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM = "You are a customer support agent. Use your tools to answer questions about orders."


@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id.

    Args:
        order_id: The order id.
    """
    return f"Order {order_id}: shipped, arriving Friday."


model = OpenAIModel(model_id=MODEL)


async def ask(prompt: str) -> str:
    # A Strands Agent keeps its conversation, so each request gets its own.
    agent = Agent(model=model, tools=[get_order_status], system_prompt=SYSTEM, callback_handler=None)
    result = await agent.invoke_async(prompt)
    return str(result)


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
