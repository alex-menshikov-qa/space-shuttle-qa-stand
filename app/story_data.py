"""Story data: editable JSON files in app/data (FAQ now; stations, fleet and the
shipyard catalog later). Texts and names change there, not in the code."""

import json
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


@cache
def load(name: str) -> list[dict]:
    """Parsed content of app/data/<name>.json (read once per process)."""
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))
