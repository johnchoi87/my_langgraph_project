from typing import TypedDict, Annotated, List

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import Field


class ServiceState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
    location: str = ""
    my_location: str = ""