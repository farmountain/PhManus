# tool/planning.py
import asyncio
import json
import os
import sqlite3
from contextlib import closing
from typing import Dict, List, Literal, Optional

import requests

from app.config import WORKSPACE_ROOT, config
from app.exceptions import ToolError
from app.tool.base import BaseTool, ToolResult


_PLANNING_TOOL_DESCRIPTION = """
A planning tool that allows the agent to create and manage plans for solving complex tasks.
The tool provides functionality for creating plans, updating plan steps, tracking progress,
and optionally persisting plans to a JSON file or SQLite database.
"""


class PlanningTool(BaseTool):
    """
    A planning tool that allows the agent to create and manage plans for solving complex tasks.
    The tool provides functionality for creating plans, updating plan steps, and tracking progress.
    """

    name: str = "planning"
    description: str = _PLANNING_TOOL_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "description": "The command to execute. Available commands: create, update, list, get, set_active, mark_step, delete, resume.",
                "enum": [
                    "create",
                    "update",
                    "list",
                    "get",
                    "set_active",
                    "mark_step",
                    "delete",
                    "resume",
                ],
                "type": "string",
            },
            "plan_id": {
                "description": "Unique identifier for the plan. Required for create, update, set_active, and delete commands. Optional for get and mark_step (uses active plan if not specified).",
                "type": "string",
            },
            "title": {
                "description": "Title for the plan. Required for create command, optional for update command.",
                "type": "string",
            },
            "steps": {
                "description": "List of plan steps. Required for create command, optional for update command.",
                "type": "array",
                "items": {"type": "string"},
            },
            "step_index": {
                "description": "Index of the step to update (0-based). Required for mark_step command.",
                "type": "integer",
            },
            "step_status": {
                "description": "Status to set for a step. Used with mark_step command.",
                "enum": ["not_started", "in_progress", "completed", "blocked"],
                "type": "string",
            },
            "step_notes": {
                "description": "Additional notes for a step. Optional for mark_step command.",
                "type": "string",
            },
        },
        "required": ["command"],
        "additionalProperties": False,
    }

    plans: dict = {}  # Dictionary to store plans by plan_id
    _current_plan_id: Optional[str] = None  # Track the current active plan

    storage_type: Literal["memory", "json", "sqlite"] = "memory"
    storage_path: Optional[str] = None
    _conn: Optional[sqlite3.Connection] = None

    def __init__(self, storage_type: str = "memory", storage_path: Optional[str] = None):
        super().__init__(storage_type=storage_type, storage_path=storage_path)
        if self.storage_type in {"json", "sqlite"}:
            if not self.storage_path:
                default = "plans.json" if self.storage_type == "json" else "plans.db"
                self.storage_path = str(WORKSPACE_ROOT / default)

        if self.storage_type == "sqlite":
            self._conn = sqlite3.connect(self.storage_path)
            self._init_db()

        self._load_plans()

    def _init_db(self) -> None:
        if not self._conn:
            return
        with closing(self._conn.cursor()) as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS plans (plan_id TEXT PRIMARY KEY, title TEXT, steps TEXT, step_statuses TEXT, step_notes TEXT)"
            )
            self._conn.commit()

    def _load_plans(self) -> None:
        """Load existing plans from storage into memory."""
        if self.storage_type == "json":
            if self.storage_path and os.path.exists(self.storage_path):
                try:
                    with open(self.storage_path, "r", encoding="utf-8") as f:
                        self.plans = json.load(f)
                except Exception:
                    self.plans = {}
        elif self.storage_type == "sqlite" and self._conn:
            with closing(self._conn.cursor()) as c:
                c.execute("SELECT plan_id, title, steps, step_statuses, step_notes FROM plans")
                rows = c.fetchall()
                self.plans = {}
                for pid, title, steps, statuses, notes in rows:
                    self.plans[pid] = {
                        "plan_id": pid,
                        "title": title,
                        "steps": json.loads(steps),
                        "step_statuses": json.loads(statuses),
                        "step_notes": json.loads(notes),
                    }
        else:
            self.plans = {}

    def _persist_plan(self, plan: Dict) -> None:
        if self.storage_type == "json" and self.storage_path:
            try:
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump(self.plans, f, indent=2)
            except Exception:
                pass
        elif self.storage_type == "sqlite" and self._conn:
            with closing(self._conn.cursor()) as c:
                c.execute(
                    "REPLACE INTO plans (plan_id, title, steps, step_statuses, step_notes) VALUES (?, ?, ?, ?, ?)",
                    (
                        plan["plan_id"],
                        plan["title"],
                        json.dumps(plan["steps"]),
                        json.dumps(plan["step_statuses"]),
                        json.dumps(plan["step_notes"]),
                    ),
                )
                self._conn.commit()

    def _remove_plan(self, plan_id: str) -> None:
        if self.storage_type == "json" and self.storage_path:
            try:
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump(self.plans, f, indent=2)
            except Exception:
                pass
        elif self.storage_type == "sqlite" and self._conn:
            with closing(self._conn.cursor()) as c:
                c.execute("DELETE FROM plans WHERE plan_id=?", (plan_id,))
                self._conn.commit()

    async def _sync_with_mcp(
        self, method: str, plan_id: str, payload: Optional[dict] = None
    ):
        """Synchronize plan data with MCP server if configured."""
        if not config.mcp_config or not config.mcp_config.server_url:
            return

        url = f"{config.mcp_config.server_url.rstrip('/')}/plans/{plan_id}"
        headers = {}
        if config.mcp_config.api_key:
            headers["Authorization"] = f"Bearer {config.mcp_config.api_key}"

        def request_fn():
            if method == "POST":
                requests.post(url, json=payload, headers=headers, timeout=5)
            elif method == "PUT":
                requests.put(url, json=payload, headers=headers, timeout=5)
            elif method == "DELETE":
                requests.delete(url, headers=headers, timeout=5)
            elif method == "GET":
                return requests.get(url, headers=headers, timeout=5)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, request_fn)

    async def execute(
        self,
        *,
        command: Literal[
            "create", "update", "list", "get", "set_active", "mark_step", "delete", "resume"
        ],
        plan_id: Optional[str] = None,
        title: Optional[str] = None,
        steps: Optional[List[str]] = None,
        step_index: Optional[int] = None,
        step_status: Optional[
            Literal["not_started", "in_progress", "completed", "blocked"]
        ] = None,
        step_notes: Optional[str] = None,
        **kwargs,
    ):
        """
        Execute the planning tool with the given command and parameters.

        Parameters:
        - command: The operation to perform
        - plan_id: Unique identifier for the plan
        - title: Title for the plan (used with create command)
        - steps: List of steps for the plan (used with create command)
        - step_index: Index of the step to update (used with mark_step command)
        - step_status: Status to set for a step (used with mark_step command)
        - step_notes: Additional notes for a step (used with mark_step command)
        """

        if command == "create":
            return self._create_plan(plan_id, title, steps)
        elif command == "update":
            return self._update_plan(plan_id, title, steps)
        elif command == "list":
            return self._list_plans()
        elif command == "get":
            return self._get_plan(plan_id)
        elif command == "set_active":
            return self._set_active_plan(plan_id)
        elif command == "mark_step":
            return self._mark_step(plan_id, step_index, step_status, step_notes)
        elif command == "delete":
            return self._delete_plan(plan_id)
        elif command == "resume":
            return self._resume_plan(plan_id)
        else:
            raise ToolError(
                f"Unrecognized command: {command}. Allowed commands are: create, update, list, get, set_active, mark_step, delete, resume"
            )

    def _create_plan(
        self, plan_id: Optional[str], title: Optional[str], steps: Optional[List[str]]
    ) -> ToolResult:
        """Create a new plan with the given ID, title, and steps."""
        if not plan_id:
            raise ToolError("Parameter `plan_id` is required for command: create")

        if plan_id in self.plans:
            raise ToolError(
                f"A plan with ID '{plan_id}' already exists. Use 'update' to modify existing plans."
            )

        if not title:
            raise ToolError("Parameter `title` is required for command: create")

        if (
            not steps
            or not isinstance(steps, list)
            or not all(isinstance(step, str) for step in steps)
        ):
            raise ToolError(
                "Parameter `steps` must be a non-empty list of strings for command: create"
            )

        # Create a new plan with initialized step statuses
        plan = {
            "plan_id": plan_id,
            "title": title,
            "steps": steps,
            "step_statuses": ["not_started"] * len(steps),
            "step_notes": [""] * len(steps),
        }

        self.plans[plan_id] = plan
        self._current_plan_id = plan_id  # Set as active plan
        self._persist_plan(plan)

        asyncio.create_task(self._sync_with_mcp("POST", plan_id, plan))

        return ToolResult(
            output=f"Plan created successfully with ID: {plan_id}\n\n{self._format_plan(plan)}"
        )

    def _update_plan(
        self, plan_id: Optional[str], title: Optional[str], steps: Optional[List[str]]
    ) -> ToolResult:
        """Update an existing plan with new title or steps."""
        if not plan_id:
            raise ToolError("Parameter `plan_id` is required for command: update")

        if plan_id not in self.plans:
            raise ToolError(f"No plan found with ID: {plan_id}")

        plan = self.plans[plan_id]

        if title:
            plan["title"] = title

        if steps:
            if not isinstance(steps, list) or not all(
                isinstance(step, str) for step in steps
            ):
                raise ToolError(
                    "Parameter `steps` must be a list of strings for command: update"
                )

            # Preserve existing step statuses for unchanged steps
            old_steps = plan["steps"]
            old_statuses = plan["step_statuses"]
            old_notes = plan["step_notes"]

            # Create new step statuses and notes
            new_statuses = []
            new_notes = []

            for i, step in enumerate(steps):
                # If the step exists at the same position in old steps, preserve status and notes
                if i < len(old_steps) and step == old_steps[i]:
                    new_statuses.append(old_statuses[i])
                    new_notes.append(old_notes[i])
                else:
                    new_statuses.append("not_started")
                    new_notes.append("")

            plan["steps"] = steps
            plan["step_statuses"] = new_statuses
            plan["step_notes"] = new_notes

        self._persist_plan(plan)

        asyncio.create_task(self._sync_with_mcp("PUT", plan_id, plan))

        return ToolResult(
            output=f"Plan updated successfully: {plan_id}\n\n{self._format_plan(plan)}"
        )

    def _list_plans(self) -> ToolResult:
        """List all available plans."""
        if not self.plans:
            return ToolResult(
                output="No plans available. Create a plan with the 'create' command."
            )

        output = "Available plans:\n"
        for plan_id, plan in self.plans.items():
            current_marker = " (active)" if plan_id == self._current_plan_id else ""
            completed = sum(
                1 for status in plan["step_statuses"] if status == "completed"
            )
            total = len(plan["steps"])
            progress = f"{completed}/{total} steps completed"
            output += f"• {plan_id}{current_marker}: {plan['title']} - {progress}\n"

        return ToolResult(output=output)

    def _get_plan(self, plan_id: Optional[str]) -> ToolResult:
        """Get details of a specific plan."""
        if not plan_id:
            # If no plan_id is provided, use the current active plan
            if not self._current_plan_id:
                raise ToolError(
                    "No active plan. Please specify a plan_id or set an active plan."
                )
            plan_id = self._current_plan_id

        if plan_id not in self.plans:
            raise ToolError(f"No plan found with ID: {plan_id}")

        plan = self.plans[plan_id]
        return ToolResult(output=self._format_plan(plan))

    def _set_active_plan(self, plan_id: Optional[str]) -> ToolResult:
        """Set a plan as the active plan."""
        if not plan_id:
            raise ToolError("Parameter `plan_id` is required for command: set_active")

        if plan_id not in self.plans:
            raise ToolError(f"No plan found with ID: {plan_id}")

        self._current_plan_id = plan_id
        return ToolResult(
            output=f"Plan '{plan_id}' is now the active plan.\n\n{self._format_plan(self.plans[plan_id])}"
        )

    def _resume_plan(self, plan_id: Optional[str]) -> ToolResult:
        """Resume a saved plan by setting it active."""
        return self._set_active_plan(plan_id)

    def _mark_step(
        self,
        plan_id: Optional[str],
        step_index: Optional[int],
        step_status: Optional[str],
        step_notes: Optional[str],
    ) -> ToolResult:
        """Mark a step with a specific status and optional notes."""
        if not plan_id:
            # If no plan_id is provided, use the current active plan
            if not self._current_plan_id:
                raise ToolError(
                    "No active plan. Please specify a plan_id or set an active plan."
                )
            plan_id = self._current_plan_id

        if plan_id not in self.plans:
            raise ToolError(f"No plan found with ID: {plan_id}")

        if step_index is None:
            raise ToolError("Parameter `step_index` is required for command: mark_step")

        plan = self.plans[plan_id]

        if step_index < 0 or step_index >= len(plan["steps"]):
            raise ToolError(
                f"Invalid step_index: {step_index}. Valid indices range from 0 to {len(plan['steps'])-1}."
            )

        if step_status and step_status not in [
            "not_started",
            "in_progress",
            "completed",
            "blocked",
        ]:
            raise ToolError(
                f"Invalid step_status: {step_status}. Valid statuses are: not_started, in_progress, completed, blocked"
            )

        if step_status:
            plan["step_statuses"][step_index] = step_status

        if step_notes:
            plan["step_notes"][step_index] = step_notes

        self._persist_plan(plan)

        return ToolResult(
            output=f"Step {step_index} updated in plan '{plan_id}'.\n\n{self._format_plan(plan)}"
        )

    def _delete_plan(self, plan_id: Optional[str]) -> ToolResult:
        """Delete a plan."""
        if not plan_id:
            raise ToolError("Parameter `plan_id` is required for command: delete")

        if plan_id not in self.plans:
            raise ToolError(f"No plan found with ID: {plan_id}")

        del self.plans[plan_id]
        self._remove_plan(plan_id)

        # If the deleted plan was the active plan, clear the active plan
        if self._current_plan_id == plan_id:
            self._current_plan_id = None

        asyncio.create_task(self._sync_with_mcp("DELETE", plan_id))

        return ToolResult(output=f"Plan '{plan_id}' has been deleted.")

    def _format_plan(self, plan: Dict) -> str:
        """Format a plan for display."""
        output = f"Plan: {plan['title']} (ID: {plan['plan_id']})\n"
        output += "=" * len(output) + "\n\n"

        # Calculate progress statistics
        total_steps = len(plan["steps"])
        completed = sum(1 for status in plan["step_statuses"] if status == "completed")
        in_progress = sum(
            1 for status in plan["step_statuses"] if status == "in_progress"
        )
        blocked = sum(1 for status in plan["step_statuses"] if status == "blocked")
        not_started = sum(
            1 for status in plan["step_statuses"] if status == "not_started"
        )

        output += f"Progress: {completed}/{total_steps} steps completed "
        if total_steps > 0:
            percentage = (completed / total_steps) * 100
            output += f"({percentage:.1f}%)\n"
        else:
            output += "(0%)\n"

        output += f"Status: {completed} completed, {in_progress} in progress, {blocked} blocked, {not_started} not started\n\n"
        output += "Steps:\n"

        # Add each step with its status and notes
        for i, (step, status, notes) in enumerate(
            zip(plan["steps"], plan["step_statuses"], plan["step_notes"])
        ):
            status_symbol = {
                "not_started": "[ ]",
                "in_progress": "[→]",
                "completed": "[✓]",
                "blocked": "[!]",
            }.get(status, "[ ]")

            output += f"{i}. {status_symbol} {step}\n"
            if notes:
                output += f"   Notes: {notes}\n"

        return output
