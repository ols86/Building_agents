# messages.py creates structured message objects that:
    # - enforce the role field to valid values,
    # - provide a consistent interface (content, dict()),
    # - support tool-calling message types.

from pydantic import BaseModel
from typing import Optional, Union, List, Dict, Any, Literal


# BaseMessage is a Pydantic model, then it lets you enforce types for all message classes that inherit from it.

class BaseMessage(BaseModel):
    # Creates the base structure for all messages.
    # content is optional, defaulting to "". Because it inherits from BaseModel, Pydantic will validate types.
    content: Optional[str] = ""

    def dict(self) -> Dict:
        #overiding Pydaatic dict() method
        return dict(self)


class SystemMessage(BaseMessage):
    role: Literal["system"] = "system" 
    # role: --> “this class has a field named role”
    # Literal["system"] = “the only allowed value is "system"”
    # = system is the defualt value when not set


class UserMessage(BaseMessage):
    role: Literal["user"] = "user"


class ToolMessage(BaseMessage):
    role: Literal["tool"] = "tool"
    tool_call_id: str # must be a string type but can be any value
    name: str


class AIMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"
    tool_calls: Optional[List[Any]] = None

    # Optional[...] --> it can be a value (in this case a list conatining anything or None)
    # So these are valid:
        #1) AIMessage(content="Hi", tool_calls=None)
        #2)  AIMessage(content="Calling tool...", tool_calls=[])
        #3)  AIMessage(content="Calling tool...", tool_calls=[
        #    {"id": "call_1", "type": "function", "function": {"name": "search", "arguments": "{}"}}
        # ])




AnyMessage = Union[ # Union means any of the valid message shape below are ok
    SystemMessage,
    UserMessage,
    AIMessage,
    ToolMessage,
]
