# Grok Gadgets: Home Assistant

Check what Home Assistant's own MCP server would offer your Grok Bot. `ha-probe` lists its
tools, resources and prompts without ever calling a tool or reading a resource. Experimental
alpha: this Home Assistant integration has no verified real-home or Grok Bot result yet. See the
[project status](https://grok-gadgets.pages.dev/doc-docs-public-support-matrix).
Independent project, not affiliated with SpaceXSI or Home Assistant.

> Writing style: ASD-STE100-inspired English. Use short sentences, active verbs and one instruction per step. This is not certified compliance.

## Install from PyPI

The package is on [PyPI](https://pypi.org/project/grok-gadgets-home-assistant/). Install it into a virtual
environment with Python 3.11+. It is an alpha, so name the version or pass `--pre`:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --pre grok-gadgets-home-assistant
.venv/bin/ha-probe --version
```

Each [GitHub release](https://github.com/adidshaft/grok-gadgets-home-assistant/releases) also has the wheel and
`SHA256SUMS`; the PyPI files are the same build.

On an Intel Mac, `cryptography` has no prebuilt wheel and needs a Rust toolchain to build.


## Quickstart

For contributors: use Python 3.11+, Git and [`uv`](https://docs.astral.sh/uv/). This fixture needs no home, account or token.

```sh
git clone https://github.com/adidshaft/grok-gadgets-home-assistant.git
cd grok-gadgets-home-assistant
uv sync --frozen
uv run ha-probe --fixture fixtures/assist.json
```

Expected result (other fixed flags omitted):

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

Next: [prepare a Home Assistant test user](docs/setup.md#2-prepare-home-assistant-safely).


## Why a probe

Home Assistant already has its own MCP server, so Grok Gadgets does not wrap your home. The
probe answers one question safely: what would a Grok Bot see if it connected? It lists tools,
resources and prompts, and never calls a tool or reads a resource.

- Discovery only: redirects refused, responses capped at 4 MiB.
- Household names and descriptions are hidden in the output.
- Fixture output says `"evidence": "fixture tested"`, never a real-home result.

## Try it on your home

The [setup guide](docs/setup.md) walks through a test user with _Control Home Assistant_ off,
[local discovery](docs/setup.md#3-check-discovery-locally), token scope and cleanup.
**A Home Assistant token is a full user credential.** Never paste it into chat or an issue,
and revoke it after testing.

## Grok Bot today

Connecting a Grok Bot needs a reachable HTTPS URL with compatible authentication; check the
[remote-route gate](docs/setup.md#4-remote-route) before you expose a home server. This
package adds no home-control tools and no event-triggered Bot tasks. Issue `HA-004` tracks native Bot compatibility; see also the
[hosting FAQ](https://github.com/adidshaft/grok-gadgets/blob/main/docs/getting-started/hosting.md).

## Learn more

| Topic | Guide |
| --- | --- |
| Set up a real home and remote route | [Setup recipe](docs/setup.md) |
| Sources and open questions | [Feasibility record](docs/feasibility.md) |
| What has been tested | [Verification](docs/verification.md) |
| Run the checks | `uv run ruff check .`, `uv run ruff format --check .`, `uv run python -m unittest discover -s tests -v` |

New gadgets use the [gateway](https://github.com/adidshaft/grok-gadgets-gateway) and SDKs;
this repository is part of [Grok Gadgets](https://github.com/adidshaft/grok-gadgets).

## Community

Share what your home exposes, ask questions and suggest ideas on
[r/GrokGadgets](https://www.reddit.com/r/GrokGadgets/), under the project's
[Code of Conduct](https://github.com/adidshaft/grok-gadgets/blob/main/CODE_OF_CONDUCT.md).
Report bugs through the [issue chooser](https://github.com/adidshaft/grok-gadgets-home-assistant/issues/new/choose).
New here? Pick a [good first issue](https://github.com/adidshaft/grok-gadgets-home-assistant/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
and read [CONTRIBUTING](CONTRIBUTING.md). Keep tokens and household names out of public posts.
Contribute on the `dev` branch; `main` holds tagged stable releases ([branches](CONTRIBUTING.md#branches)).

## License and affiliation

Apache-2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE). [uv.lock](uv.lock) pins the dependencies; the package is also on [PyPI](https://pypi.org/project/grok-gadgets-home-assistant/). Grok Gadgets is an independent open-source
project. It is **not affiliated with, endorsed by or sponsored by SpaceXSI**, which
make Grok and Grok Bot, nor with Home Assistant. We reconstructed the pre-publication commit dates; see the
[history record](https://github.com/adidshaft/grok-gadgets/blob/main/docs/verification/publication-sanitization.md).
