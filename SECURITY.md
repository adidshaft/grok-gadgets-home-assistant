# Security

Keep access tokens, private household state, entity names and exploit details out of public issues.

After activation, use [GitHub private vulnerability reporting](https://github.com/adidshaft/grok-gadgets-home-assistant/security/advisories/new) when enabled. If that channel is unavailable, email [adidshaft@kyokasuigetsu.xyz](mailto:adidshaft@kyokasuigetsu.xyz). Include the affected commit, transport/category, reproduction and expected impact privately; omit tokens and agree how to share sensitive evidence safely. No response-time guarantee is promised.

The alpha probe initializes MCP and lists tools/resources/prompts. It never executes tools or reads resources, but discovery can still encounter private entity names. Its public report exposes only counts/capability flags; keep full endpoint responses private. Use a dedicated least-privilege test user where appropriate, restrict entity exposure, and revoke experiment credentials when finished. Entity exposure is not automatically a scope restriction on all Home Assistant APIs.

The default URL checks reject plaintext public endpoints and embedded credentials. The explicit `--allow-local-http` option is only for a separately authorized local/private endpoint; it does not configure TLS, authentication, a firewall, tunnel or cloud reachability. Interactive OAuth is unimplemented in the probe. Actual home access and physical actions need their own authorization and verification.

Follow the hub's [disclosure process](https://github.com/adidshaft/grok-gadgets/blob/main/SECURITY.md). Installation/discovery support uses [Support](SUPPORT.md), with redacted summaries rather than secrets.
