"""Order-status agent built with Deep Agents, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import os

import uvicorn
from deepagents import create_deep_agent
from fastapi import FastAPI
from langchain_core.tools import tool
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id."""
    return f"Order {order_id}: shipped, arriving Friday."


agent = create_deep_agent(
    model=f"openai:{MODEL}",
    tools=[get_order_status],
    system_prompt="You are a customer support agent. Use your tools to answer questions about orders.",
)


async def ask(prompt: str) -> str:
    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    return result["messages"][-1].content


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
