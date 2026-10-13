"""Dialect detection from file extension and source sniffing."""

from __future__ import annotations

from pathlib import Path

_EXT_MAP: dict[str, str] = {
    ".frag": "glsl",
    ".vert": "glsl",
    ".glsl": "glsl",
    ".comp": "glsl",
    ".hlsl": "hlsl",
    ".fx": "hlsl",
    ".hlsli": "hlsl",
}


def infer_dialect(path: Path) -> str:
    """Return 'glsl' or 'hlsl' from the file extension.

    Falls back to source sniffing when the extension is unknown — HLSL
    uses `float4`/`SV_Target`, GLSL uses `vec4`/`#version`. Sniffing is
    best-effort; ambiguous sources default to GLSL.
    """
    ext = path.suffix.lower()
    if ext in _EXT_MAP:
        return _EXT_MAP[ext]

    if ext in {".txt", ""}:
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:2048]
        except OSError:
            return "glsl"
        if "SV_Target" in head or "cbuffer" in head or "float4" in head:
            return "hlsl"
    return "glsl"


__all__ = ["infer_dialect"]
</｜｜DSML｜｜ parameter>