"""Persist alert states atomically, so failures do not corrupt the tracked JSON."""
import json
import os
import tempfile

import config


def load_state() -> dict:
    if not os.path.exists(config.STATE_FILE):
        return {}
    try:
        with open(config.STATE_FILE, "r", encoding="utf-8") as f:
            value = json.load(f)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: dict) -> None:
    """Replace the state file atomically only after fully writing valid JSON."""
    target = os.path.abspath(config.STATE_FILE)
    directory = os.path.dirname(target)
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".state-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
