import asyncio
import contextlib
import copy
import gzip
import io
import json
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch

import httpx2
from ha_probe import (
    CLEARTEXT_WARNING,
    MAX_RESPONSE_BYTES,
    GuardedTransport,
    ProbeRefused,
    ReadOnlyDiscovery,
    collect_pages,
    main,
    probe,
    summarize,
    validate_url,
)
from mcp_types import ListToolsResult

FIXTURE = json.loads((Path(__file__).parents[1] / "fixtures/assist.json").read_text())
RESULTS = {
    "initialize": FIXTURE["initialize"],
    "tools/list": FIXTURE["tools"],
    "resources/list": FIXTURE["resources"],
    "prompts/list": FIXTURE["prompts"],
}


def rpc_payload(body, pad=0):
    """A valid JSON-RPC reply; `pad` bytes of JSON whitespace inflate tools/list only."""
    reply = json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": RESULTS[body["method"]]})
    if body["method"] == "tools/list":
        reply = reply[:-1] + " " * pad + "}"
    return reply.encode()


def fixture_handler(seen, pad=0, gzip_tools=False):
    def handler(request):
        seen.append(request)
        if request.method != "POST":
            return httpx2.Response(405)
        body = json.loads(request.content)
        if "id" not in body:
            return httpx2.Response(202)
        headers = {"Content-Type": "application/json"}
        payload = rpc_payload(body, pad)
        if gzip_tools and body["method"] == "tools/list":
            headers["Content-Encoding"] = "gzip"
            payload = gzip.compress(payload)
        return httpx2.Response(200, headers=headers, content=payload)

    return handler


def serve(handler_cls):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


async def stop(server, thread):
    await asyncio.to_thread(server.shutdown)
    server.server_close()
    thread.join(timeout=2)


def redirector(location_for):
    class Redirect(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            self.send_response(307)
            self.send_header("Location", location_for(self.server.server_port))
            self.send_header("Content-Length", "0")
            self.end_headers()

        do_GET = do_POST

    return Redirect


class DiscoveryTests(unittest.TestCase):
    
    def test_version_flag(self):
        output = io.StringIO()
        with (
            patch("sys.argv", ["ha-probe", "--version"]),
            contextlib.redirect_stdout(output),
        ):
            with self.assertRaises(SystemExit) as exc:
                main()
        self.assertEqual(exc.exception.code, 0)
        self.assertIn("0.", output.getvalue())

    def test_fixture_is_honest_and_redacted(self):
        private = copy.deepcopy(FIXTURE)
        private["tools"]["tools"][0]["description"] = "SECRET private home"
        report = summarize(private, "fixture tested")
        self.assertEqual(report["tool_count"], 2)
        self.assertTrue(report["get_live_context_available"])
        self.assertTrue(report["assist_snapshot_available"])
        self.assertFalse(report["grok_verified"])
        self.assertFalse(report["hardware_verified"])
        self.assertNotIn("SECRET", json.dumps(report))

    def test_absent_context_is_supported(self):
        discovery = copy.deepcopy(FIXTURE)
        discovery["tools"] = {"tools": []}
        discovery["resources"] = {"resources": []}
        report = summarize(discovery, "fixture tested")
        self.assertFalse(report["assist_snapshot_available"])
        self.assertFalse(report["get_live_context_available"])

    def test_malformed_schema_rejected(self):
        discovery = copy.deepcopy(FIXTURE)
        discovery["tools"]["tools"][0]["inputSchema"] = "bad"
        with self.assertRaises(ValueError):
            summarize(discovery, "fixture tested")

    def test_duplicate_tools_rejected(self):
        discovery = copy.deepcopy(FIXTURE)
        discovery["tools"]["tools"].append(discovery["tools"]["tools"][0])
        with self.assertRaises(ValueError):
            summarize(discovery, "fixture tested")

    def test_public_plaintext_and_url_secrets_rejected(self):
        for url in [
            "http://example.com/api/mcp",
            "https://u:token@example.com/api/mcp",
            "https://example.com/api/mcp?token=x",
            "https://example.com/api/mcp#secret",
            "https://example.com:99999/api/mcp",
            "https://exa\nmple.com/api/mcp",
            "http://0.0.0.0/api/mcp",
            "https://example.com/api/mcp/admin",
        ]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url, True)

    def test_lan_opt_in(self):
        with self.assertRaises(ValueError):
            validate_url("http://192.168.1.2:8123/api/mcp")
        self.assertEqual(validate_url("http://192.168.1.2:8123/api/mcp", True), "192.168.1.2")
        self.assertEqual(validate_url("http://127.0.0.1:8123/api/mcp"), "127.0.0.1")
        self.assertIsNone(validate_url("https://example.com/api/mcp/assist"))

    def test_http_names_are_resolved_and_every_address_checked(self):
        answers = {
            "localhost": ["127.0.0.1", "::1"],
            "ha.local": ["192.168.1.20"],
            "spoofed.local": ["203.0.113.9"],
            "mixed.local": ["192.168.1.20", "203.0.113.9"],
            "linklocal.local": ["169.254.10.10"],
            "tailnet": ["100.101.102.103"],
            "ula.lan": ["fd12:3456::1"],
            "mapped.lan": ["::ffff:192.168.1.5"],
            "empty.local": [],
        }

        def resolve(host, port):
            if host not in answers:
                raise OSError("no such host")
            return answers[host]

        def check(host, allow):
            return validate_url(f"http://{host}:8123/api/mcp", allow, resolve)

        self.assertEqual(check("localhost", False), "127.0.0.1")
        self.assertEqual(check("ha.local", True), "192.168.1.20")
        self.assertEqual(check("tailnet", True), "100.101.102.103")
        self.assertEqual(check("ula.lan", True), "fd12:3456::1")
        self.assertEqual(check("mapped.lan", True), "::ffff:192.168.1.5")
        for host, allow in [
            ("ha.local", False),
            ("spoofed.local", True),
            ("mixed.local", True),
            ("linklocal.local", True),
            ("empty.local", True),
            ("unknown.local", True),
        ]:
            with self.subTest(host=host), self.assertRaises(ValueError):
                check(host, allow)

    def test_https_names_are_not_resolved(self):
        def resolve(host, port):
            raise AssertionError("HTTPS relies on certificate verification")

        self.assertIsNone(validate_url("https://ha.example/api/mcp", False, resolve))

    def test_only_assist_paths_are_allowed(self):
        for path in ["/api/mcp/custom_api", "/api/mcp/", "/api/other"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_url(f"https://ha.example{path}")

    def test_read_only_facade_exposes_only_discovery(self):
        public = {name for name in dir(ReadOnlyDiscovery) if not name.startswith("_")}
        self.assertEqual(public, {"initialize", "list_tools", "list_resources", "list_prompts"})
        facade = ReadOnlyDiscovery(object())
        for name in ["call_tool", "read_resource", "get_prompt", "complete", "subscribe_resource"]:
            self.assertFalse(hasattr(facade, name), name)
        with self.assertRaises(AttributeError):
            facade.call_tool = None

    def test_cli_never_exposes_exception(self):
        with patch("sys.argv", ["ha-probe"]), patch.dict("os.environ", {}, clear=True):
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                self.assertEqual(main(), 1)
            self.assertNotIn("Traceback", output.getvalue())


class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_sdk_initialize_auth_and_discovery_without_actions(self):
        methods = []
        tokens = []

        def handler(request):
            tokens.append(request.headers.get("Authorization"))
            if request.method != "POST":
                return httpx2.Response(405)
            body = json.loads(request.content)
            methods.append(body["method"])
            if "id" not in body:
                return httpx2.Response(202)
            result = {
                "initialize": FIXTURE["initialize"],
                "tools/list": FIXTURE["tools"],
                "resources/list": FIXTURE["resources"],
                "prompts/list": FIXTURE["prompts"],
            }[body["method"]]
            return httpx2.Response(200, json={"jsonrpc": "2.0", "id": body["id"], "result": result})

        report = await probe(
            "https://ha.example/api/mcp", "test-secret", transport=httpx2.MockTransport(handler)
        )
        self.assertEqual(report["evidence"], "MCP endpoint discovered")
        self.assertEqual(report["tool_count"], 2)
        self.assertEqual(report["tool_calls_performed"], 0)
        self.assertNotIn("tools/call", methods)
        self.assertNotIn("resources/read", methods)
        self.assertTrue(all(token == "Bearer test-secret" for token in tokens))

    async def test_unauthorized_endpoint_is_failure(self):
        with self.assertRaises(Exception):
            await probe(
                "https://ha.example/api/mcp",
                "revoked",
                transport=httpx2.MockTransport(lambda request: httpx2.Response(401)),
            )

    async def test_missing_endpoint_is_failure(self):
        with self.assertRaises(Exception):
            await probe(
                "https://ha.example/api/mcp",
                "test-secret",
                transport=httpx2.MockTransport(lambda request: httpx2.Response(404)),
            )

    async def test_pagination_and_repeated_cursor(self):
        results = iter(
            [
                ListToolsResult.model_validate(
                    {"tools": FIXTURE["tools"]["tools"][:1], "nextCursor": "page2"}
                ),
                ListToolsResult.model_validate({"tools": FIXTURE["tools"]["tools"][1:]}),
            ]
        )
        cursors = []

        async def pages(params=None):
            cursors.append(params.cursor if params else None)
            return next(results)

        self.assertEqual(len((await collect_pages(pages, "tools"))["tools"]), 2)
        self.assertEqual(cursors, [None, "page2"])

        async def repeated(params=None):
            return ListToolsResult.model_validate({"tools": [], "nextCursor": "same"})

        with self.assertRaises(ValueError):
            await collect_pages(repeated, "tools")

    async def test_page_limit_is_failure_not_partial_success(self):
        index = 0

        async def endless(params=None):
            nonlocal index
            index += 1
            return ListToolsResult.model_validate({"tools": [], "nextCursor": str(index)})

        with self.assertRaises(ValueError):
            await collect_pages(endless, "tools")


class GuardTests(unittest.IsolatedAsyncioTestCase):
    async def test_local_http_connects_only_to_the_checked_address(self):
        seen = []
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            report = await probe(
                "http://ha.local:8123/api/mcp",
                "test-secret",
                allow_local_http=True,
                transport=httpx2.MockTransport(fixture_handler(seen)),
                resolve=lambda host, port: ["192.168.1.20"],
            )
        self.assertEqual(report["tool_count"], 2)
        self.assertTrue(seen)
        self.assertEqual({request.url.host for request in seen}, {"192.168.1.20"})
        self.assertEqual({request.headers["Host"] for request in seen}, {"ha.local:8123"})
        self.assertEqual(stderr.getvalue().strip(), CLEARTEXT_WARNING)

    async def test_loopback_http_has_no_cleartext_warning(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            await probe(
                "http://localhost:8123/api/mcp",
                "test-secret",
                transport=httpx2.MockTransport(fixture_handler([])),
                resolve=lambda host, port: ["127.0.0.1"],
            )
        self.assertEqual(stderr.getvalue(), "")

    async def test_redirects_are_never_followed(self):
        cases = {
            "cross-origin": "https://other.example/api/mcp",
            "same-origin": "https://ha.example/api/mcp/assist",
            "http-to-https": "https://127.0.0.1/api/mcp",
        }
        for name, location in cases.items():
            url = (
                "http://127.0.0.1/api/mcp"
                if name == "http-to-https"
                else "https://ha.example/api/mcp"
            )
            seen = []

            def handler(request, location=location, seen=seen):
                seen.append(str(request.url))
                return httpx2.Response(307, headers={"Location": location})

            with self.subTest(name=name):
                with self.assertRaises(Exception):
                    await probe(
                        url,
                        "test-secret",
                        transport=httpx2.MockTransport(handler),
                        resolve=lambda host, port: ["127.0.0.1"],
                    )
                self.assertNotIn(location, seen)
                self.assertEqual(set(seen), {url})

    async def test_cross_origin_redirect_over_sockets_reaches_nobody(self):
        victim_requests = []

        class Victim(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                victim_requests.append(self.headers.get("Authorization"))
                self.send_error(500)

            do_GET = do_POST

        victim, victim_thread = serve(Victim)
        source, source_thread = serve(
            redirector(lambda _port: f"http://127.0.0.1:{victim.server_port}/api/mcp")
        )
        try:
            with self.assertRaises(Exception):
                await probe(f"http://127.0.0.1:{source.server_port}/api/mcp", "test-secret")
            self.assertEqual(victim_requests, [])
        finally:
            await stop(source, source_thread)
            await stop(victim, victim_thread)

    async def test_oversized_declared_response_is_refused(self):
        transport = httpx2.MockTransport(fixture_handler([], pad=MAX_RESPONSE_BYTES))
        with self.assertRaises(Exception):
            await probe("https://ha.example/api/mcp", "test-secret", transport=transport)
        report = await probe(
            "https://ha.example/api/mcp",
            "test-secret",
            transport=httpx2.MockTransport(fixture_handler([], pad=MAX_RESPONSE_BYTES - 4096)),
        )
        self.assertEqual(report["tool_count"], 2)

    async def test_oversized_streamed_response_is_refused(self):
        class Chunked(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *_args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if "id" not in body:
                    self.send_response(202)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                payload = rpc_payload(body, pad=MAX_RESPONSE_BYTES)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                try:
                    for start in range(0, len(payload), 65536):
                        chunk = payload[start : start + 65536]
                        self.wfile.write(b"%x\r\n%s\r\n" % (len(chunk), chunk))
                    self.wfile.write(b"0\r\n\r\n")
                except OSError:
                    pass

        server, thread = serve(Chunked)
        try:
            with self.assertRaises(Exception):
                await probe(f"http://127.0.0.1:{server.server_port}/api/mcp", "test-secret")
        finally:
            await stop(server, thread)

    async def test_compressed_response_is_refused(self):
        seen = []
        with self.assertRaises(Exception):
            await probe(
                "https://ha.example/api/mcp",
                "test-secret",
                transport=httpx2.MockTransport(fixture_handler(seen, gzip_tools=True)),
            )
        self.assertEqual({request.headers["Accept-Encoding"] for request in seen}, {"identity"})

    async def test_transport_refuses_actions_before_sending(self):
        sent = []
        transport = GuardedTransport(
            "https://ha.example/api/mcp", inner=httpx2.MockTransport(fixture_handler(sent))
        )
        async with httpx2.AsyncClient(transport=transport) as client:
            for body in [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "HassTurnOn"},
                },
                {"jsonrpc": "2.0", "id": 2, "method": "resources/read", "params": {"uri": "x"}},
                [{"jsonrpc": "2.0", "id": 3, "method": "tools/list"}],
            ]:
                with self.subTest(body=body), self.assertRaises(ProbeRefused):
                    await client.post("https://ha.example/api/mcp", json=body)
            with self.assertRaises(ProbeRefused):
                await client.post("https://other.example/api/mcp", json={"method": "tools/list"})
            with self.assertRaises(ProbeRefused):
                await client.put("https://ha.example/api/mcp", content=b"")
        self.assertEqual(sent, [])

    async def test_cli_redirect_failure_is_generic(self):
        server, thread = serve(redirector(lambda _port: "http://127.0.0.1:9/api/mcp?leak=1"))
        env = {
            "HA_MCP_URL": f"http://127.0.0.1:{server.server_port}/api/mcp",
            "HA_TOKEN": "probe-secret-token-value",
        }
        try:
            output = io.StringIO()
            with (
                patch("sys.argv", ["ha-probe"]),
                patch.dict("os.environ", env, clear=True),
                contextlib.redirect_stderr(output),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(await asyncio.to_thread(main), 1)
        finally:
            await stop(server, thread)
        self.assertNotIn("probe-secret-token-value", output.getvalue())
        self.assertNotIn("127.0.0.1:9", output.getvalue())
        self.assertIn("Probe failed", output.getvalue())


class LoopbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_socket_transport_against_fixture_server(self):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                self.send_error(405)

            def do_POST(self):
                if self.headers.get("Authorization") != "Bearer fixture-only":
                    self.send_error(401)
                    return
                request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                requests.append(request["method"])
                if "id" not in request:
                    self.send_response(202)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                results = {
                    "initialize": FIXTURE["initialize"],
                    "tools/list": FIXTURE["tools"],
                    "resources/list": FIXTURE["resources"],
                    "prompts/list": FIXTURE["prompts"],
                }
                payload = json.dumps(
                    {"jsonrpc": "2.0", "id": request["id"], "result": results[request["method"]]}
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            report = await probe(f"http://127.0.0.1:{server.server_port}/api/mcp", "fixture-only")
            self.assertEqual(report["tool_count"], 2)
            self.assertEqual(
                set(requests),
                {
                    "initialize",
                    "notifications/initialized",
                    "tools/list",
                    "resources/list",
                    "prompts/list",
                },
            )
            self.assertFalse(report["grok_verified"])
        finally:
            await asyncio.to_thread(server.shutdown)
            server.server_close()
            thread.join(timeout=2)
