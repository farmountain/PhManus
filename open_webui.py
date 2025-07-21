import asyncio
from typing import List

import gradio as gr

from app.logger import logger

try:
    from app.agent.manus import Manus as _Manus
except Exception:  # pragma: no cover - missing heavy deps in tests
    _Manus = None

Manus = _Manus


class ChatSession:
    """Maintain a Manus agent instance and capture logs."""

    def __init__(self):
        global Manus
        if Manus is None:
            from app.agent.manus import Manus as _Manus

            Manus = _Manus
        self.agent = Manus()
        self.logs: List[str] = []
        logger.remove()
        logger.add(self._log_sink, format="{message}", level="INFO")
        logger.info("Open WebUI session initialized")

    def _log_sink(self, message: str):
        self.logs.append(message)

    async def generate(self, message: str) -> str:
        if not message.strip():
            return "Please enter a valid message."
        try:
            logger.info("Processing message via Manus agent")
            return await self.agent.run(message)
        except Exception as exc:  # pragma: no cover - handle runtime issues
            logger.error(f"Error generating response: {exc}")
            return f"Error: {exc}"

    def get_recent_logs(self, n: int = 20) -> List[str]:
        return self.logs[-n:]

    def get_recent_thoughts(self, n: int = 20) -> List[str]:
        return [
            f"{m.role}: {m.content}"
            for m in self.agent.memory.get_recent_messages(n)
            if m.content
        ]


session: ChatSession | None = None


def get_session() -> ChatSession:
    global session
    if session is None:
        session = ChatSession()
    return session


with gr.Blocks() as open_webui:
    gr.Markdown(
        "<a href='https://github.com/modelcontextprotocol/servers' target='_blank'>\ud83d\udcbe MCP Servers Marketplace</a>"
    )
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Message")
            send = gr.Button("Send")
        with gr.Column(scale=1):
            thoughts = gr.Textbox(label="Agent Thoughts", lines=20)
            logs = gr.Textbox(label="Logs", lines=20)

    def user_message(user, history):
        history = history + [[user, None]]
        return "", history

    async def bot_response(history):
        sess = get_session()
        prompt = history[-1][0]
        result = await sess.generate(prompt)
        history[-1][1] = result
        return history, "\n".join(sess.get_recent_thoughts()), "\n".join(sess.get_recent_logs())

    msg.submit(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_response, chatbot, [chatbot, thoughts, logs]
    )
    send.click(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_response, chatbot, [chatbot, thoughts, logs]
    )


def launch():
    open_webui.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    launch()
