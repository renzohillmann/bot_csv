from langgraph.prebuilt import create_react_agent
from langchain_openai import AzureChatOpenAI
from langchain_experimental.tools import PythonAstREPLTool
import os

def get_project_root():
    """Returns project root folder."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

def resolve_path(relative_path):
    """Resolves a path relative to the project root."""
    return os.path.join(get_project_root(), relative_path)

def create_csvsearch_agent(llm: AzureChatOpenAI, prompt: str):
    """Create a simple agent that can run Python code to query a CSV file."""
    return create_react_agent(llm, tools=[PythonAstREPLTool()], prompt=prompt)