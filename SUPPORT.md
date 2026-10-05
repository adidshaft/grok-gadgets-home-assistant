# Support

Run the [fixture quickstart](README.md#quickstart) before you diagnose a real installation.

| Symptom | First check | Expected outcome |
| --- | --- | --- |
| `ha-probe` is unavailable | Run `uv sync --frozen`, then use `uv run ha-probe` | The local console entry point runs |
| Fixture cannot be found | Run from this repository root and use `fixtures/assist.json` | Hand-authored discovery validates |
| Generic probe failure | Check URL, authentication, integration and reachability privately | No token/exception/household data is printed |
| Plaintext endpoint rejected | Use HTTPS, or `--allow-local-http` only for an authorized local test. Every address the name resolves to must be private | Public, link-local, and mixed-answer plaintext endpoints remain rejected |
| Redirect or oversized response | Use the final `/api/mcp/assist` URL directly; check what the proxy returns | The probe never follows redirects and refuses responses over 4 MiB |
| Tool/context availability differs | Record HA/client versions and a redacted summary | Establish a specific compatibility issue rather than assume universal coverage |
| Bot cannot reach a local URL | Establish the actual Bot process location and approved reachable route | No assumption that a cloud client can access your local computer |

The CLI gives a generic error for real-endpoint failures. Inspect 401 or 404 errors privately to identify authentication or path problems.
Do not copy full remote error messages into public logs.

Use the [issue chooser](https://github.com/adidshaft/grok-gadgets-home-assistant/issues/new/choose) to report a defect. Include:

- Component commit.
- Host, Python, and client versions.
- Exact command, with private values removed.
- Evidence source: fixture or real installation.
- Expected result and actual result.

Use [r/GrokGadgets](https://www.reddit.com/r/GrokGadgets/) for discussion.
Use [Security](SECURITY.md) for vulnerabilities.
Send private conduct reports to [adidshaft@kyokasuigetsu.xyz](mailto:adidshaft@kyokasuigetsu.xyz).

See [setup](docs/setup.md) for the real-home procedure. Get separate authorization before you run it.
Actual Home Assistant, OAuth/client compatibility, desktop/mobile behavior, and physical devices remain unverified.
An independent person has not reproduced the results. The probe does not monitor your home or wake a Bot when an event occurs.
