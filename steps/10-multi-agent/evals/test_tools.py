#!/usr/bin/env python3
"""Layer 1: deterministic evals for the agent's TOOLS (no model involved).

    python evals/test_tools.py

Tests the MCP server, the guard hook and the whoami script. They're quick and
give the same result every time, so run them on every change, and in CI
(see .github/workflows/tool-evals.yml at the repo root).
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

STEP = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable


class McpClient:
    """Just enough of an MCP client to talk to hello_mcp_server.py over stdio."""

    def __init__(self):
        self.proc = subprocess.Popen(
            [PY, str(STEP / "mcp" / "hello_mcp_server.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8",
        )
        self.next_id = 0

    def request(self, method, params=None):
        self.next_id += 1
        msg = {"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params or {}}
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def call(self, tool, **arguments):
        reply = self.request("tools/call", {"name": tool, "arguments": arguments})
        return json.loads(reply["result"]["content"][0]["text"])

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=5)


class TestMcpServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mcp = McpClient()
        cls.init = cls.mcp.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                  "clientInfo": {"name": "tests", "version": "1"}})

    @classmethod
    def tearDownClass(cls):
        cls.mcp.close()

    def test_handshake(self):
        self.assertEqual(self.init["result"]["serverInfo"]["name"], "hello-mcp")
        self.assertIn("tools", self.init["result"]["capabilities"])

    def test_tools_are_listed_with_descriptions_and_schemas(self):
        tools = {t["name"]: t for t in self.mcp.request("tools/list")["result"]["tools"]}
        self.assertEqual(set(tools), {"get_current_user", "lookup_teammate"})
        for tool in tools.values():
            self.assertGreater(len(tool["description"]), 20, "the model picks tools by description")
            self.assertEqual(tool["inputSchema"]["type"], "object")
        self.assertEqual(tools["lookup_teammate"]["inputSchema"]["required"], ["name"])

    def test_lookup_known_teammate(self):
        priya = self.mcp.call("lookup_teammate", name="Priya")
        self.assertTrue(priya["found"])
        self.assertEqual(priya["language"], "Hindi")
        self.assertIn(priya["part_of_day"], {"morning", "afternoon", "evening"})

    def test_lookup_ignores_case_and_spaces(self):
        self.assertTrue(self.mcp.call("lookup_teammate", name="  kENJI ")["found"])

    def test_unknown_teammate_lists_known_ones(self):
        bob = self.mcp.call("lookup_teammate", name="Bob")
        self.assertFalse(bob["found"])
        self.assertIn("Priya", bob["known_teammates"])

    def test_current_user(self):
        me = self.mcp.call("get_current_user")
        self.assertTrue(me["username"])
        self.assertRegex(me["local_time"], r"^\d\d:\d\d$")

    def test_unknown_tool_is_an_error(self):
        reply = self.mcp.request("tools/call", {"name": "launch_rockets", "arguments": {}})
        self.assertIn("error", reply)


class TestGuardHook(unittest.TestCase):
    def run_hook(self, command):
        event = {"hook_event_name": "PreToolUse", "tool_name": "run_in_terminal", "tool_input": {"command": command}}
        with tempfile.TemporaryDirectory() as scratch:  # keep test events out of the real audit log
            result = subprocess.run(
                [PY, str(STEP / ".github" / "hooks" / "scripts" / "audit.py")],
                input=json.dumps(event), capture_output=True, text=True, encoding="utf-8", cwd=scratch,
            )
        self.assertEqual(result.returncode, 0)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def test_blocks_deletes(self):
        for command in ["rm -rf cards", "del cards\\x.md", "Remove-Item cards -Recurse"]:
            with self.subTest(command=command):
                decision = self.run_hook(command)
                self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_allows_harmless_commands(self):
        for command in ["git status", "python --version", "echo format"]:
            with self.subTest(command=command):
                self.assertIsNone(self.run_hook(command))


class TestWhoamiScript(unittest.TestCase):
    def test_prints_json_with_expected_fields(self):
        scripts = STEP / ".github" / "skills" / "identify-user" / "scripts"
        if sys.platform == "win32":
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(scripts / "whoami.ps1")]
        elif shutil.which("bash"):
            cmd = ["bash", str(scripts / "whoami.sh")]
        else:
            self.skipTest("no shell available")
        out = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
        self.assertEqual(set(out), {"name", "username", "os", "local_time", "part_of_day"})
        self.assertIn(out["part_of_day"], {"morning", "afternoon", "evening"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
