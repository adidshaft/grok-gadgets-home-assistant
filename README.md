# Grok Gadgets: Home Assistant

Check what Home Assistant can offer your existing **Grok Bot**. `ha-probe` lists the tools,
resources, and prompts from Home Assistant's own MCP server. It never calls a tool or reads
a resource. A [setup recipe](docs/setup.md) describes the unverified Bot connection.
It is an experimental alpha and is not affiliated with xAI or Home Assistant.

## What works with Grok Bot today

**The probe works with fixtures and local test servers. Real Home Assistant and Grok Bot use remain unverified.**
Bot setup needs compatible authentication and a reachable HTTPS URL. Check the
[authentication gate](docs/setup.md#4-remote-route) before exposing a home server.
This package adds no home-control tools or event-triggered Bot tasks.

## Quickstart

You need Python 3.11+ and [`uv`](https://docs.astral.sh/uv/). From this repository, run:

```sh
uv sync --frozen
uv run ha-probe --fixture fixtures/assist.json
```

No home, account, or token is needed. Expected result (other fixed flags omitted):

```json
{
  "evidence": "fixture tested",
  "tool_count": 2,
  "resource_count": 1,
  "prompt_count": 1,
  "tool_calls_performed": 0,
  "resource_reads_performed": 0,
  "grok_verified": false,
  "hardware_verified": false
}
```

Next, [prepare a Home Assistant test user and run discovery](docs/setup.md#2-prepare-home-assistant-safely).
That guide keeps _Control Home Assistant_ off for the first test and explains HTTPS, token scope, and cleanup.
**A Home Assistant token is a full user credential.** Never paste it into chat or an issue. Revoke it after testing.

## Details

The probe enforces discovery-only requests, refuses redirects, and caps responses at 4 MiB.
It hides household names and descriptions. The [setup recipe](docs/setup.md#3-check-discovery-locally)
explains the local HTTP opt-in and other limits.

Run the checks with `uv run ruff check .`, `uv run ruff format --check .`, and
`uv run python -m unittest discover -s tests -v`. CI runs them on Python 3.11–3.14.

| Next | Guide |
| --- | --- |
| Set up a real home and remote route | [Setup recipe](docs/setup.md) |
| Sources and open questions | [Feasibility record](docs/feasibility.md) |
| What has been tested | [Verification](docs/verification.md) |
| Contribute or get help | [Contributing](CONTRIBUTING.md) · [Support](SUPPORT.md) · [Security](SECURITY.md) |

This repository is part of [Grok Gadgets](https://github.com/adidshaft/grok-gadgets).
The [gateway](https://github.com/adidshaft/grok-gadgets-gateway) and SDKs serve new gadgets. Home Assistant
uses its own MCP server instead. Native Bot compatibility is tracked as `HA-004`. See the
[hosting FAQ](https://github.com/adidshaft/grok-gadgets/blob/main/docs/getting-started/hosting.md) for who runs what.
Use the [issue chooser](https://github.com/adidshaft/grok-gadgets-home-assistant/issues/new/choose).
Keep tokens and household names out of issues. General discussion is at [r/GrokGadgets](https://www.reddit.com/r/GrokGadgets/)
under the hub's [Code of Conduct](https://github.com/adidshaft/grok-gadgets/blob/main/CODE_OF_CONDUCT.md).

Original code is [Apache-2.0](LICENSE), with attribution in [NOTICE](NOTICE). Dependencies are pinned by
[uv.lock](uv.lock). Package releases are pending; install from source. The docs follow the project
[writing guide](https://github.com/adidshaft/grok-gadgets/blob/main/docs/contributing/writing-guide.md), which is inspired by ASD-STE100.
Pre-publication commit dates were reconstructed at the owner's request. See the
[history and privacy record](https://github.com/adidshaft/grok-gadgets/blob/main/docs/verification/publication-sanitization.md).
