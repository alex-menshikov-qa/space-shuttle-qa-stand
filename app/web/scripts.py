"""Page scripts, served through a tiny preprocessor.

A script may hold two variants of a fragment:

    // #if SOME_DEFECT
    ...lines served while the seeded defect is on...
    // #else
    ...lines served while it is off...
    // #endif

Only the matching lines are sent and the directive lines never are, so an
enabled defect changes what the page does without leaving a flag, attribute
or comment in the page for a test (or a tester) to key on.
"""

import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app import defects

router = APIRouter(include_in_schema=False)

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "static" / "js"
_NAME = re.compile(r"[a-z][a-z0-9_-]*")
_IF = re.compile(r"\s*// #if (\w+)\s*")
_ELSE = re.compile(r"\s*// #else\s*")
_ENDIF = re.compile(r"\s*// #endif\s*")


def preprocess(source: str) -> str:
    """Resolve the #if / #else / #endif blocks (not nested) against the defect flags."""
    out = []
    keep = True  # outside a block every line is kept
    for line in source.splitlines():
        match = _IF.fullmatch(line)
        if match:
            keep = defects.is_enabled(match[1])
        elif _ELSE.fullmatch(line):
            keep = not keep
        elif _ENDIF.fullmatch(line):
            keep = True
        elif keep:
            out.append(line)
    return "\n".join(out) + "\n"


@router.get("/static/js/{name}.js")
def script(name: str) -> Response:
    path = SCRIPTS_DIR / f"{name}.js"
    if not _NAME.fullmatch(name) or not path.is_file():
        raise HTTPException(status_code=404)
    return Response(
        preprocess(path.read_text(encoding="utf-8")),
        media_type="text/javascript",
        # Flags can change between restarts: make the browser revalidate.
        headers={"Cache-Control": "no-cache"},
    )
