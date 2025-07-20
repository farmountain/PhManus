from pathlib import Path
from typing import Any, Dict

import yaml


def load_workflow(path: str) -> Dict[str, Any]:
    """Load a workflow definition from a YAML file.

    Parameters
    ----------
    path: str
        Path to the YAML file containing the workflow.

    Returns
    -------
    dict
        Parsed workflow dictionary.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)

    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "workflow" not in data:
        raise ValueError("Invalid workflow format")

    return data["workflow"]
