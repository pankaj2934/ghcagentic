#!/usr/bin/env node
// Shows the raw MCP conversation that VS Code has with the server.
// Run it from this folder:   node mcp/demo-client.js
// Handy on stage, and works even when MCP is switched off in VS Code by policy.
const { spawn } = require("child_process");
const path = require("path");

const server = spawn(process.execPath, [path.join(__dirname, "hello-mcp-server.js")], { stdio: ["pipe", "pipe", "inherit"] });

const requests = [
  { id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "demo-client", version: "1.0.0" } } },
  { method: "notifications/initialized" },
  { id: 2, method: "tools/list" },
  { id: 3, method: "tools/call", params: { name: "get_current_user", arguments: {} } },
  { id: 4, method: "tools/call", params: { name: "lookup_teammate", arguments: { name: "Priya" } } },
];

let buffer = "";
let pending = requests.filter((r) => r.id !== undefined).length;
server.stdout.on("data", (chunk) => {
  buffer += chunk;
  let i;
  while ((i = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, i);
    buffer = buffer.slice(i + 1);
    console.log("\n⬅️  server:", JSON.stringify(JSON.parse(line), null, 2));
    if (--pending === 0) server.stdin.end();
  }
});

for (const r of requests) {
  const msg = { jsonrpc: "2.0", ...r };
  console.log("\n➡️  client:", JSON.stringify(msg));
  server.stdin.write(JSON.stringify(msg) + "\n");
}
