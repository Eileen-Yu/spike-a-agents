"""Order-status agent built with Google ADK, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Uses OpenAI through LiteLLM so every sample needs the same key: OPENAI_API_KEY.
Run: uv run main.py
"""

import os

import uvicorn
from fastapi import FastAPI
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
APP_NAME = "order_agent"


def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id."""
    return f"Order {order_id}: shipped, arriving Friday."


agent = Agent(
    name="order_agent",
    model=LiteLlm(model=f"openai/{MODEL}"),
    instruction="You are a customer support agent. Use your tools to answer questions about orders.",
    tools=[get_order_status],
)
sessions = InMemorySessionService()
runner = Runner(agent=agent, app_name=APP_NAME, session_service=sessions)


async def ask(prompt: str) -> str:
    session = await sessions.create_session(app_name=APP_NAME, user_id="user")
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    answer = ""
    async for event in runner.run_async(user_id="user", session_id=session.id, new_message=message):
        if event.is_final_response() and event.content and event.content.parts:
            answer = "".join(part.text or "" for part in event.content.parts)
    return answer


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
