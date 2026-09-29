# Repository instructions

Own only Home Assistant compatibility/client/recipes here. Reuse upstream MCP; explain any missing adapter. Read the project implementation plan in ../grok-gadgets/planning before changing boundaries. Use subagents when required; do not open Brave/Safari or access Passwords. No publication, remote push, deployment, spending, or live home actions without authorization.

Use main and short feature branches, small tested commits referencing the local ledger. Keep issues current; migrate them to GitHub after authorized publication. Run `uv sync --frozen`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run python -m unittest discover -s tests -v`. Label fixtures honestly and keep tokens/private home state out of Git. Never infer Grok/hardware verification from MCP fixtures.
