"""Page scripts and the stylesheet, served through a tiny preprocessor.

A file may hold two variants of a fragment. In a script:

    // #if SOME_DEFECT
    ...lines served while the seeded defect is on...
    // #else
    ...lines served while it is off...
    // #endif

In the stylesheet the directives are written as CSS comments:
`/* #if SOME_DEFECT */`, `/* #else */`, `/* #endif */`.

Only the matching lines are sent and the directive lines never are, so an
enabled defect changes what the page does or looks like without leaving a
flag, attribute or comment in the page for a test (or a tester) to key on.
"""

import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app import defects

router = APIRouter(include_in_schema=False)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
_NAME = re.compile(r"[a-z][a-z0-9_-]*")
_OPEN = r"\s*(?://|/\*)\s*"
_CLOSE = r"\s*(?:\*/)?\s*"
_IF = re.compile(_OPEN + r"#if (\w+)" + _CLOSE)
_ELSE = re.compile(_OPEN + r"#else" + _CLOSE)
_ENDIF = re.compile(_OPEN + r"#endif" + _CLOSE)


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


def _serve(folder: str, name: str, extension: str, media_type: str) -> Response:
    path = STATIC_DIR / folder / f"{name}.{extension}"
    if not _NAME.fullmatch(name) or not path.is_file():
        raise HTTPException(status_code=404)
    return Response(
        preprocess(path.read_text(encoding="utf-8")),
        media_type=media_type,
        # Flags can change between restarts: make the browser revalidate.
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/static/js/{name}.js")
def script(name: str) -> Response:
    return _serve("js", name, "js", "text/javascript")


@router.get("/static/css/{name}.css")
def stylesheet(name: str) -> Response:
    return _serve("css", name, "css", "text/css")
