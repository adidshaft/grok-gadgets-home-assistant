"""Read-only MCP discovery. No home actions or resource content are requested."""

import argparse
import asyncio
import ipaddress
import json
import logging
import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlsplit
from importlib.metadata import version

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp_types import InitializeResult, ListPromptsResult, ListResourcesResult, ListToolsResult
from mcp_types import PaginatedRequestParams

CONTEXT_URI = "homeassistant://assist/context-snapshot"
MAX_PAGES = 10
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
# Other /api/mcp/<api_id> endpoints require an administrator; the probe stays on Assist.
ALLOWED_PATHS = {"/api/mcp", "/api/mcp/assist"}
DISCOVERY_METHODS = {
    "initialize",
    "notifications/initialized",
    "notifications/cancelled",
    "ping",
    "tools/list",
    "resources/list",
    "prompts/list",
}
LOCAL_NETWORKS = [
    ipaddress.ip_network(net)
    for net in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10", "fc00::/7")
]
CLEARTEXT_WARNING = "Warning: HA_TOKEN travels unencrypted over local HTTP; prefer HTTPS."


def _system_resolve(host: str, port: int) -> list[str]:
    return [info[4][0] for info in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)]


def _classify(address: str) -> str:
    ip = ipaddress.ip_address(address.split("%", 1)[0])
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    if ip.is_loopback:
        return "loopback"
    if any(ip in net for net in LOCAL_NETWORKS):
        return "local"
    return "public"


def validate_url(url: str, allow_local_http: bool = False, resolve=_system_resolve) -> str | None:
    """Reject unsafe endpoints. For HTTP, return the one resolved address the probe must use.

    Every address a plain-HTTP name resolves to must be loopback, or with
    allow_local_http a private LAN, ULA or CGNAT/Tailscale address. Connecting
    only to the returned address prevents a later DNS answer from redirecting the token.
    """
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
        or parsed.path not in ALLOWED_PATHS
    ):
        raise ValueError("Use a full HA Assist MCP URL without embedded credentials")
    # Accessing port validates malformed and out-of-range values.
    port = parsed.port
    if parsed.scheme == "https":
        return None
    try:
        addresses = resolve(parsed.hostname, port or 80)
        kinds = {_classify(address) for address in addresses}
    except (OSError, ValueError) as error:
        raise ValueError("Could not resolve the HTTP host to a local address") from error
    allowed = {"loopback", "local"} if allow_local_http else {"loopback"}
    if not addresses or not kinds <= allowed:
        raise ValueError("HTTPS required; LAN HTTP requires explicit --allow-local-http")
    return addresses[0]


class ProbeRefused(Exception):
    """The guarded transport refused a request or response."""


class _CappedStream(httpx2.AsyncByteStream):
    def __init__(self, stream, limit: int):
        self._stream = stream
        self._limit = limit

    async def __aiter__(self):
        total = 0
        async for chunk in self._stream:
            total += len(chunk)
            if total > self._limit:
                raise ProbeRefused("Response exceeds size limit")
            yield chunk

    async def aclose(self):
        await self._stream.aclose()


class GuardedTransport(httpx2.AsyncBaseTransport):
    """Wire-level guard: one origin, pinned address, discovery methods, bounded responses.

    Redirects are never followed, including same-origin and http-to-https ones.
    """

    def __init__(self, url: str, pinned_address: str | None = None, inner=None):
        self._origin = httpx2.URL(url)
        self._pinned = pinned_address
        self._inner = inner or httpx2.AsyncHTTPTransport(trust_env=False)

    async def handle_async_request(self, request):
        url = request.url
        if (url.scheme, url.host, url.port) != (
            self._origin.scheme,
            self._origin.host,
            self._origin.port,
        ):
            raise ProbeRefused("Request outside the configured origin")
        if request.method == "POST":
            try:
                message = json.loads(await request.aread())
            except ValueError as error:
                raise ProbeRefused("Unreadable request body") from error
            if not isinstance(message, dict):
                raise ProbeRefused("Batch requests are not sent")
            if "method" in message and message["method"] not in DISCOVERY_METHODS:
                raise ProbeRefused("Only discovery methods are sent")
        elif request.method not in {"GET", "DELETE"}:
            raise ProbeRefused("Unexpected HTTP method")
        if self._pinned is not None:
            request.url = url.copy_with(host=self._pinned)
        response = await self._inner.handle_async_request(request)
        try:
            if 300 <= response.status_code < 400:
                raise ProbeRefused("Redirects are not followed")
            if response.headers.get("content-encoding", "identity").lower() != "identity":
                raise ProbeRefused("Compressed responses are not accepted")
            length = response.headers.get("content-length")
            if length is not None and (not length.isdigit() or int(length) > MAX_RESPONSE_BYTES):
                raise ProbeRefused("Response exceeds size limit")
        except ProbeRefused:
            await response.aclose()
            raise
        return httpx2.Response(
            response.status_code,
            headers=response.headers,
            stream=_CappedStream(response.stream, MAX_RESPONSE_BYTES),
            extensions=response.extensions,
        )

    async def aclose(self):
        await self._inner.aclose()


class ReadOnlyDiscovery:
    """The only MCP surface the probe uses: initialize plus list_* discovery."""

    __slots__ = ("_session",)

    def __init__(self, session: ClientSession):
        self._session = session

    async def initialize(self) -> InitializeResult:
        return await self._session.initialize()

    async def list_tools(self, params=None) -> ListToolsResult:
        return await self._session.list_tools(params=params)

    async def list_resources(self, params=None) -> ListResourcesResult:
        return await self._session.list_resources(params=params)

    async def list_prompts(self, params=None) -> ListPromptsResult:
        return await self._session.list_prompts(params=params)


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


async def probe(
    url: str,
    token: str,
    *,
    allow_local_http: bool = False,
    transport=None,
    resolve=_system_resolve,
) -> dict:
    pinned = await asyncio.to_thread(validate_url, url, allow_local_http, resolve)
    if not token or any(char in token for char in "\r\n"):
        raise ValueError("HA_TOKEN must be set without newlines")
    if pinned is not None and _classify(pinned) != "loopback":
        print(CLEARTEXT_WARNING, file=sys.stderr)
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {token}", "Accept-Encoding": "identity"},
        timeout=10,
        follow_redirects=False,
        trust_env=False,
        transport=GuardedTransport(url, pinned, transport),
    ) as http:
        async with streamable_http_client(url, http_client=http) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=10) as raw_session:
                session = ReadOnlyDiscovery(raw_session)
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
    parser.add_argument(
        "--version", action="version", version=version("grok-gadgets-home-assistant")
    )
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
