# Home Assistant setup recipe

## Run the local fixture first

Run the [README fixture commands](../README.md#run-the-fixture-first).
The fixture contains manually written MCP discovery data. It is not a capture from a Home Assistant release.
The probe initializes the connection and lists tools, resources, and prompts.
It does not execute tools, read resources, or change a light.

Local fixture tests need no public hosting. For a real home, the Home Assistant operator
runs the upstream MCP server. Grok/xAI hosts Grok Bot.
The proposed cloud connection goes directly to Home Assistant. It does not use the Grok Gadgets gateway.
See the [hosting FAQ](https://github.com/adidshaft/grok-gadgets/blob/main/docs/getting-started/hosting.md)
for who hosts each process and who operates a tunnel.

## Prepare a real home

**This procedure has not been performed here.** It is based on the [4 October 2026 feasibility record](feasibility.md).
Check the actual installation and client interface before an authorized home test.
These steps are separate from the account-free quickstart.

1. Record the Home Assistant version and the selected light or sensor. Record its current state.
2. Choose a harmless test light. Do not expose locks, alarms, garage doors, or other devices that could cause harm during this test.
3. In Home Assistant, open Settings → Devices & services. Add Model Context Protocol Server.
4. Select Assist. Use the exposed-entity page to expose only the selected entities.
5. Check that ordinary dashboard controls still work. Entity exposure does not restrict every Home Assistant API through token scopes.
6. Create a dedicated test user without administrator access, if practical.
7. Get its access token from the Home Assistant profile. Store it privately in `HA_TOKEN`. Do not use command arguments or committed configuration.
8. Set `HA_MCP_URL` to the full endpoint reachable by your probe, for example `http://homeassistant.local:8123/api/mcp/assist`.
9. Run `uv run ha-probe`. For an authorized LAN HTTP test, add `--allow-local-http`.
10. Check the evidence level, counts, and context-tool/resource availability in the output.

Prefer OAuth for a compatible Bot client. The CLI probe does not implement interactive OAuth.

By default, the probe permits non-HTTPS connections only on loopback.
`--allow-local-http` also permits private IP addresses and `.local` hostnames.
It never permits a public HTTP endpoint. It does not change exposure or firewall settings.

This LAN URL is for the local probe. Grok cloud cannot reach it directly.

The probe hides household names and server descriptions. A 401 error indicates an authentication check is necessary.
A 404 error suggests an integration or selected API mismatch. The CLI returns a generic error without exception text.

## Test an existing Grok Bot

**Account access and network reachability remain pending.**
Use the Bot's desktop plugin or custom-MCP setup, if available.
The proposed connection uses publicly reachable HTTPS directly to the authorized Home Assistant MCP endpoint.
Do not put a Mac-local URL or path in a cloud Command configuration.
Do not publish a personal Bot as a Team Bot only to follow Team Bots documentation.

Before you activate a connection, verify these requirements:

- The endpoint uses TLS and authentication.
- The Bot supports the selected transport.
- OAuth uses a Home Assistant-compatible client ID and callback, or the client supports the required secret/bearer configuration.
- The endpoint is reachable through an authorized cloud connection.

Get the exact Grok settings and callback URI from the actual UI.
Do not invent an OAuth identifier or a ready-to-import Grok configuration.

If an authorized test uses a tunnel, the home operator configures it and keeps it running.
The tunnel provider or operator controls that route. Grok is its client.
A tunnel forwards requests. It does not add Home Assistant authentication.
Keep the Home Assistant host running for this route.

The gadget gateway's missing remote service is tracked under `HARD-GROK-REMOTE-001`.
That work does not replace Home Assistant's existing MCP service.
This route still needs its own authentication, reachability, and native Bot checks under `HA-004`.

After account authorization, perform these checks:

1. Discover tools. Check that excluded entities remain unavailable.
2. Request the selected sensor or light state. Compare the result and timestamp with the Home Assistant dashboard.
3. Ask to turn on the harmless light. Change a supported value. Restore the original state.
4. Save the tool name, arguments, and result with private data removed. Record physical observations separately.
5. Disconnect or revoke test access. Check that the Bot reports failure or unconfirmed operation.
6. Restore access. Check recovery.
7. Repeat state and control checks with the same Bot on available mobile clients. Record exact versions.
8. Close the Bot client. Check that ordinary Home Assistant controls and automations still work.

Desktop success does not prove mobile support. Shutting down the Home Assistant host stops its service.

Do not advertise automatic Bot wake-up from a button event. The upstream MCP server provides no notification stream in this dated recipe.
Home automations and supported notification channels require a separate authorized investigation.
The probe does not monitor your home continuously.

## Record evidence

Save a report outside Git. Remove private data. Include:

- Test date and component commit.
- Home Assistant and client versions.
- Transport and authentication method. Never include the token.
- URL category: local or approved remote.
- Each check and its result.

Record local fixture acceptance, remote security, native Grok invocation, physical effects,
and independent reproduction separately. A reachable URL does not prove any tool invocation.
Fixture checks need no cloud dependency or subscription.

## Remove the experiment

1. Revoke its token or OAuth grant.
2. Remove the Bot plugin.
3. Restore the previous entity exposure.
4. Remove the Home Assistant MCP integration only if nobody else uses it.

See [feasibility](feasibility.md) for sources and unresolved authentication questions.
Do not expose an endpoint or spend money only to run this recipe.
