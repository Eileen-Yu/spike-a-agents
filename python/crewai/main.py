"""Order-status agent built with CrewAI, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import os

import uvicorn
from crewai import Agent, Crew, Task
from crewai.tools import tool
from fastapi import FastAPI
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@tool("get_order_status")
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id."""
    return f"Order {order_id}: shipped, arriving Friday."


support = Agent(
    role="Customer support agent",
    goal="Answer customer questions about their orders accurately",
    backstory="You work on the support desk and look orders up before answering.",
    tools=[get_order_status],
    llm=MODEL,
)

answer_task = Task(
    description="Answer the customer's question: {question}",
    expected_output="A short, direct answer for the customer.",
    agent=support,
)

crew = Crew(agents=[support], tasks=[answer_task])


async def ask(prompt: str) -> str:
    result = await crew.kickoff_async(inputs={"question": prompt})
    return result.raw


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
