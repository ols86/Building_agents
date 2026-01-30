from typing import List, Optional, Dict, Any
import os
from openai import OpenAI
from lib.messages import (
    AnyMessage,
    AIMessage,
    BaseMessage,
    UserMessage,
)
from lib.tooling import Tool


class LLM:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        tools: Optional[List[Tool]] = None,
        api_key: Optional[str] = None
    ):
        self.model = model
        self.temperature = temperature

        openai_api_key = api_key or os.getenv("OPENAI_API_KEY")

        self.client = OpenAI(
            base_url = "https://openai.vocareum.com/v1",
            api_key=openai_api_key
            ) # if api_key else OpenAI()
        self.tools: Dict[str, Tool] = {
            tool.name: tool for tool in (tools or [])
        }

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool # Add tools after construction to attribute tools which is a list

    def _build_payload(self, messages: List[BaseMessage]) -> Dict[str, Any]: # _build_payload use _ to show intenral method (note does not stop it being used as python does not have pub and private func)
        """
        Builds the request payload for chat.completions.create.
        Messages must be a list of dicts, so it converts each BaseMessage via .dict()
        """
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [m.dict() for m in messages],
        }

        if self.tools: # If self.tools == {} empty → False → skip tool section
            payload["tools"] = [tool.dict() for tool in self.tools.values()]
            payload["tool_choice"] = "auto"

        return payload

    def _convert_input(self, input: Any) -> List[BaseMessage]:
        if isinstance(input, str):
            return [UserMessage(content=input)]
        elif isinstance(input, BaseMessage):
            return [input]
        elif isinstance(input, list) and all(isinstance(m, BaseMessage) for m in input):
            return input
        else:
            raise ValueError(f"Invalid input type {type(input)}.")

    def invoke(self, input: str | BaseMessage | List[BaseMessage]) -> AIMessage:
        messages = self._convert_input(input)
        payload = self._build_payload(messages)
        response = self.client.chat.completions.create(**payload)
        choice = response.choices[0]
        message = choice.message

        return AIMessage( # creates a new AIMessage instnace and validate the inputs align
            content=message.content,
            tool_calls=message.tool_calls
        )
