"""Read-only MCP discovery. No home actions or resource content are requested."""

import argparse
import asyncio
import ipaddress
import json
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp_types import InitializeResult, ListPromptsResult, ListResourcesResult, ListToolsResult
from mcp_types import PaginatedRequestParams

CONTEXT_URI = "homeassistant://assist/context-snapshot"
MAX_PAGES = 10


def validate_url(url: str, allow_local_http: bool = False) -> str:
    """Prevent accidental token transmission to plaintext public endpoints."""
    if any(ord(char) < 33 for char in url):
        raise ValueError("Invalid URL")
    parsed = urlsplit(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"/api/mcp", "/api/mcp/assist"}
    ):
        raise ValueError("Use a full HA Assist MCP URL without embedded credentials")
    # Accessing port validates malformed and out-of-range values.
    _ = parsed.port
    host = parsed.hostname.lower()
    try:
        address = ipaddress.ip_address(host)
        loopback = address.is_loopback
        private = address.is_private and not address.is_unspecified and not address.is_reserved
    except ValueError:
        loopback = host == "localhost"
        private = host.endswith(".local")
    if parsed.scheme == "http" and not (loopback or (allow_local_http and private)):
        raise ValueError("HTTPS required; LAN HTTP requires explicit --allow-local-http")
    return url


def summarize(discovery: dict, evidence: str) -> dict:
    """Validate actual MCP models, returning only counts and fixed known capabilities."""
    if evidence not in {"fixture tested", "MCP endpoint discovered"}:
        raise ValueError("Unknown evidence level")
    initialized = InitializeResult.model_validate(discovery["initialize"])
    tools = ListToolsResult.model_validate(discovery["tools"]).tools
    resources = ListResourcesResult.model_validate(discovery["resources"]).resources
    prompts = ListPromptsResult.model_validate(discovery["prompts"]).prompts
    tool_names = [tool.name for tool in tools]
    resource_uris = [str(resource.uri) for resource in resources]
    if len(tool_names) != len(set(tool_names)) or len(resource_uris) != len(set(resource_uris)):
        raise ValueError("Duplicate discovery entries")
    return {
        "evidence": evidence,
        "protocol_version": initialized.protocol_version,
        "tool_count": len(tools),
        "resource_count": len(resources),
        "prompt_count": len(prompts),
        "get_live_context_available": "GetLiveContext" in tool_names,
        "assist_snapshot_available": CONTEXT_URI in resource_uris,
        "tool_calls_performed": 0,
        "resource_reads_performed": 0,
        "grok_verified": False,
        "hardware_verified": False,
    }


async def collect_pages(method, field: str) -> dict:
    """Bounded pagination; never silently report a partial list as complete."""
    entries = []
    cursor = None
    seen = set()
    for _ in range(MAX_PAGES):
        result = await method(params=PaginatedRequestParams(cursor=cursor) if cursor else None)
        payload = result.model_dump(mode="json", by_alias=True)
        entries.extend(payload[field])
        cursor = payload.get("nextCursor")
        if not cursor:
            return {field: entries}
        if cursor in seen:
            raise ValueError("Repeated pagination cursor")
        seen.add(cursor)
    raise ValueError("Discovery exceeds page limit")


async def probe(url: str, token: str, *, allow_local_http: bool = False, transport=None) -> dict:
    validate_url(url, allow_local_http)
    if not token or any(char in token for char in "\r\n"):
        raise ValueError("HA_TOKEN must be set without newlines")
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
        follow_redirects=False,
        trust_env=False,
        transport=transport,
    ) as http:
        async with streamable_http_client(url, http_client=http) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=10) as session:
                initialized = await session.initialize()
                caps = initialized.capabilities
                discovery = {
                    "initialize": initialized.model_dump(mode="json", by_alias=True),
                    "tools": await collect_pages(session.list_tools, "tools")
                    if caps.tools is not None
                    else {"tools": []},
                    "resources": await collect_pages(session.list_resources, "resources")
                    if caps.resources is not None
                    else {"resources": []},
                    "prompts": await collect_pages(session.list_prompts, "prompts")
                    if caps.prompts is not None
                    else {"prompts": []},
                }
                return summarize(discovery, "MCP endpoint discovered")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, help="Hand-authored discovery fixture; no network")
    parser.add_argument("--allow-local-http", action="store_true")
    args = parser.parse_args()
    # Third-party exception logs may include URLs/response bodies; never disclose them here.
    logging.disable(logging.CRITICAL)
    try:
        if args.fixture:
            report = summarize(json.loads(args.fixture.read_text()), "fixture tested")
        else:
            report = asyncio.run(
                probe(
                    os.environ.get("HA_MCP_URL", ""),
                    os.environ.get("HA_TOKEN", ""),
                    allow_local_http=args.allow_local_http,
                )
            )
    except Exception:
        print(
            "Probe failed. Check URL, authentication, integration and reachability privately.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(report, indent=2))
    return 0
