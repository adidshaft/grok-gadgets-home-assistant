import asyncio
import contextlib
import copy
import io
import json
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch

import httpx2
from ha_probe import collect_pages, main, probe, summarize, validate_url
from mcp_types import ListToolsResult

FIXTURE = json.loads((Path(__file__).parents[1] / "fixtures/assist.json").read_text())


class DiscoveryTests(unittest.TestCase):
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
        self.assertTrue(validate_url("http://192.168.1.2:8123/api/mcp", True))
        self.assertTrue(validate_url("http://localhost:8123/api/mcp"))
        self.assertTrue(validate_url("https://example.com/api/mcp/assist"))

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
