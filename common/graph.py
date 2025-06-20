# graph.py
# -----------------------------------------------------------------------------
# Build a simple workflow with a single CSV search agent.
# -----------------------------------------------------------------------------

import os
import functools
import logging
from typing_extensions import TypedDict
from typing import Annotated, Sequence
import operator


from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END

from common.utils import create_csvsearch_agent
from common.prompts import CUSTOM_CHATBOT_PREFIX, CSV_AGENT_PROMPT_TEXT

logger = logging.getLogger(__name__)

os.environ["OPENAI_API_VERSION"] = os.environ.get("AZURE_OPENAI_API_VERSION", "")


class AgentState(TypedDict):
    """State that flows through the graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]


async def agent_node_async(state: AgentState, agent):
    result = await agent.ainvoke(state)
    last_ai_content = result["messages"][-1].content
    return {"messages": [AIMessage(content=last_ai_content)]}


def build_csv_workflow(csv_file_path: str = None):
    """Create a simple workflow that answers questions from a CSV file."""
    # Use a default path relative to project root if none provided
    if csv_file_path is None:
        # Get the project root directory (2 levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        botservice_dir = os.path.dirname(current_dir)
        csv_file_path = os.path.join(botservice_dir, "data", "all-states-history.csv")
        
    model_name = os.environ.get("GPT4o_DEPLOYMENT_NAME", "")
    llm = AzureChatOpenAI(
        deployment_name=model_name,
        temperature=0,
        max_tokens=2000,
        streaming=True,
    )

    csv_agent = create_csvsearch_agent(
        llm=llm,
        prompt=CUSTOM_CHATBOT_PREFIX + CSV_AGENT_PROMPT_TEXT.format(file_url=str(csv_file_path)),
    )

    workflow = StateGraph(AgentState)
    csv_node = functools.partial(agent_node_async, agent=csv_agent)
    workflow.add_node("CSVSearchAgent", csv_node)
    workflow.add_edge(START, "CSVSearchAgent")
    workflow.add_edge("CSVSearchAgent", END)

    return workflow
