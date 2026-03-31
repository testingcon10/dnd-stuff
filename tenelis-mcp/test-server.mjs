import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({ name: "test", version: "1.0.0" });
server.tool("ping", "test tool", {}, async () => ({ content: [{ type: "text", text: "pong" }] }));
const transport = new StdioServerTransport();
await server.connect(transport);
