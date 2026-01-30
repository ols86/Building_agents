# This file builds a Tool class that wraps a Python function and creates a JSON schema describing its parameters.

import inspect # introspection (look at function signatures, docstrings).
import datetime # used to map date/datetime types into JSON schema types.
from typing import (
    Callable, Any, get_type_hints, get_origin, get_args,
    Literal, Optional, Union, List, Dict
)
# Typing utilities:
# - Callable: function type
# get_type_hints: reads annotated types from a function
# get_origin, get_args: parse generics like List[str], Optional[int], Literal["a","b"]

from functools import wraps # preserves name/docstring when using decorators.


class Tool:
    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.func = func
        self.name = name or func.__name__ # Tool name defaults to the function name unless you override it by passing as part of the class
        self.description = description or inspect.getdoc(func) # use descrition passed by class or the doc string in the function if not avaiblable

        # Capture the function's call signature (parameter names, defaults, *args/**kwargs, and return type)
        # so we can inspect/validate how to call the tool and potentially build a schema for it.
        # eval_str=True resolves string type annotations (e.g. "int") into real types (int).
        self.signature = inspect.signature(func, eval_str=True)

        # def add(a: int, b: int) -> int:
        # print(get_type_hints(add))
        # output: {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
        self.type_hints = get_type_hints(func)

        self.parameters = [
            self._build_param_schema(key, param)
            for key, param in self.signature.parameters.items()
        ]

    def _build_param_schema(self, name: str, param: inspect.Parameter):
        param_type = self.type_hints.get(name, str)
        schema = self._infer_json_schema_type(param_type)
        return {
            "name": name,
            "schema": schema,
            "required": param.default == inspect.Parameter.empty
        }

    def _infer_json_schema_type(self, typ: Any) -> dict:
        origin = get_origin(typ)

        # Handle Literal (enums)
        if origin is Literal:
            return {
                "type": "string",
                "enum": list(get_args(typ))
            }

        # Handle Optional[T]
        if origin is Union:
            args = get_args(typ)
            non_none = [arg for arg in args if arg is not type(None)]
            if len(non_none) == 1:
                return self._infer_json_schema_type(non_none[0])
            return {"type": "string"}  # fallback

        # Handle collections
        if origin is list:
            return {
                "type": "array",
                "items": self._infer_json_schema_type(get_args(typ)[0] if get_args(typ) else str)
            }

        if origin is dict:
            return {
                "type": "object",
                "additionalProperties": self._infer_json_schema_type(get_args(typ)[1] if get_args(typ) else str)
            }

        # Primitive mappings
        mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            datetime.date: "string",
            datetime.datetime: "string",
        }

        return {"type": mapping.get(typ, "string")}

    def dict(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param["name"]: param["schema"]
                        for param in self.parameters
                    },
                    "required": [
                        param["name"] for param in self.parameters if param["required"]
                    ],
                    "additionalProperties": False
                }
            }
        }

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return f"<Tool name={self.name} params={[p['name'] for p in self.parameters]}>"

    @classmethod
    def from_func(cls, func: Callable):
        return cls(func)



def tool(func=None, *, name: str = None, description: str = None):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return Tool(f, name=name, description=description)
    
    # @tool ou @tool(name="foo")
    return wrapper(func) if func else wrapper