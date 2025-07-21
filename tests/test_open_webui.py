import os
import sys

import pytest


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import open_webui


class DummyManus:
    async def run(self, message: str) -> str:
        return "dummy response"


class DummyMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class DummyMemory:
    def __init__(self, messages=None):
        self.messages = messages or []

    def get_recent_messages(self, n: int):
        return self.messages[-n:]


@pytest.mark.asyncio
async def test_respond(monkeypatch):
    monkeypatch.setattr(open_webui, "Manus", lambda: DummyManus())
    open_webui.session = None
    session = open_webui.get_session()
    result = await session.generate("hello")
    assert result == "dummy response"


@pytest.mark.asyncio
@pytest.mark.sit
async def test_integration(monkeypatch):
    monkeypatch.setattr(open_webui, "Manus", lambda: DummyManus())
    open_webui.session = None
    session = open_webui.get_session()
    result = await session.generate("test message")
    assert "dummy" in result


@pytest.mark.asyncio
@pytest.mark.uat
async def test_user_acceptance(monkeypatch):
    monkeypatch.setattr(open_webui, "Manus", lambda: DummyManus())
    open_webui.session = None
    session = open_webui.get_session()
    result = await session.generate("another message")
    assert result == "dummy response"


@pytest.mark.asyncio
async def test_generate_empty(monkeypatch):
    monkeypatch.setattr(open_webui, "Manus", lambda: DummyManus())
    open_webui.session = None
    session = open_webui.get_session()
    result = await session.generate("   ")
    assert result == "Please enter a valid message."


def test_recent_helpers(monkeypatch):
    def make_manus():
        manus = DummyManus()
        manus.memory = DummyMemory(
            [DummyMessage("user", "hi"), DummyMessage("assistant", "hey")]
        )
        return manus

    monkeypatch.setattr(open_webui, "Manus", make_manus)
    open_webui.session = None
    session = open_webui.get_session()
    session.logs = ["a", "b", "c"]
    assert session.get_recent_logs(2) == ["b", "c"]
    assert session.get_recent_thoughts(2) == ["user: hi", "assistant: hey"]
