import asyncio
import time

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

from app.agent.manus import Manus
from app.flow.base import FlowType
from app.flow.flow_factory import FlowFactory
from app.logger import logger


class SidePanelUI:
    """Terminal UI that displays agent thoughts and logs in a side panel."""

    def __init__(self):
        self.console = Console()
        self.logs: list[str] = []
        self.thoughts: list[str] = []
        logger.remove()
        logger.add(self._log_sink, format="{message}", level="INFO")
        logger.info("SidePanelUI initialized")

    def _log_sink(self, message: str):
        self.logs.append(message)

    def _render(self) -> Layout:
        layout = Layout()
        layout.split_row(
            Layout(Panel("\n".join(self.thoughts[-20:]), title="Agent Thoughts")),
            Layout(Panel("\n".join(self.logs[-20:]), title="Logs")),
        )
        return layout

    async def run(self):
        agents = {"manus": Manus()}
        prompt = input("Enter your prompt: ").strip()
        if not prompt or len(prompt) < 3:
            logger.warning("Invalid or empty prompt provided.")
            return

        flow = FlowFactory.create_flow(flow_type=FlowType.PLANNING, agents=agents)
        logger.warning("Processing your request...")
        start_time = time.time()
        with Live(self._render(), console=self.console, refresh_per_second=4) as live:
            task = asyncio.create_task(flow.execute(prompt))
            while not task.done():
                self.thoughts = [
                    f"{msg.role}: {msg.content}"
                    for msg in agents["manus"].memory.get_recent_messages(20)
                    if msg.content
                ]
                live.update(self._render())
                await asyncio.sleep(0.5)
            result = await task
            self.thoughts = [
                f"{msg.role}: {msg.content}"
                for msg in agents["manus"].memory.get_recent_messages(20)
                if msg.content
            ]
            elapsed_time = time.time() - start_time
            logger.info(f"Request processed in {elapsed_time:.2f} seconds")
            logger.info(result)
            live.update(self._render())
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(SidePanelUI().run())
