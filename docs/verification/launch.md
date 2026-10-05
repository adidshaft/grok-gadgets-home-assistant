# Standalone documentation rehearsal — 5 October 2026

The first experience was checked in a fresh temporary source directory with no sibling repositories and then through a separately installed wheel. Runtime source was committed `5a808b23371e373e961a0217ac94d1e6b6129418`; the new README/setup/policy working changes were copied into that archive. No runtime, tests, schemas or dependency locks changed.

Environment: macOS 27.0 arm64, Python 3.11.15, uv 0.12.3, MCP SDK 2.3.0, Ruff 0.15.7; wheel/sdist backend hatchling 1.27.0 pinned in pyproject. Dependencies were installed from the frozen lock, reusing the existing offline cache. This is fresh-environment reproduction by an agent, not independent-human or empty-cache installation evidence.

| Command from the standalone source directory | Result |
| --- | --- |
| `uv sync --frozen --offline --python 3.11` | Passed; fresh environment, locked installation |
| `uv run ha-probe --fixture fixtures/assist.json` | Passed; 2 tools, 1 resource, 1 prompt; 0 tool calls/resource reads |
| `uv run ruff check .` and `uv run ruff format --check .` | Passed |
| `uv run python -m unittest discover -s tests -v` | Passed; 13 tests |
| `uv build --offline` | Passed; wheel and sdist built |
| Install the wheel into another fresh Python 3.11 venv and run its `ha-probe --fixture <source>/fixtures/assist.json` outside the checkout | Passed; same fixture counts and false Grok/hardware flags |

The package metadata declares Apache-2.0 original code; inspection found `LICENSE` and `NOTICE` inside the wheel's license directory. The MCP dependency retains its installed license file, and Home Assistant code is not vendored. See the unchanged root NOTICE and frozen dependency distributions for attribution. Distribution review remains required before public release.

Raw output and hashes are retained privately under ignored `reports/launch-docs/`. The trial's source/build state is recorded there, so this working-source trial is not mislabeled as a package built from a future commit. The final launch candidate is built from committed sources by the hub publication tooling and carries exact source/SHA-256 provenance. Verify those hashes against the actual selected candidate, rather than treating older `dist` files as current.

The optional real-endpoint procedure was not run. No account, household state, tool execution, OAuth, mobile behavior, real Home Assistant installation or physical device was accessed. HA-004 remains blocked; the fixture proves the diagnostic behavior tested here.

## Committed package checkpoint

`uv build --offline` built wheel and sdist from clean documentation commit `c36f06e548ddcdfbf383665a97f15631b604abd1`. The [artifact record](../../planning/artifacts.json) identifies that source, environment, actual sizes/hashes and inspected wheel license metadata. The 8,449-byte wheel has SHA-256 `ccaa745c6c9528175918d92e71a5e22c966523783e57f87ad873387f933240fa`; the 68,553-byte sdist has SHA-256 `bb040a6c88449b871221956cdf2c8480fe8eecc7ce9db2d6d6684f33c9b122fd`.

This evidence-only checkpoint changes source documentation, so the final launch candidate rebuilds its sdist from the selected final committed source. Existing local packages are unpublished; current-candidate source and hashes take precedence over this historical checkpoint.
