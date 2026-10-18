from typing_extensions import TypedDict, List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated


class State(TypedDict):
    """
    Represent the structure of the state used in graph
    """
    messages: Annotated[List[AnyMessage], add_messages]