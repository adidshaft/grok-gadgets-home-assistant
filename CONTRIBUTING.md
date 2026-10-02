# Contributing to Home Assistant compatibility

Improve discovery fixtures, the read-only diagnostic client and the setup recipe here. Home Assistant owns its MCP server, entity exposure and home-control behavior. Capture a reproducible compatibility gap before proposing an adapter; the current route reuses upstream directly.

The [hub contribution guide](https://github.com/adidshaft/grok-gadgets/blob/main/CONTRIBUTING.md) owns the shared process. Hardware and account access are unnecessary for fixture, test or documentation work.

## Work from one checkout

1. Choose a [tracked issue](https://github.com/adidshaft/grok-gadgets-home-assistant/issues), or discuss a significant feature/interface change first. Typo fixes need no preliminary issue. Until publication, use [local IDs](planning/issues.json).
2. Fork/clone after activation and create a short branch, for example `git switch -c docs/clarify-fixture`.
3. From the repository root, install and check the locked Python 3.11 environment:

   ```sh
   uv sync --frozen --python 3.11
   uv run ha-probe --fixture fixtures/assist.json
   uv run ruff check .
   uv run ruff format --check .
   uv run python -m unittest discover -s tests -v
   uv build
   ```

4. Add a focused regression for changed probe behavior. Use hand-authored fixtures or a local fake endpoint; fixture output is not a real-home result. For documentation changes, rehearse the exact edited commands and validate links. Record source dates for upstream integration claims.
5. Open a focused PR linking its issue, with expected/observed behavior, commands and results, changed guides and unverified boundaries. Respond to review with small commits. The maintainer integrates tested changes into `main`; documentation and tests receive contribution credit alongside code.

Never add home-control calls to a diagnostic test without explicitly changing its scope. Do not include bearer tokens, household entity names, endpoint credentials or raw account logs. Do not infer Grok/mobile/hardware verification from a fixture or tool listing.

Contributions use Apache-2.0 without an additional CLA or sign-off requirement. AI assistance does not transfer responsibility for code, sources or test claims. Follow the shared [governance](https://github.com/adidshaft/grok-gadgets/blob/main/GOVERNANCE.md) and [Code of Conduct](https://github.com/adidshaft/grok-gadgets/blob/main/CODE_OF_CONDUCT.md). Send private conduct reports to [adidshaft@kyokasuigetsu.xyz](mailto:adidshaft@kyokasuigetsu.xyz); vulnerabilities use [Security](SECURITY.md). No fictitious review team or independent-human test result is implied.
