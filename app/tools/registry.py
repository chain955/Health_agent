"""Tool registry — collects Tool instances, exposes get/list/json (spec §5)."""

import builtins
from typing import Any

from app.tools.base import Tool, ToolSpec


class ToolRegistry:
    """In-process registry of available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._version: int = 0

    @property
    def version(self) -> int:
        return self._version

    def register(self, tool: Tool) -> None:
        self._tools[tool.spec.name] = tool
        self._version += 1

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError:
            raise KeyError(f"tool not found: {name}") from None

    def list(self) -> builtins.list[ToolSpec]:
        return [t.spec for t in self._tools.values()]

    def all_tool_jsons(self) -> builtins.list[dict[str, Any]]:
        """OpenAI-style tool descriptions (name + description + parameters JSON Schema)."""
        out: builtins.list[dict[str, Any]] = []
        for tool in self._tools.values():
            spec = tool.spec
            out.append(
                {
                    "type": "function",
                    "function": {
                        "name": spec.name,
                        "description": spec.description,
                        "parameters": spec.input_schema.model_json_schema(),
                    },
                }
            )
        return out


default_registry = ToolRegistry()
