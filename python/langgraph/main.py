"""Order-status agent built with LangGraph, served over HTTP.

POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
Needs OPENAI_API_KEY. Run: uv run main.py
"""

import os

import uvicorn
from fastapi import FastAPI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM = "You are a customer support agent. Use your tools to answer questions about orders."


@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id."""
    return f"Order {order_id}: shipped, arriving Friday."


tools = [get_order_status]
llm = ChatOpenAI(model=MODEL).bind_tools(tools)


def call_model(state: MessagesState) -> dict:
    return {"messages": [llm.invoke([SystemMessage(SYSTEM), *state["messages"]])]}


builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()


async def ask(prompt: str) -> str:
    result = await graph.ainvoke({"messages": [HumanMessage(prompt)]})
    return result["messages"][-1].content


app = FastAPI()


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run(req: RunRequest) -> dict:
    return {"answer": await ask(req.prompt)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
