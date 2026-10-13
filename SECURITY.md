# Security Policy

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | Yes                |
| 0.3.x   | Security fixes only |
| < 0.3   | No                 |

## Reporting a vulnerability

Open a private security advisory on GitHub, or mail
`security@shader-playground-live.invalid` (replace with the real domain
before shipping). Do not open a public issue for anything that could be
turned into a local code-execution primitive.

Things we care about:

- Sandbox escapes from the shader compile pipeline. Shader source is
  user-supplied and we shell out to `dxc.exe` / `glslangValidator` —
  argument injection there is a real class of bug.
- Path traversal in the preset loader. Presets are JSON and reference
  relative shader paths; a malicious preset must not read outside its
  own directory.
- Arbitrary file write via the export/screenshot pipeline.
- Deserialization in `shader_playground.services.preset_store` — we use
  `json`, not `pickle`, and we intend to keep it that way.

Things we do not consider vulnerabilities:

- The editor running arbitrary user shaders on the user's own GPU. That
  is the entire point of the tool.
- Crashes from malformed shaders. Report them as bugs, not CVEs.
- Denial of service via a 500 MB shader. There's a soft cap; we'll raise
  it if someone actually hits it.

## Response timeline

- Acknowledgment within 72 hours.
- Triage within 7 days.
- Patch or mitigation for confirmed issues within 30 days, faster for
  anything with a working PoC.

## Hardening notes for users

- Presets from untrusted sources can point at arbitrary shader files.
  Review the JSON before loading.
- The `--unsafe-shader-paths` flag disables path confinement. Do not
  use it on a machine you care about.