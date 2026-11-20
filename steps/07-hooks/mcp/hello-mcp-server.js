#!/usr/bin/env node
// A tiny MCP server with no dependencies (no npm install).
//
// MCP over stdio = JSON-RPC 2.0 messages, one per line, on stdin/stdout.
// VS Code starts this process, sends requests, and reads the replies.
// Anything for humans goes to stderr (stdout is reserved for the protocol).
//
// Tools exposed:
//   get_current_user        -> who is at the keyboard, and their local time
//   lookup_teammate(name)   -> a teammate's role, city, language and local time

const fs = require("fs");
const os = require("os");
const path = require("path");
const readline = require("readline");
const { execSync } = require("child_process");

const TEAM = JSON.parse(fs.readFileSync(path.join(__dirname, "team.json"), "utf8"));

// ---------------------------------------------------------------- tools ----
function partOfDay(hour) {
  return hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
}

function timeIn(timeZone) {
  const fmt = new Intl.DateTimeFormat("en-GB", { timeZone, hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
  const local_time = fmt.format(new Date());
  return { local_time, part_of_day: partOfDay(parseInt(local_time.slice(0, 2), 10)) };
}

const TOOLS = [
  {
    name: "get_current_user",
    description: "Returns the name of the person using this computer and their local time of day.",
    inputSchema: { type: "object", properties: {} },
    run() {
      let name = "";
      try { name = execSync("git config user.name", { encoding: "utf8" }).trim(); } catch {}
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      return { name, username: os.userInfo().username, timezone: tz, ...timeIn(tz) };
    },
  },
  {
    name: "lookup_teammate",
    description: "Looks up a teammate by first name. Returns their role, city, preferred language and current local time.",
    inputSchema: {
      type: "object",
      properties: { name: { type: "string", description: "The teammate's first name, e.g. Priya" } },
      required: ["name"],
    },
    run({ name }) {
      const person = TEAM.find((p) => p.name.toLowerCase() === String(name).trim().toLowerCase());
      if (!person) return { found: false, known_teammates: TEAM.map((p) => p.name) };
      return { found: true, ...person, ...timeIn(person.timezone) };
    },
  },
];

// ------------------------------------------------------------- protocol ----
function send(msg) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", ...msg }) + "\n");
}

function handle(req) {
  const { id, method, params = {} } = req;
  switch (method) {
    case "initialize":
      return send({
        id,
        result: {
          protocolVersion: params.protocolVersion || "2025-06-18",
          capabilities: { tools: {} },
          serverInfo: { name: "hello-mcp", version: "1.0.0" },
        },
      });
    case "ping":
      return send({ id, result: {} });
    case "tools/list":
      return send({
        id,
        result: { tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) },
      });
    case "tools/call": {
      const tool = TOOLS.find((t) => t.name === params.name);
      if (!tool) return send({ id, error: { code: -32602, message: `Unknown tool: ${params.name}` } });
      console.error(`[hello-mcp] ${params.name}(${JSON.stringify(params.arguments || {})})`);
      try {
        const data = tool.run(params.arguments || {});
        return send({ id, result: { content: [{ type: "text", text: JSON.stringify(data) }] } });
      } catch (err) {
        return send({ id, result: { isError: true, content: [{ type: "text", text: String(err) }] } });
      }
    }
    default:
      // Notifications (no id), e.g. "notifications/initialized", need no reply.
      if (id !== undefined) send({ id, error: { code: -32601, message: `Method not found: ${method}` } });
  }
}

readline.createInterface({ input: process.stdin }).on("line", (line) => {
  if (!line.trim()) return;
  try { handle(JSON.parse(line)); }
  catch (err) { send({ id: null, error: { code: -32700, message: "Parse error" } }); }
});
console.error("[hello-mcp] server started (node)");
