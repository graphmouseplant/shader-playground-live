# Contributing to shader-playground-live

Thanks for wanting to poke at the tater. This is a Windows-first desktop
shader sandbox — live GLSL/HLSL editing, hot reload, and a small native
bridge for the HLSL → SPIR-V path. Contributions welcome from anyone who
likes watching a fragment shader recompile in under a frame.

## Ground rules

- Python 3.11+ is the baseline. 3.12 is what CI runs.
- GUI is PySide6 (Qt6). Do not introduce PyQt5 — license and API drift.
- Native bridge is C++20 with CMake. Keep it optional; the pure-Python
  fallback path must keep working for contributors without MSVC.
- No shader dialect wars in the issue tracker. Both GLSL and HLSL ship.

## Dev setup

```powershell
git clone https://github.com/yourname/shader-playground-live.git
cd shader-playground-live
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m shader_playground.bootstrap.entrypoint
```

For the native HLSL bridge:

```powershell
cd native
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

The Python side auto-detects `native/build/Release/spbridge.dll` on
import. If it's missing, the HLSL compiler falls back to `dxc.exe` via
subprocess — slower, but it works.

## Code style

- `ruff` + `black` + `mypy --strict` on `shader_playground/`.
- Line length 100. No exceptions.
- Public functions get type hints. Private helpers can be loose.
- Logging via the `sp.logging` helper — no bare `print()` in shipped code.

## Tests

```powershell
pytest -q
pytest --cov=shader_playground --cov-report=term-missing
```

Shader compilation tests are marked `@pytest.mark.gpu` and skipped when
no OpenGL 4.3 context is available. Run them locally before opening a PR
that touches the compile pipeline.

## Pull requests

- One concern per PR. "Refactor + feature" gets split.
- Include a screenshot or a recorded GIF for any UI change. The editor
  has too many moving parts for a description to be enough.
- Update `CHANGELOG.md` if you touch the public API surface of
  `shader_playground.core`.

## Reporting shader bugs

Attach the failing shader, the driver version (`glGetString(GL_VERSION)`),
and the full compiler log. "It doesn't work" is not a bug report.