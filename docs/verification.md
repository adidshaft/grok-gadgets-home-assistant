# Local alpha verification — 2026-10-04

Environment: macOS arm64; uv-managed CPython 3.11.15. Official MCP SDK 2.3.0; dependency versions/hashes in uv.lock. These are client and fixture tests, not a running Home Assistant installation.

Passed: frozen install, ruff lint/format, 13 unittest cases, wheel/sdist build, wheel installation into a separate `/tmp/grok-ha-clean-alpha` venv and fixture CLI run. Transport evidence includes authenticated initialize, tool/resource/prompt pagination through SDK MockTransport and a real ephemeral loopback HTTP fixture server. 401/404 fail; malformed/duplicate schemas/cursors fail; plaintext public/embedded-credential URLs fail; errors omit exceptions. No tools/call or resources/read requests occurred. Endpoint test counts are assertions, not HA device claims.

Fixture CLI reports 2 tools, 1 resource, 1 prompt, no tool execution, and false Grok/hardware flags. Fixtures are hand-authored and are not a captured compatibility matrix for an installed HA version.

Open gates: actual Home Assistant version/user/entity behavior; Grok personal-Bot custom-MCP setup, OAuth compatibility and network reachability; desktop/mobile and physical observation; independent reproduction; GitHub/publication approval. See HA-004 and setup recipe.

Rollback: uninstall the Python package/venv. Fixture checks provision no home or cloud service. No remote exists; prepared CI and protections are inactive.
