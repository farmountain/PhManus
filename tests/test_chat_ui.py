import os
import sys

import pytest


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import chat_ui


class DummyManus:
    async def run(self, message: str) -> str:
        return "dummy response"


@pytest.mark.asyncio
async def test_respond(monkeypatch):
    monkeypatch.setattr(chat_ui, "Manus", lambda: DummyManus())
    chat_ui.session = None
    session = chat_ui.get_session()
    result = await session.generate("hello")
    assert result == "dummy response"


@pytest.mark.asyncio
@pytest.mark.sit
async def test_integration(monkeypatch):
    monkeypatch.setattr(chat_ui, "Manus", lambda: DummyManus())
    chat_ui.session = None
    session = chat_ui.get_session()
    result = await session.generate("test message")
    assert "dummy" in result


@pytest.mark.asyncio
@pytest.mark.uat
async def test_user_acceptance(monkeypatch):
    monkeypatch.setattr(chat_ui, "Manus", lambda: DummyManus())
    chat_ui.session = None
    session = chat_ui.get_session()
    result = await session.generate("another message")
    assert result == "dummy response"


def test_marketplace_link_utf8():
    encoded = chat_ui.MARKETPLACE_LINK.encode("utf-8")
    assert b"MCP Servers Marketplace" in encoded


def test_launch_fallback(monkeypatch):
    calls = []

    def fake_launch(*args, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise ValueError("When localhost is not accessible, a shareable link must be created")

    monkeypatch.setattr(chat_ui.chatbot, "launch", fake_launch)
    chat_ui.launch()
    assert len(calls) == 2
    assert calls[1].get("share") is True
