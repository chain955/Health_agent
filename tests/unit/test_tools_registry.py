"""Unit tests for tool registry — registration, get, list, JSON shape."""

from __future__ import annotations

import json

import pytest
from pydantic import BaseModel

from app.tools.base import ToolContext, ToolSpec
from app.tools.registry import ToolRegistry


class _EchoInput(BaseModel):
    text: str


class _EchoOutput(BaseModel):
    echoed: str


class _EchoTool:
    spec = ToolSpec(
        name="echo",
        description="Echo input text back.",
        input_schema=_EchoInput,
        output_schema=_EchoOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = _EchoInput.model_validate(params.model_dump())
        return _EchoOutput(echoed=inp.text)


class _AnotherInput(BaseModel):
    n: int


class _AnotherOutput(BaseModel):
    doubled: int


class _AnotherTool:
    spec = ToolSpec(
        name="double",
        description="Double the given number.",
        input_schema=_AnotherInput,
        output_schema=_AnotherOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = _AnotherInput.model_validate(params.model_dump())
        return _AnotherOutput(doubled=inp.n * 2)


def test_register_and_get() -> None:
    reg = ToolRegistry()
    tool = _EchoTool()
    reg.register(tool)
    assert reg.get("echo") is tool


def test_get_unknown_raises() -> None:
    reg = ToolRegistry()
    with pytest.raises(KeyError, match="tool not found"):
        reg.get("nonexistent")


def test_list_returns_specs() -> None:
    reg = ToolRegistry()
    reg.register(_EchoTool())
    reg.register(_AnotherTool())
    specs = reg.list()
    assert len(specs) == 2
    names = {s.name for s in specs}
    assert names == {"echo", "double"}


def test_all_tool_jsons_shape() -> None:
    reg = ToolRegistry()
    reg.register(_EchoTool())
    reg.register(_AnotherTool())

    jsons = reg.all_tool_jsons()
    assert len(jsons) == 2

    for item in jsons:
        assert item["type"] == "function"
        func_desc = item["function"]
        assert "name" in func_desc
        assert "description" in func_desc
        assert "parameters" in func_desc

        params_schema = func_desc["parameters"]
        raw = json.dumps(params_schema)
        parsed = json.loads(raw)
        assert "properties" in parsed
        assert "type" in parsed


def test_version_increments_on_register() -> None:
    reg = ToolRegistry()
    assert reg.version == 0
    reg.register(_EchoTool())
    assert reg.version == 1
    reg.register(_AnotherTool())
    assert reg.version == 2


def test_default_registry_has_builtin_tools() -> None:
    from app.tools.registry import default_registry

    specs = default_registry.list()
    names = {s.name for s in specs}
    expected = {
        "get_user_profile",
        "get_recent_workouts",
        "get_workout",
        "get_daily_metrics",
        "get_metrics_range",
        "get_period_summary",
    }
    assert expected.issubset(names)
