"""Order-status agent with a hand-written tool loop and no agent framework.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import json
import os

import uvicorn
from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_STEPS = 8
SYSTEM = "You are a customer support agent. Use your tools to answer questions about orders."


def get_order_status(order_id: str) -> str:
    return f"Order {order_id}: shipped, arriving Friday."


TOOLS = {"get_order_status": get_order_status}
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up the shipping status of an order by its id.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    }
]

client = AsyncOpenAI()


async def ask(prompt: str) -> str:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
    for _ in range(MAX_STEPS):
        response = await client.chat.completions.create(model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content or ""
        messages.append(message.model_dump(exclude_none=True))
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return "Stopped: too many steps."


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
