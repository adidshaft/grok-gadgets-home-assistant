# Repository instructions

Own only Home Assistant compatibility/client/recipes here. Reuse upstream MCP; explain any missing adapter. Consult the canonical project architecture/implementation plan in the hub before changing boundaries: https://github.com/adidshaft/grok-gadgets. Use subagents when required; do not open Brave/Safari or access Passwords. No publication, remote push, deployment, spending, or live home actions without authorization.

Use main and short feature branches, small tested commits referencing the local ledger. Keep issues current; migrate them to GitHub after authorized publication. Run `uv sync --frozen`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run python -m unittest discover -s tests -v`. Label fixtures honestly and keep tokens/private home state out of Git. Never infer Grok/hardware verification from MCP fixtures.

Research subagents require Max reasoning; documentation-only tasks reuse the dated feasibility records unless research is explicitly assigned. Public cross-repository policy links use owner adidshaft; private fallback contact is adidshaft@kyokasuigetsu.xyz. Do not present planned reporting/CI/release channels as activated. Keep workflow edits with their assigned owner.
