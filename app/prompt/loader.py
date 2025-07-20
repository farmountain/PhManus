from pathlib import Path
from typing import Any, Dict

import yaml


def load_prompt(path: str) -> Dict[str, Any]:
    """Load a Parahelp SOP prompt specification from YAML."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)
    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Invalid prompt format")
    required_fields = {"role", "objective", "kpis", "output_format", "constraints"}
    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    return data
