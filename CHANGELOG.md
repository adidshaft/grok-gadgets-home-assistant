# Changelog

## Unreleased

## 0.1.0-alpha.6 — 24 October 2026

- Docs: the README and guides install from PyPI and describe the current route and start paths; support and community links are current. No probe behavior changes.
- Development tools: `ruff` 0.17.1 (code needed no changes) and current GitHub Actions pins.

## 0.1.0-alpha.5 — 12 October 2026

- A hand-started **release packages** workflow builds a tag, writes `SHA256SUMS` with plain file names, checks it in a fresh folder and attaches the files to the release. PyPI upload is a separate opt-in through trusted publishing; no token is stored ([#48](https://github.com/adidshaft/grok-gadgets-home-assistant/issues/48), hub [#151](https://github.com/adidshaft/grok-gadgets/issues/151)). The package is not on PyPI yet.
- README adds pip install from the release wheel. Homepage is https://grokgadgets.org/.
- Docs match the 12 October evidence and use shorter instructions. No probe behavior changes.

## 0.1.0-alpha.4 — 8 October 2026

- Development tools: `ruff` 0.16.10 and `hatchling` 1.32.4. Code follows the new `ruff` default rules without behavior changes. CI checks packages with `twine` 7.0.0, which reads the Metadata-Version 2.5 that `hatchling` 1.32 writes.

## 0.1.0-alpha.3 — 8 October 2026

- Dependabot opens weekly grouped update PRs into `dev`.
- CONTRIBUTING starts fork branches from `upstream/dev`. CI also runs the plain-language check on CONTRIBUTING and SUPPORT.

## 0.1.0-alpha.2 — 7 October 2026

- Include the contributor `ha-probe --version` option from PR #30.
- Align setup guidance with the Grok Bot-only project target.

## 0.1.0a1 — 6 October 2026

- CI runs the README Quickstart and checks its documented JSON output, on push, pull request and nightly.

## 0.1.0a1 — unpublished

Initial reuse recipe, feasibility evidence, fixture checks, and read-only probe. Real integrations pending.
