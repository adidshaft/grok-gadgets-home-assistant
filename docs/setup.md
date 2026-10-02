# Home Assistant setup recipe

## Local fixture first

Run the [README fixture commands](../README.md#run-the-fixture-first). Fixture data is hand-authored representative MCP discovery data, not captured from a real HA release. The probe only initializes and lists tools/resources/prompts; it never executes a tool, reads a resource, or changes a light.

## Prepare a real home (not performed here)

This is a dated preparation recipe based on the [4 October 2026 feasibility record](feasibility.md). Verify the actual installation/client interface when an authorized home test is scheduled. These steps are separate from the account-free quickstart.

1. Record HA version, selected test light/sensor, and current state. Choose a harmless test light; leave locks, alarms, garage doors and other consequential entities unexposed for this acceptance run.
2. In HA Settings → Devices & services add Model Context Protocol Server. Select Assist, then expose only the chosen entities through the exposed-entity page. Confirm ordinary dashboard controls still work. Do not interpret exposure as a token scope limiting every HA API.
3. Create a dedicated non-administrator test user where practical. Use its access token from HA profile for the diagnostic client; keep it in `HA_TOKEN`, never command arguments or committed configuration. OAuth is preferable for a compatible Bot client; the CLI probe does not implement interactive OAuth.
4. On your own machine, set `HA_MCP_URL` to the full endpoint, e.g. `http://homeassistant.local:8123/api/mcp/assist`. Set `HA_TOKEN` privately, then run `uv run ha-probe`. Non-HTTPS is accepted only for loopback by default; a LAN HTTP URL requires `--allow-local-http`, which accepts private IP addresses or `.local` hostnames and never a public HTTP endpoint. It changes no exposure or firewall settings.
5. Check the output's evidence level, counts, context-tool/resource availability. It suppresses household names and server-provided descriptions. A 401 indicates token/auth review; 404 suggests integration/selected API mismatch. The CLI returns a generic failure without leaking exception text.

## Existing Grok Bot experiment (pending account and reachability)

Use the existing Bot's desktop plugin/custom-MCP setup if present. Proposed route: Remote HTTPS pointing directly at the already authorized HA endpoint. Do not paste the Mac's local URL/path into a cloud Command configuration. Do not publish the personal Bot as a Team Bot solely to follow the Team Bots documentation.

Before activating a connection, confirm: endpoint TLS/authentication; the Bot's actual supported transport; HA-compatible OAuth client ID/callback or supported secret/bearer configuration; and authorized cloud reachability. Exact Grok settings and callback URI must come from the actual UI. No guessed OAuth identifier or fabricated ready-to-import Grok JSON is included.

After account authorization, use this acceptance sequence:

1. Discover tools and confirm excluded entities remain unavailable.
2. Ask for chosen sensor/light state; compare with HA dashboard and timestamp.
3. Ask to turn on the harmless light, change a supported value, then restore its original state. Save redacted tool name/arguments/result and separately record visible physical observations.
4. Disconnect/revoke test access; confirm the Bot reports failure or unconfirmed operation. Restore access and check recovery.
5. Repeat state/control from the same Bot on available mobile clients. Record exact versions; do not infer device support from desktop success.
6. Leave ordinary HA dashboard/automations functional. Close Bot client and check HA controls; shutting down the HA host stops its service.

Do not advertise button-triggered Bot wake: upstream HA MCP provides no notification stream. Home automations and supported notification channels can be investigated as a separate authorized feature. The probe itself performs no ongoing monitoring.

## Evidence and rollback

Save a redacted report outside Git containing date, component commit, HA/client versions, transport, auth method (never token), URL category (local/approved remote), and each result. Separate fixture tested, Grok verified, hardware verified and independently reproduced. If removing the experiment, revoke its token/OAuth grant, remove the Bot plugin, restore entity exposure, and remove the HA MCP integration only if nobody else uses it. No cloud dependency or subscription is required for fixture checks.

Source and unresolved auth details: [feasibility](feasibility.md). Do not expose an endpoint or spend money merely to run this recipe.
