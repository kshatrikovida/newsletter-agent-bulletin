from __future__ import annotations

import json
import os
from pathlib import Path

from newsletter_agent.models import SourceConfig


def load_sources(config_path: str | Path) -> list[SourceConfig]:
    path = Path(config_path)
    raw_sources = json.loads(path.read_text(encoding="utf-8"))
    return [SourceConfig(**item) for item in raw_sources]


def load_env_file(env_path: str | Path, override: bool = False) -> None:
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if not key:
            continue
        if not override and key in os.environ:
            continue
        os.environ[key] = value
