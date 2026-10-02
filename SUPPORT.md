# Support

Run the [fixture quickstart](README.md#run-the-fixture-first) before diagnosing a real installation.

| Symptom | First check | Expected outcome |
| --- | --- | --- |
| `ha-probe` is unavailable | Run `uv sync --frozen --python 3.11`, then use `uv run ha-probe` | The local console entry point runs |
| Fixture cannot be found | Run from this repository root and use `fixtures/assist.json` | Hand-authored discovery validates |
| Generic probe failure | Check URL, authentication, integration and reachability privately | No token/exception/household data is printed |
| Plaintext endpoint rejected | Use HTTPS, or the explicit local/private HTTP option only for an authorized local test | Public plaintext endpoints remain rejected |
| Tool/context availability differs | Record HA/client versions and a redacted summary | Establish a specific compatibility issue rather than assume universal coverage |
| Bot cannot reach a local URL | Establish the actual Bot process location and approved reachable route | No assumption that a cloud client can access your local computer |

The CLI intentionally gives a generic real-endpoint failure. A private 401/404 investigation can distinguish authentication from integration/path problems; do not paste full remote error bodies into public logs.

For a reproducible defect, include component commit, host/Python/client versions, exact command, fixture versus real-installation evidence, and expected/observed result. Use the [planned issue chooser](https://github.com/adidshaft/grok-gadgets-home-assistant/issues/new/choose) after activation; [local issues](planning/issues.json) remain authoritative before migration. Discussion uses [r/GrokGadgets](https://www.reddit.com/r/GrokGadgets/). Security reports use [Security](SECURITY.md); private conduct reports use [adidshaft@kyokasuigetsu.xyz](mailto:adidshaft@kyokasuigetsu.xyz).

See [setup](docs/setup.md) for the separately gated home procedure. Actual Home Assistant, OAuth/client compatibility, desktop/mobile behavior, physical devices and independent-human reproduction remain open. The probe does not run ongoing monitoring or wake a Bot on an outside event.
