"""Per-dialect defaults — entry points, uniforms, precision hints.

When a user drops a fresh `.frag` or `.hlsl` into the editor, the
playground needs a shader skeleton that actually compiles. This module
holds the templates and the per-dialect compiler flags.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DialectProfile:
    name: str
    extension: str
    vertex_entry: str
    fragment_entry: str
    template: str
    compiler_flags: tuple[str, ...]


GLSL_TEMPLATE = """\
#version 430 core

// Vertex stage is provided by the playground — do not redeclare.
// This is a fragment shader. `uv` and `time` are injected uniforms.

in vec2 uv;
out vec4 fragColor;

uniform float time;
uniform vec2 resolution;

void main() {
    vec2 p = (uv - 0.5) * 2.0;
    p.x *= resolution.x / resolution.y;
    float d = length(p);
    vec3 col = vec3(0.5 + 0.5 * cos(time + d * 6.0 + vec3(0.0, 2.0, 4.0)));
    fragColor = vec4(col, 1.0);
}
"""

HLSL_TEMPLATE = """\
// HLSL fragment entry — compiled to SPIR-V via dxc.
// `uv` and `time` are injected by the playground.

cbuffer Frame : register(b0) {
    float time;
    float2 resolution;
    float2 _pad;
};

float4 ps_main(float2 uv : TEXCOORD0) : SV_Target {
    float2 p = (uv - 0.5) * 2.0;
    p.x *= resolution.x / resolution.y;
    float d = length(p);
    float3 col = 0.5 + 0.5 * cos(time + d * 6.0 + float3(0.0, 2.0, 4.0));
    return float4(col, 1.0);
}
"""


PROFILES: dict[str, DialectProfile] = {
    "glsl": DialectProfile(
        name="glsl",
        extension=".frag",
        vertex_entry="vs_main",
        fragment_entry="main",
        template=GLSL_TEMPLATE,
        compiler_flags=("--target-env", "opengl"),
    ),
    "hlsl": DialectProfile(
        name="hlsl",
        extension=".hlsl",
        vertex_entry="vs_main",
        fragment_entry="ps_main",
        template=HLSL_TEMPLATE,
        compiler_flags=("-T", "ps_6_0", "-E", "ps_main", "-spirv"),
    ),
}


def profile_for(dialect: str) -> DialectProfile:
    try:
        return PROFILES[dialect]
    except KeyError as e:
        raise ValueError(f"unknown dialect: {dialect!r}") from e


__all__ = ["DialectProfile", "PROFILES", "profile_for", "GLSL_TEMPLATE", "HLSL_TEMPLATE"]