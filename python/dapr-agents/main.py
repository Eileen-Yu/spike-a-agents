"""Order-status agent built with Dapr Agents, run on a local Dapr sidecar.

Dapr Agents has only DurableAgent, so this sample is already a workflow; what
it does not know about is Catalyst. It serves the framework's own entry point:
POST /agent/run {"task": "What's the status of order 42?"}

Needs OPENAI_API_KEY and `dapr init`. Run:
    dapr run --app-id order-agent --app-port 8000 --resources-path ./resources -- uv run main.py
"""

import os

from dapr_agents import DurableAgent, tool
from dapr_agents.agents.configs import AgentMemoryConfig, AgentStateConfig
from dapr_agents.llm import OpenAIChatClient
from dapr_agents.memory import ConversationDaprStateMemory
from dapr_agents.storage.daprstores.stateservice import StateStoreService
from dapr_agents.workflow.runners import AgentRunner

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its id."""
    return f"Order {order_id}: shipped, arriving Friday."


def main() -> None:
    agent = DurableAgent(
        name="OrderAgent",
        role="Customer support agent",
        instructions=["Use your tools to answer questions about orders."],
        tools=[get_order_status],
        llm=OpenAIChatClient(model=MODEL),
        memory=AgentMemoryConfig(store=ConversationDaprStateMemory(store_name="statestore")),
        state=AgentStateConfig(store=StateStoreService(store_name="statestore")),
    )
    runner = AgentRunner()
    try:
        runner.serve(agent, port=int(os.getenv("PORT", "8000")))
    finally:
        runner.shutdown()


if __name__ == "__main__":
    main()
