# Standalone documentation rehearsal — 5 October 2026

The first experience was checked in a fresh temporary source directory with no sibling repositories and then through a separately installed wheel. Runtime source was committed `a8b2370b7e82e136511b6299e1317eb80915d012`; the new README/setup/policy working changes were copied into that archive. No runtime, tests, schemas or dependency locks changed.

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
