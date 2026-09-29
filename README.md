# Grok Gadgets: Home Assistant

Integration guidance and compatibility checks for the upstream Home Assistant MCP server. Independent open-source project exclusively targeting Grok; not affiliated with xAI or Home Assistant.

Status: local alpha preparation. No real home, Grok account, mobile, or hardware verification. This repository adds a diagnostic client, not another home-control server.

See [integration recipe](docs/setup.md), [feasibility](docs/feasibility.md), and [local issues](planning/issues.json). Original code is Apache-2.0.

Setup and fixture checks (Python 3.11+ and uv):

```sh
uv sync --frozen
uv run python -m unittest discover -s tests -v
uv run ha-probe --fixture fixtures/assist.json
```

These checks need no account or hardware. See the recipe before using a real endpoint.
