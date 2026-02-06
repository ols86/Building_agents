from pydantic import BaseModel
from typing import Optional, Union, List, Dict, Any, Literal


class BaseMessage(BaseModel):
    content: Optional[str] = "" # content is a variable that can hold the text of the message, but it’s optional and defaults to an empty string if not provided.
    # so when we must write content = "<add content >"

    def dict(self) -> Dict:
        return dict(self)


class SystemMessage(BaseMessage):
    role: Literal["system"] = "system" # role is a variable that is defined as a literal string "system". This means that any instance of SystemMessage will have its role attribute set to "system" and cannot be changed to anything else. This is useful for distinguishing system messages from other types of messages in the application.


class UserMessage(BaseMessage):
    role: Literal["user"] = "user"


class ToolMessage(BaseMessage):
    role: Literal["tool"] = "tool"
    tool_call_id: str
    name: str


class AIMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"
    tool_calls: Optional[List[Any]] = None


AnyMessage = Union[
    SystemMessage,
    UserMessage,
    AIMessage,
    ToolMessage,
]
