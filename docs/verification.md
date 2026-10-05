# Verification

Current newcomer rehearsal: [standalone documentation verification](verification/launch.md). It identifies the source state, checks, installed-wheel result and package-license inspection.

## Review fixes — 5 October 2026

Environment: macOS arm64, uv 0.12.3, MCP SDK 2.3.0. The full CI sequence passed on CPython 3.11.15, 3.12.13,
3.13.5 and 3.14.7: frozen install, Ruff lint/format, 26 unittest cases, wheel/sdist build, and the fixture probe.
New tests cover name resolution and address pinning for local HTTP, the 4 MiB response cap (declared and streamed),
refused compression, refused cross-origin, same-origin and http-to-https redirects, the list-only facade,
and transport refusal of `tools/call` and `resources/read`. They use mock resolvers, mock transports and loopback
servers only. No Home Assistant, Grok Bot, tunnel or device was used. The remote-route recipe in
[setup](setup.md) is documentation only and unverified. Hosted CI has not run these changes.

## Historical local alpha checkpoint — 4 October 2026

Environment: macOS arm64; uv-managed CPython 3.11.15. Official MCP SDK 2.3.0; dependency versions/hashes in uv.lock. These are client and fixture tests, not a running Home Assistant installation.

Passed: frozen install, ruff lint/format, 13 unittest cases, wheel/sdist build, wheel installation into a separate temporary venv and fixture CLI run. Transport evidence includes authenticated initialize, tool/resource/prompt pagination through SDK MockTransport and a real ephemeral loopback HTTP fixture server. 401/404 fail; malformed/duplicate schemas/cursors fail; plaintext public/embedded-credential URLs fail; errors omit exceptions. No tools/call or resources/read requests occurred. Endpoint test counts are assertions, not HA device claims.

Fixture CLI reports 2 tools, 1 resource, 1 prompt, no tool execution, and false Grok/hardware flags. Fixtures are hand-authored and are not a captured compatibility matrix for an installed HA version.

Open gates: actual Home Assistant version/user/entity behavior; Grok personal-Bot custom-MCP setup, OAuth compatibility and network reachability; desktop/mobile and physical observation; independent reproduction; GitHub/publication approval. See HA-004 and setup recipe.

Rollback: uninstall the Python package/venv. Fixture checks provision no home or cloud service. No remote exists; prepared CI and protections are inactive.
