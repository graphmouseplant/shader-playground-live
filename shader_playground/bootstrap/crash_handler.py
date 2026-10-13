"""Crash handler — dumps the last-active shader and log tail on unhandled exceptions.

Writes a timestamped dump into the platformdirs crash directory so users
can attach a single file to a bug report instead of trying to describe
what happened.

Dump layout:
    <crash_dir>/crash-YYYYMMDD-HHMMSS/
        traceback.txt
        last_shader.<ext>
        log_tail.txt
        env.json
"""

from __future__ import annotations

import json
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Callable

from shader_playground.utils.logging_setup import get_logger

_LOG = get_logger(__name__)

_LAST_SHADER: Path | None = None
_LOG_TAIL_LINES = 200


def register_last_shader(path: Path) -> None:
    """Called by the editor whenever the active buffer changes."""
    global _LAST_SHADER
    _LAST_SHADER = path


def _dump(crash_dir: Path, exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = crash_dir / f"crash-{stamp}"
    target.mkdir(parents=True, exist_ok=True)

    (target / "traceback.txt").write_text(
        "".join(traceback.format_exception(exc_type, exc, tb)), encoding="utf-8"
    )

    if _LAST_SHADER is not None and _LAST_SHADER.exists():
        try:
            (target / f"last_shader{_LAST_SHADER.suffix}").write_bytes(_LAST_SHADER.read_bytes())
        except OSError as e:
            _LOG.warning("could not snapshot last shader: %s", e)

    (target / "env.json").write_text(
        json.dumps(
            {
                "python": sys.version,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "executable": sys.executable,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return target


def install_crash_handler(crash_dir: Path, logger: Callable[..., None] | None = None) -> None:
    """Chain onto sys.excepthook. Preserves the default hook's exit behavior."""
    crash_dir.mkdir(parents=True, exist_ok=True)
    default_hook = sys.excepthook

    def _hook(
        exc_type: type[BaseException],
        exc: BaseException,
        tb: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            default_hook(exc_type, exc, tb)
            return
        try:
            target = _dump(crash_dir, exc_type, exc, tb)
            _LOG.error("unhandled exception — dump at %s", target)
        except Exception as dump_err:  # noqa: BLE001 — handler must never raise
            _LOG.error("crash dump failed: %s", dump_err)
        default_hook(exc_type, exc, tb)

    sys.excepthook = _hook