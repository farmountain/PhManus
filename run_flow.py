import argparse
import asyncio
import re
import time

from app.flow.base import FlowType
from app.flow.flow_factory import FlowFactory
from app.logger import define_log_level, logger


def _validate_plan_id(value: str) -> str:
    """Validate plan identifier format."""
    if not re.match(r"^[A-Za-z0-9_-]+$", value):
        raise argparse.ArgumentTypeError(
            "plan-id must be alphanumeric and may include hyphens/underscores"
        )
    if len(value) > 50:
        raise argparse.ArgumentTypeError("plan-id must be under 50 characters")
    return value


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the PhManus planning flow")
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Task description for the agent to work on",
    )
    parser.add_argument(
        "--plan-id",
        dest="plan_id",
        type=_validate_plan_id,
        help="Use an existing plan identifier instead of creating a new one",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools and exit",
    )
    parsed = parser.parse_args(args=args)
    logger.debug(f"Parsed arguments: {parsed}")
    return parsed


async def run_flow(args: argparse.Namespace) -> None:
    from app.agent.manus import Manus

    agents = {"manus": Manus()}

    if args.verbose:
        define_log_level("DEBUG")
        logger.debug("Debug logging enabled")

    logger.info("Starting CLI run_flow")

    if args.list_tools:
        for key, agent in agents.items():
            tool_names = ", ".join([tool.name for tool in agent.available_tools])
            print(f"{key} tools: {tool_names}")
        if not args.prompt:
            return

    if not args.prompt or args.prompt.strip().isspace():
        logger.warning("Empty prompt provided.")
        return

    flow = FlowFactory.create_flow(
        flow_type=FlowType.PLANNING,
        agents=agents,
        plan_id=args.plan_id,
    )

    logger.info("Processing your request...")

    try:
        start_time = time.time()
        result = await asyncio.wait_for(
            flow.execute(args.prompt),
            timeout=3600,
        )
        elapsed_time = time.time() - start_time
        logger.info(f"Request processed in {elapsed_time:.2f} seconds")
        logger.info(result)
    except asyncio.TimeoutError:
        logger.error("Request processing timed out after 1 hour")
        logger.info(
            "Operation terminated due to timeout. Please try a simpler request."
        )
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_flow(parse_args()))
