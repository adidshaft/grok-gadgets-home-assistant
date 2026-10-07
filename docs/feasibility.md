# Feasibility record — 4 October 2026

Historical documentation review. The current software first step and tested limits are in the [README](../README.md) and [verification](verification.md). This record is not a fresh platform or account test.

For current project hosting boundaries, use the canonical
[hosting FAQ](https://github.com/adidshaft/grok-gadgets/blob/main/docs/getting-started/hosting.md).
Home Assistant's operator runs its upstream MCP server. The cloud Bot needs a publicly
reachable HTTPS route and compatible authentication. Native Bot compatibility remains unverified.
The separate gadget gateway's remote-service gate does not mean Home Assistant lacks an MCP server.

Evidence: official documentation review only; no Grok account, HA installation, or phone was connected. Source dates below are publication/update dates where provided. Recheck at actual onboarding.

| Question | Finding and primary source | Remaining experiment |
| --- | --- | --- |
| Existing Bot extension | [Team Bots](https://docs.x.ai/grok-bot/team-bots) (updated Oct 2): custom MCP offers Remote HTTPS and Command, with OAuth or Bot credential for remote. Documentation is strongest for Team Bots. | Confirm the existing personal Bot exposes the same setup and can discover tools. Do not create a different developer-API conversation. |
| Process location | [Overview](https://docs.x.ai/grok-bot/overview) (updated Sep 21): persistent cloud computer; account Bots share its filesystem. A local Mac path is unavailable there. Team Bot conversations use owner/teammate/shared cloud computers according to context. | Record actual computer and network reachability; Command installed on cloud requires its own reachable HA URL. |
| Home authentication/hosting | [HA MCP](https://www.home-assistant.io/integrations/mcp_server/) (retrieved Oct 4): stateless Streamable HTTP, `/api/mcp`; selected LLM API, exposed entities, bearer token or OAuth. OAuth uses URL client IDs, not RFC7591 registration. | Confirm Grok supports HA's URL client ID and callback scheme/domain. No exact Grok callback/client ID is documented in the reviewed material. Remote HTTPS must be authenticated and reachable by cloud. No tunnel created. |
| Mobile | [Mobile](https://docs.x.ai/grok-bot/mobile) (updated Sep 21): same Bots/connectors/cloud computer on iOS, iPadOS, Android; advanced setup can require desktop. Push rollout is account dependent. | Record desktop/iOS/Android versions and real tool calls. Documentation parity is not verification. |
| Outside events | [Routines](https://docs.x.ai/grok-bot/skills-routines-and-automations) (updated Sep 14): supported integrations may trigger routines, e.g. Slack/GitHub. HA MCP docs explicitly exclude notifications and sampling. | Arbitrary HA button/webhook wake into the existing Bot is not established. Polling/event retention in gadget gateway is distinct from Bot wake or mobile push. |

Update, 5 October 2026 (documentation review only): the Home Assistant MCP page still describes IndieAuth URL client IDs, no RFC 7591 registration endpoint, the _Control Home Assistant_ option, and `/api/mcp/<api_id>` requiring an administrator for non-Assist APIs. A public Grok Bot community support thread (number 171877; staff replies 17 and 25 September 2026) reports that Grok Bot custom MCP authenticates only through OAuth with Dynamic Client Registration, and that there is no safe way to set a secret header. If that holds, neither OAuth nor bearer authentication currently works between Grok Bot and Home Assistant. This is a community report, not a primary xAI document, and was not tested here.


Decision: reuse Home Assistant's MCP server directly for its exposed Assist capabilities. A second server would duplicate authentication, entity exposure, and actions. This repository supplies discovery diagnostics, fixtures, and an onboarding recipe. No adapter is currently required. If real onboarding reveals a gap, capture the exact failure before designing one.

Upstream code reference: [integration setup](https://github.com/home-assistant/core/blob/dev/homeassistant/components/mcp_server/__init__.py), retrieved Oct 4. `dev` is moving evidence, not a pinned tested installation. This repository does not vendor HA code.

Limits: entity/vendor capability coverage depends on Assist and the selected API. Listing a tool or receiving an action result is not proof of physical effect. Resource snapshots are observations, not durable event streams. No universal household compatibility, unsolicited Bot messaging, push-button wake, or Grok certification is claimed.
