const { McpServer } = require("@modelcontextprotocol/sdk/server/mcp.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");

async function main() {
  const server = new McpServer({ name: "test", version: "1.0.0" });
  server.tool("ping", "test tool", {}, async () => ({ content: [{ type: "text", text: "pong" }] }));
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
main();
