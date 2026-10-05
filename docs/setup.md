# Home Assistant setup recipe

**Nothing in this guide has been performed against a real Home Assistant installation or a real Grok Bot.**
It is based on the current [Home Assistant MCP Server documentation](https://www.home-assistant.io/integrations/mcp_server/)
and the [xAI Team Bots documentation](https://docs.x.ai/grok-bot/team-bots), both read on 5 October 2026,
and on the [4 October 2026 feasibility record](feasibility.md). Every Grok step is unverified.

The route goes directly from Grok Bot to Home Assistant's own MCP server. It does not use the
Grok Gadgets gateway or a second server. The Home Assistant operator runs the server and any tunnel.
Grok/xAI hosts Grok Bot. See the [hosting FAQ](https://github.com/adidshaft/grok-gadgets/blob/main/docs/getting-started/hosting.md).

## 1. Run the local fixture first

Run the [README quickstart](../README.md#quickstart) step 1. The fixture is hand-written MCP
discovery data, not a capture from a Home Assistant release. The probe initializes the connection and
lists tools, resources, and prompts. It cannot execute tools, read resources, or change a light.

## 2. Prepare Home Assistant safely

1. Record the Home Assistant version. Choose one harmless test light or sensor and record its state.
   Do not expose locks, alarms, garage doors, heaters, or anything that could cause harm.
2. **Create a dedicated test user without administrator access. This is required.**
   Use it only for this test.
3. In Settings → Devices & services, add **Model Context Protocol Server** and select **Assist**.
4. **Turn off _Control Home Assistant_** in the integration options for the first test.
   Then MCP clients can read exposed entities but cannot control them.
5. On the exposed-entities page, expose only the selected test entities.
6. Sign in as the test user. In Profile → Security, create a long-lived access token.
   Store it only in your shell environment as `HA_TOKEN` (for example `read -rs HA_TOKEN; export HA_TOKEN`).
   Never put it in a command argument, a file in Git, or chat text.

### What the token can do

A long-lived access token is a **full credential for that user**, not an MCP-only key.
It works with Home Assistant's REST and WebSocket APIs too.
Entity exposure and _Control Home Assistant_ limit only what the MCP Assist tools offer.
They do not limit what someone with the token can do through the other APIs.
Home Assistant has no per-entity permissions for non-admin users in its UI, so expect the token to reach
everything the test user can reach in the dashboard. A non-admin user reduces the damage. It does not remove it.

Revoke the token (Profile → Security) as soon as the test ends.

### Which URL paths the probe accepts

The probe accepts only `/api/mcp` and `/api/mcp/assist`. This is intentional.
Home Assistant also serves `/api/mcp/<api_id>` for other LLM APIs, but those require an
administrator user. This guide keeps the test user non-admin, so the probe refuses those paths.

## 3. Check discovery locally

```sh
export HA_MCP_URL=http://homeassistant.local:8123/api/mcp/assist
uv run ha-probe --allow-local-http
```

Use your server port. From Home Assistant 2026.8, Home Assistant OS defaults to port 80, so
the URL is `http://homeassistant.local/api/mcp/assist`. Container installations keep 8123.

Check the counts and the `get_live_context_available` and `assist_snapshot_available` flags.
The probe prints only counts and fixed flags. It hides household names and descriptions.
A failure prints one generic line. A 401 usually means a wrong or revoked token.
A 404 usually means the integration is not set up.

How the probe treats plain HTTP:

- Without `--allow-local-http`, plain HTTP is accepted only if the host resolves to loopback.
- With `--allow-local-http`, the probe resolves the name first. Every resolved address must be loopback,
  a private LAN address (10/8, 172.16/12, 192.168/16), an IPv6 ULA (fc00::/7), or CGNAT/Tailscale
  (100.64.0.0/10). Public and link-local addresses are refused. The probe then connects only to
  the address it checked, so a later DNS or mDNS answer cannot send the token elsewhere.
- For any non-loopback HTTP, the probe prints a one-line warning: the token travels unencrypted on your network.
- A public plain-HTTP endpoint is always refused.

The probe also refuses every redirect, any response larger than 4 MiB, compressed responses,
and any MCP method other than discovery.

This LAN URL is only for the local probe. Grok Bot runs in the cloud and cannot reach it.

## 4. Remote route

A cloud Grok Bot needs a public **HTTPS** URL for Home Assistant. Pick one option.
**Never port-forward Home Assistant's plain-HTTP port (80 or 8123) to the internet.**
Either option exposes the whole Home Assistant login and API on the internet, not only MCP.
Keep Home Assistant updated and use strong passwords with multi-factor authentication for every user.

### Option A: Home Assistant Cloud (recommended by Home Assistant)

1. Enable remote access in Settings → Home Assistant Cloud. This is a paid Nabu Casa subscription.
   Do not subscribe only to run this recipe.
2. Use the remote URL it shows: `https://<id>.ui.nabu.casa`.
   Home Assistant Cloud handles TLS and the canonical hostname for you. You do not need reverse-proxy settings.

### Option B: Cloudflare Tunnel or your own reverse proxy

1. Run the tunnel (for example `cloudflared` or its Home Assistant add-on) or a TLS reverse proxy.
   Point it at Home Assistant on the local network. Do not open an inbound port on your router.
2. In Settings → System → Network, set **External URL** to exactly the public hostname,
   for example `https://ha.example.com`. The hostname Grok uses must match this.
   A mismatch breaks OAuth discovery, because Home Assistant then returns relative `issuer` paths.
3. Let Home Assistant trust forwarded headers from the proxy only. In Settings → System → Network →
   HTTP server, turn on **Trust X-Forwarded-For** and add only the proxy's address to **Trusted proxies**.
   Examples: `127.0.0.1` when the proxy or `cloudflared` runs on the same host, or the add-on network
   your add-on's documentation names. Use a network address for a range, for example `172.30.33.0/24`.
   Home Assistant blocks proxied requests until these are set. Releases before 2026.8 used the
   `http:` block (`use_x_forwarded_for`, `trusted_proxies`) in `configuration.yaml` instead. See
   [HTTP reverse-proxy settings](https://www.home-assistant.io/integrations/http/#reverse-proxies).
4. A tunnel forwards traffic. It does not add authentication. Home Assistant's own login and
   token checks still protect the endpoint. Putting Cloudflare Access in front would also block Grok
   unless Grok can send its credentials. See [Current reported blocker](#current-reported-blocker).

### First: probe the same HTTPS URL

Before you touch Grok, run the probe against the exact URL Grok will use:

```sh
export HA_MCP_URL=https://<external-host>/api/mcp/assist
uv run ha-probe
```

Do not use `--allow-local-http` here. Continue only if the probe reports `"evidence": "MCP endpoint discovered"`.
This proves only that the URL, TLS, and token work from your computer. It does not prove that Grok can connect.

### Then: add the server to a personal Grok Bot (unverified)

**Use a personal Bot only.** A Team Bot shares its plugins and secrets with every teammate's
conversation and with its Slack channels. xAI says: "The Bot can use every secret in any teammate's
conversation, so treat a secret as access you are giving the whole team." A Home Assistant token in a
Team Bot gives every teammate and every Slack channel the Bot is in access to your home.

1. In the personal Bot, add a custom MCP server of type **Remote HTTPS**.
2. URL: `https://<external-host>/api/mcp/assist`.
3. Choose one way to authenticate:
   - **Bearer token.** Send the header `Authorization: Bearer <token>`, with the value taken from a
     Bot secret. Never type the token into chat or into anything the model can read.
     If the form cannot take the header value from a secret, stop. Do not paste the token anywhere else.
   - **OAuth.** Home Assistant uses IndieAuth-style client IDs. The client ID is the client's own base URL.
     Home Assistant requires the OAuth `redirect_uri` to have the same scheme and domain as that client ID.
     Home Assistant does **not** support RFC 7591 Dynamic Client Registration.
     If Grok requires dynamic registration, OAuth will fail. Use the bearer route instead.
     Copy any client ID or callback only from the actual Grok UI. Do not guess them.
4. Ask the Bot to list the Home Assistant tools. Then go to [Check the connection](#5-check-the-connection).

### Current reported blocker

Not verified here. On 17 and 25 September 2026, a Cursor staff reply in a
[Cursor forum thread](https://forum.cursor.com/t/grok-bot-custom-mcp-oauth-fails-before-sign-in-redirect-uri-not-allowed/171877)
reported the following about Grok Bot's custom MCP:

- Grok Bot custom MCP connectors authenticate only through OAuth with Dynamic Client Registration.
- There is no safe way to enter a secret header value.

If this is still true, neither route works with Home Assistant today. OAuth fails because Home Assistant has
no registration endpoint. Bearer fails because the token cannot be stored safely.
Do not work around this by giving the token to the Bot in chat or in a tool call.
Native Bot compatibility stays an open gate under `HA-004`.

## 5. Check the connection

Do these checks only after the probe passes and the account owner authorizes the test.

1. Discover tools. Check that entities you did not expose stay unavailable.
2. Ask for the test sensor or light state. Compare it and its timestamp with the Home Assistant dashboard.
3. Only after the read-only checks pass: turn on _Control Home Assistant_, then ask to switch the
   harmless light. Restore its original state.
4. Save the tool name, arguments, and result with private data removed. Record physical observations separately.
5. Revoke the token or OAuth grant. Check that the Bot reports a failure, not a success.
6. Repeat on the mobile apps you use, with the same Bot. Record exact versions.
   Desktop success does not prove mobile support.
7. Close the Bot. Check that the dashboard and automations still work.

Home Assistant's MCP server sends no notifications, so a button press cannot wake the Bot through it.
The probe does not monitor your home.

## Record evidence

Save a report outside Git with private data removed:

- Test date and component commit.
- Home Assistant and Grok Bot client versions.
- Remote option (A or B) and authentication method. Never the token.
- Each check and its result.

Record local probe results, remote reachability, native Grok calls, and physical effects separately.
A reachable URL does not prove that Grok called a tool.

## Remove the experiment

1. Revoke the token or OAuth grant.
2. Remove the custom MCP server from the Bot.
3. Turn off the tunnel or remote access if you enabled it only for this test.
4. Restore the previous entity exposure. Delete the test user.
5. Remove the MCP Server integration only if nobody else uses it.
