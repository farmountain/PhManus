import pytest
import sys
import os

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
