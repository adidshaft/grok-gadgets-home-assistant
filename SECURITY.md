# Security

Keep access tokens, private household state, entity names and exploit details out of public issues.

After activation, use [GitHub private vulnerability reporting](https://github.com/adidshaft/grok-gadgets-home-assistant/security/advisories/new) when enabled. If that channel is unavailable, email [adidshaft@kyokasuigetsu.xyz](mailto:adidshaft@kyokasuigetsu.xyz). Include the affected commit, transport/category, reproduction and expected impact privately; omit tokens and agree how to share sensitive evidence safely. No response-time guarantee is promised.

The alpha probe initializes MCP and lists tools/resources/prompts. A list-only session facade and a guarded transport refuse every other MCP method before it is sent. Discovery can still encounter private entity names. Its public report exposes only counts/capability flags; keep full endpoint responses private. A dedicated non-admin test user is required. Restrict entity exposure, and revoke experiment credentials when finished. A long-lived token is a full user credential for Home Assistant's REST and WebSocket APIs; entity exposure limits only the MCP tools. Never put it in a Team Bot, where every teammate and Slack channel could use it.

The default URL checks reject plaintext public endpoints and embedded credentials. The explicit `--allow-local-http` option is only for a separately authorized local/private endpoint. It resolves the name, requires every address to be private, pins the connection to that address, and prints a cleartext warning. It does not configure TLS, authentication, a firewall, tunnel or cloud reachability. The probe never follows redirects and refuses responses over 4 MiB. Interactive OAuth is unimplemented in the probe. Actual home access and physical actions need their own authorization and verification.

Follow the hub's [disclosure process](https://github.com/adidshaft/grok-gadgets/blob/main/SECURITY.md). Installation/discovery support uses [Support](SUPPORT.md), with redacted summaries rather than secrets.
