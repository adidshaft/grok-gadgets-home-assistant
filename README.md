# Grok Gadgets: Home Assistant

Home Assistant already ships its own MCP server, so Grok Bot does not need a second one.
This repository gives you two things: `ha-probe`, a safe read-only check of what your
Home Assistant MCP server exposes, and a [setup recipe](docs/setup.md) for connecting Grok Bot to it.
It is an experimental alpha and is not affiliated with xAI or Home Assistant.

## What works with Grok Bot today

- **Works:** `ha-probe` lists the tools, resources, and prompts your Home Assistant offers. It never calls a tool,
  reads a resource, or changes your home. It is tested with fixtures and local test servers.
  We have not run it against a real Home Assistant installation.
- **Documented, not verified:** connecting Grok Bot to Home Assistant through a remote HTTPS URL.
  A September 2026 Grok Bot community forum report says Grok Bot custom MCP accepts only OAuth with dynamic registration,
  which Home Assistant does not support. If that is still true, this route is blocked today.
  See [Current reported blocker](docs/setup.md#current-reported-blocker).
- **Not provided:** another MCP server, home control, or Bot wake-up from home events.

## Quickstart

You need Python 3.11 or later and [`uv`](https://docs.astral.sh/uv/).

1. **Try it with no home and no account.**

   ```sh
   uv sync --frozen
   uv run ha-probe --fixture fixtures/assist.json
   ```

2. **Check your own Home Assistant, read-only.** First do [Prepare Home Assistant safely](docs/setup.md#2-prepare-home-assistant-safely):
   use a non-admin test user, turn off _Control Home Assistant_, and expose only one harmless entity.

   ```sh
   read -rs HA_TOKEN; export HA_TOKEN
   export HA_MCP_URL=https://<your-home-assistant>/api/mcp/assist
   uv run ha-probe
   ```

3. **Connect Grok Bot (unverified).** Follow the [Remote route](docs/setup.md#4-remote-route).
   Use a personal Bot only, never paste the token into chat, and revoke the token after the test.

## Details

The fixture run prints counts and fixed flags only:

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

The probe enforces these limits in code, and tests check each one:

- It speaks to MCP only through a list-only interface. Its transport refuses any non-discovery method before sending.
- It needs HTTPS. Plain HTTP is accepted only for loopback, or with `--allow-local-http` for hosts whose every
  resolved address is private (LAN, IPv6 ULA, or 100.64.0.0/10). It then connects only to the address it checked.
- It never follows redirects. It refuses responses over 4 MiB, URLs with embedded credentials,
  and Home Assistant APIs other than Assist, which need an administrator.
- It hides names and descriptions, prints one generic line on failure, and never prints the token.

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
