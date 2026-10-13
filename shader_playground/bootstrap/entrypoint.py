"""Process entrypoint for shader-playground-live.

Responsibilities:
  * Parse CLI args (shader path, dialect override, headless flags).
  * Configure logging to the platformdirs user-log location.
  * Build the QApplication and hand off to the main window.
  * Install the crash handler that dumps the last shader + log to disk.

Exit codes:
  0  clean shutdown
  1  unhandled exception during startup
  2  bad CLI arguments
  3  no OpenGL 4.3 context available
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from shader_playground.bootstrap.crash_handler import install_crash_handler
from shader_playground.config.settings import AppSettings, load_settings
from shader_playground.utils.logging_setup import configure_logging, get_logger

_LOG = get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shader-playground",
        description="Live GLSL/HLSL shader playground.",
    )
    parser.add_argument(
        "shader",
        nargs="?",
        type=Path,
        help="Optional shader file to open on launch (.glsl/.frag/.vert/.hlsl).",
    )
    parser.add_argument(
        "--dialect",
        choices=("glsl", "hlsl"),
        default=None,
        help="Force a shader dialect. Inferred from extension when omitted.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Compile-and-exit mode. Useful for CI shader linting.",
    )
    parser.add_argument(
        "--unsafe-shader-paths",
        action="store_true",
        help="Disable path confinement when loading presets. Do not use on "
        "a machine you care about.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings: AppSettings = load_settings(unsafe_paths=args.unsafe_shader_paths)
    configure_logging(settings.log_dir, verbose=settings.verbose)

    if args.version:
        from shader_playground import __version__

        print(f"shader-playground-live {__version__}")
        return 0

    install_crash_handler(settings.crash_dir, _LOG)

    if args.headless:
        return _run_headless(args, settings)

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        _LOG.error("PySide6 not installed. Run `pip install -e .` from the repo root.")
        return 1

    from shader_playground.handlers.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("shader-playground-live")
    app.setOrganizationName("shader-playground-live")

    window = MainWindow(settings=settings, initial_shader=args.shader, dialect=args.dialect)
    window.show()
    return app.exec()


def _run_headless(args: argparse.Namespace, settings: AppSettings) -> int:
    """Compile the given shader and exit. Used by CI and pre-commit hooks."""
    if args.shader is None:
        _LOG.error("--headless requires a shader path.")
        return 2

    from shader_playground.core.compile_pipeline import CompilePipeline
    from shader_playground.core.dialect import infer_dialect

    dialect = args.dialect or infer_dialect(args.shader)
    pipeline = CompilePipeline(settings=settings)
    result = pipeline.compile_file(args.shader, dialect=dialect)
    if result.ok:
        _LOG.info("compiled %s (%s) in %.1fms", args.shader, dialect, result.duration_ms)
        return 0
    for diag in result.diagnostics:
        _LOG.error("%s:%d:%d %s", args.shader, diag.line, diag.column, diag.message)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())