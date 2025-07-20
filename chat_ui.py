import asyncio

import gradio as gr

from app.logger import logger

try:
    from app.agent.manus import Manus as _Manus
except Exception:  # pragma: no cover - missing heavy deps in tests
    _Manus = None

Manus = _Manus


class ChatSession:
    """Maintain a Manus agent instance for a chat session."""

    def __init__(self):
        global Manus
        if Manus is None:
            from app.agent.manus import Manus as _Manus
            Manus = _Manus
        self.agent = Manus()

    async def generate(self, message: str) -> str:
        if not message.strip():
            return "Please enter a valid message."
        try:
            logger.info("Processing message via Manus agent")
            return await self.agent.run(message)
        except Exception as exc:
            logger.error(f"Error generating response: {exc}")
            return f"Error: {exc}"


session: ChatSession | None = None


def get_session() -> ChatSession:
    global session
    if session is None:
        session = ChatSession()
    return session


def respond(message, history):
    """Wrapper for gradio ChatInterface."""
    sess = get_session()
    return asyncio.run(sess.generate(message))


with gr.Blocks() as chatbot:
    gr.Markdown(
        "<a href='https://github.com/modelcontextprotocol/servers' target='_blank'>"
        "\ud83d\udcbe MCP Servers Marketplace</a>"
    )
    gr.ChatInterface(
        respond,
        title="Manus Chat",
        description="ChatGPT style interface powered by Manus agent",
    )


def launch():
    chatbot.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    launch()
