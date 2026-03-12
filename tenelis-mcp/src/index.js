import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { register as registerNpcPortrait } from "./tools/generate-npc-portrait.js";
import { register as registerLocationArt } from "./tools/generate-location-art.js";
import { register as registerScene } from "./tools/generate-scene.js";
import { register as registerPartyPortrait } from "./tools/generate-party-portrait.js";

const server = new McpServer({
  name: "tenelis-imagegen",
  version: "1.0.0",
});

registerNpcPortrait(server);
registerLocationArt(server);
registerScene(server);
registerPartyPortrait(server);

const transport = new StdioServerTransport();
await server.connect(transport);
