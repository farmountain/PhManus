import os
import sys
import asyncio

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import open_webui


class DummyManus:
    async def run(self, message: str) -> str:
        return "dummy response"


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
