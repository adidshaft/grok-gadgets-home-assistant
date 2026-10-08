# Contributing to Home Assistant compatibility

Improve discovery fixtures, the read-only diagnostic client, and the setup guide here.
Home Assistant controls its MCP server, entity exposure, and home-control behavior.
Before you propose an adapter, record a compatibility problem that others can reproduce.
The current connection uses the upstream server directly.

The [hub contribution guide](https://github.com/adidshaft/grok-gadgets/blob/main/CONTRIBUTING.md) owns the shared process. Hardware and account access are unnecessary for fixture, test or documentation work.

## Work from one checkout

1. Choose a [tracked issue](https://github.com/adidshaft/grok-gadgets-home-assistant/issues), or discuss a significant feature/interface change first. Typo fixes need no preliminary issue. Include a [local ID](planning/issues.json) if the issue has one.
2. Fork the repository and clone your fork. A fork can hold only `main`, so start a short-lived branch from the upstream `dev`:

   ```sh
   git clone https://github.com/YOUR_ACCOUNT/grok-gadgets-home-assistant.git
   cd grok-gadgets-home-assistant
   git remote add upstream https://github.com/adidshaft/grok-gadgets-home-assistant.git
   git fetch upstream dev
   git switch -c docs/HA-123-clarify-fixture upstream/dev
   ```

3. From the repository root, install and check the locked Python 3.11 environment:

   ```sh
   uv sync --frozen --python 3.11
   uv run ha-probe --fixture fixtures/assist.json
   uv run ruff check .
   uv run ruff format --check .
   uv run python -m unittest discover -s tests -v
   uv build
   ```

4. Add a test for changed probe behavior. Use manually written fixtures or a local fake endpoint. Fixture output is not a real-home result. For documentation changes, run the edited commands and check links. Record source dates for upstream integration claims.
5. Push the branch to your fork and open a focused PR into `adidshaft/grok-gadgets-home-assistant` `dev`. The GitHub PR form selects `main` by default. Change the base branch to `dev`, because the PR-target check rejects other PRs into `main`. Link its issue. Include expected and actual behavior, check commands, results, and updated guides. State what remains unverified. Respond to review with small commits. The maintainer squash-merges tested changes into `dev`. Code, documentation, and tests receive contribution credit.

Never add home-control calls to a diagnostic test without explicitly changing its scope. Do not include bearer tokens, household entity names, endpoint credentials or raw account logs. Do not infer Grok/mobile/hardware verification from a fixture or tool listing.

Contributions use Apache-2.0 without an additional CLA or sign-off requirement. You remain responsible for AI-assisted code, sources, and test claims. Follow the shared [governance](https://github.com/adidshaft/grok-gadgets/blob/main/GOVERNANCE.md) and [Code of Conduct](https://github.com/adidshaft/grok-gadgets/blob/main/CODE_OF_CONDUCT.md). Send private conduct reports to [adidshaft@kyokasuigetsu.xyz](mailto:adidshaft@kyokasuigetsu.xyz); vulnerabilities use [Security](SECURITY.md). Do not claim review by a team or testing by another person without evidence.

## Branches

Branch from `dev` and open your PR into `dev` for integration, development and testing; PRs into `dev` are squash-merged when checks pass. `main` is the default branch for users, builders and the website, holds tagged releases, and changes only through release or hotfix PRs. Name branches `<type>/<ISSUE-ID>-<short-slug>`, for example `fix/HA-021-short-name`. The shared [branch and release policy](https://github.com/adidshaft/grok-gadgets/blob/main/CONTRIBUTING.md#branches-and-releases) covers releases, hotfixes and cross-repository changes.

## Ignore rules and publication privacy

Update `.gitignore` when a new tool creates caches, build output, local configuration, logs, or credentials.
Keep reviewed sample configuration files and the hub's verified public simulator download.
Check new patterns with `git check-ignore`. Review staged files before each commit.
Ignore rules do not remove tracked files or Git history. Never merge private pre-publication history into a public branch.
Use the sanitized public checkout. Use a public or GitHub noreply commit email.
