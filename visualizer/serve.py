#!/usr/bin/env python3
"""Serve the flow visualizer and stream the agent's hook events to it.

Run it from the step folder you have open in VS Code (07 or 08):

    python ../../visualizer/serve.py

then open http://localhost:8765 in a browser, or inside VS Code:
Command Palette -> "Simple Browser: Show" -> http://localhost:8765

Python standard library only. It only listens on localhost.
"""
import argparse
import json
import pathlib
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = pathlib.Path(__file__).resolve().parent


def make_handler(log_file):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(HERE), **kwargs)

        def do_GET(self):
            url = urlparse(self.path)
            if url.path != "/api/events":
                return super().do_GET()
            # Return every event after line number `after`.
            after = int(parse_qs(url.query).get("after", ["0"])[0])
            lines = log_file.read_text(encoding="utf-8").splitlines() if log_file.exists() else []
            events = []
            for line in lines[after:]:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            body = json.dumps({"next": len(lines), "events": events, "log": str(log_file),
                               "log_exists": log_file.exists()}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # keep the terminal quiet
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", default=".", help="step folder whose hook log to watch (default: current folder)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true", help="don't open a browser window")
    args = parser.parse_args()

    log_file = pathlib.Path(args.workspace).resolve() / ".github" / "hooks" / "logs" / "audit.jsonl"
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(log_file))
    url = f"http://localhost:{args.port}/#live"
    print(f"Flow visualizer: {url}")
    print(f"Watching:        {log_file}" + ("" if log_file.exists() else "  (not created yet; send a chat message)"))
    print("Press Ctrl+C to stop.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
