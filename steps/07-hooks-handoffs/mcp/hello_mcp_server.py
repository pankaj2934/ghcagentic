#!/usr/bin/env python3
"""A tiny MCP server with no dependencies (standard library only).

Same tools as hello-mcp-server.js. Use this one if Node isn't installed.

MCP over stdio = JSON-RPC 2.0 messages, one per line, on stdin/stdout.
Anything for humans goes to stderr (stdout is reserved for the protocol).
"""
import datetime
import getpass
import json
import pathlib
import subprocess
import sys

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

TEAM = json.loads((pathlib.Path(__file__).parent / "team.json").read_text(encoding="utf-8"))


def part_of_day(hour):
    return "morning" if hour < 12 else "afternoon" if hour < 18 else "evening"


def time_in(tz_name=None, utc_offset=None):
    now = datetime.datetime.now().astimezone()
    if tz_name:
        try:
            now = datetime.datetime.now(ZoneInfo(tz_name))
        except Exception:
            # Windows Python usually has no time-zone database (it needs the
            # 'tzdata' package), so fall back to the fixed offset in team.json.
            if utc_offset:
                sign = -1 if utc_offset.startswith("-") else 1
                hours, minutes = utc_offset.lstrip("+-").split(":")
                delta = datetime.timedelta(hours=int(hours), minutes=int(minutes)) * sign
                now = datetime.datetime.now(datetime.timezone(delta))
    return {"local_time": now.strftime("%H:%M"), "part_of_day": part_of_day(now.hour)}


def get_current_user(_args):
    try:
        name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    except Exception:
        name = ""
    return {"name": name, "username": getpass.getuser(), **time_in()}


def lookup_teammate(args):
    wanted = str(args.get("name", "")).strip().lower()
    for person in TEAM:
        if person["name"].lower() == wanted:
            return {"found": True, **person, **time_in(person["timezone"], person.get("utc_offset"))}
    return {"found": False, "known_teammates": [p["name"] for p in TEAM]}


TOOLS = {
    "get_current_user": {
        "description": "Returns the name of the person using this computer and their local time of day.",
        "inputSchema": {"type": "object", "properties": {}},
        "run": get_current_user,
    },
    "lookup_teammate": {
        "description": "Looks up a teammate by first name. Returns their role, city, preferred language and current local time.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "The teammate's first name, e.g. Priya"}},
            "required": ["name"],
        },
        "run": lookup_teammate,
    },
}


def send(msg):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", **msg}) + "\n")
    sys.stdout.flush()


def handle(req):
    rid, method, params = req.get("id"), req.get("method"), req.get("params") or {}
    if method == "initialize":
        send({"id": rid, "result": {
            "protocolVersion": params.get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "hello-mcp", "version": "1.0.0"},
        }})
    elif method == "ping":
        send({"id": rid, "result": {}})
    elif method == "tools/list":
        send({"id": rid, "result": {"tools": [
            {"name": n, "description": t["description"], "inputSchema": t["inputSchema"]} for n, t in TOOLS.items()
        ]}})
    elif method == "tools/call":
        tool = TOOLS.get(params.get("name"))
        if not tool:
            send({"id": rid, "error": {"code": -32602, "message": f"Unknown tool: {params.get('name')}"}})
            return
        print(f"[hello-mcp] {params['name']}({json.dumps(params.get('arguments') or {})})", file=sys.stderr)
        try:
            data = tool["run"](params.get("arguments") or {})
            send({"id": rid, "result": {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}})
        except Exception as err:
            send({"id": rid, "result": {"isError": True, "content": [{"type": "text", "text": str(err)}]}})
    elif rid is not None:
        send({"id": rid, "error": {"code": -32601, "message": f"Method not found: {method}"}})
    # else: a notification such as notifications/initialized, which needs no reply


if __name__ == "__main__":
    # Always talk UTF-8, whatever the Windows console code page is.
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("[hello-mcp] server started (python)", file=sys.stderr)
    for line in sys.stdin:
        if line.strip():
            try:
                handle(json.loads(line))
            except json.JSONDecodeError:
                send({"id": None, "error": {"code": -32700, "message": "Parse error"}})
