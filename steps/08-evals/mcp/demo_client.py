#!/usr/bin/env python3
"""Shows the raw MCP conversation that VS Code has with the server.

Run it from the step folder:   python mcp/demo_client.py
Handy on stage, and works even when MCP is switched off in VS Code by policy.
"""
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")  # emoji-safe on Windows consoles

server_path = pathlib.Path(__file__).parent / "hello_mcp_server.py"
server = subprocess.Popen(
    [sys.executable, str(server_path)],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1,
)

requests = [
    {"id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                                  "clientInfo": {"name": "demo-client", "version": "1.0.0"}}},
    {"method": "notifications/initialized"},
    {"id": 2, "method": "tools/list"},
    {"id": 3, "method": "tools/call", "params": {"name": "get_current_user", "arguments": {}}},
    {"id": 4, "method": "tools/call", "params": {"name": "lookup_teammate", "arguments": {"name": "Priya"}}},
]

for req in requests:
    msg = {"jsonrpc": "2.0", **req}
    print("\n➡️  client:", json.dumps(msg, ensure_ascii=False), flush=True)
    server.stdin.write(json.dumps(msg) + "\n")
    server.stdin.flush()
    if "id" in req:  # requests get a reply; notifications don't
        reply = json.loads(server.stdout.readline())
        print("⬅️  server:", json.dumps(reply, indent=2, ensure_ascii=False), flush=True)

server.stdin.close()
server.wait()
