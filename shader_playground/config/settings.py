"""Application settings — loaded from TOML, environment, and CLI overrides.

Precedence (highest wins):
    1. CLI flags
    2. Environment (SP_*)
    3. User config  %APPDATA%/shader-playground-live/config.toml
    4. Built-in defaults

The settings object is frozen after load — the UI reads it, never mutates
it. Runtime state lives in the session model instead.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_log_dir


@dataclass(frozen=True, slots=True)
class AppSettings:
    config_dir: Path
    data_dir: Path
    log_dir: Path
    crash_dir: Path
    presets_dir: Path
    cache_dir: Path
    verbose: bool = False
    unsafe_paths: bool = False
    watch_debounce_ms: int = 120
    compile_timeout_ms: int = 4000
    target_fps: int = 60
    default_dialect: str = "glsl"
    recent_files: tuple[Path, ...] = field(default_factory=tuple)


_DEFAULTS_TOML = """\
verbose = false
watch_debounce_ms = 120
compile_timeout_ms = 4000
target_fps = 60
default_dialect = "glsl"
"""


def _read_user_toml(config_dir: Path) -> dict[str, object]:
    cfg = config_dir / "config.toml"
    if not cfg.exists():
        return {}
    try:
        with cfg.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        # A broken config must never brick the app. Fall back to defaults.
        return {}


def load_settings(*, unsafe_paths: bool = False) -> AppSettings:
    config_dir = Path(user_config_dir("shader-playground-live"))
    data_dir = Path(user_data_dir("shader-playground-live"))
    log_dir = Path(user_log_dir("shader-playground-live"))
    crash_dir = data_dir / "crashes"
    presets_dir = data_dir / "presets"
    cache_dir = data_dir / "cache"

    for d in (config_dir, data_dir, log_dir, crash_dir, presets_dir, cache_dir):
        d.mkdir(parents=True, exist_ok=True)

    user = _read_user_toml(config_dir)

    def _pick(key: str, default: object) -> object:
        env = os.environ.get(f"SP_{key.upper()}")
        if env is not None:
            return env
        return user.get(key, default)

    verbose = str(_pick("verbose", "false")).lower() in {"1", "true", "yes"}
    debounce = int(_pick("watch_debounce_ms", 120))
    timeout = int(_pick("compile_timeout_ms", 4000))
    fps = int(_pick("target_fps", 60))
    dialect = str(_pick("default_dialect", "glsl"))

    return AppSettings(
        config_dir=config_dir,
        data_dir=data_dir,
        log_dir=log_dir,
        crash_dir=crash_dir,
        presets_dir=presets_dir,
        cache_dir=cache_dir,
        verbose=verbose,
        unsafe_paths=unsafe_paths,
        watch_debounce_ms=debounce,
        compile_timeout_ms=timeout,
        target_fps=fps,
        default_dialect=dialect,
    )


__all__ = ["AppSettings", "load_settings", "_DEFAULTS_TOML"]