import { z } from "zod";
import { readFileSync, existsSync } from "fs";
import path from "path";
import { readNpc, listFiles } from "../lib/vault-reader.js";
import { craftNpcTokenPrompt } from "../lib/gemini-director.js";
import { generateImage } from "../lib/imagen-generator.js";
import { slugify, getAssetPath, getRelativeAssetPath, ASSETS_DIR } from "../lib/file-utils.js";
import { blockedResponse, successResponse } from "../lib/tool-responses.js";

function readPortraitAsReference(npcName) {
  const slug = slugify(npcName);
  const npcsDir = path.join(ASSETS_DIR, "npcs");
  const portraitPath = path.join(npcsDir, `${slug}-portrait.png`);

  if (!existsSync(portraitPath)) return null;

  const ext = ".png";
  const mimeTypes = { ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg" };
  const data = readFileSync(portraitPath, { encoding: "base64" });
  return { name: npcName, mimeType: mimeTypes[ext] || "image/png", data };
}

export function register(server) {
  server.tool(
    "generate_npc_token",
    "Generate a circular VTT token from an NPC's existing portrait",
    {
      npc_name: z.string().describe("Name of the NPC as it appears in the vault"),
      style_hint: z.string().optional().describe("Optional style direction to augment the default token style"),
    },
    async ({ npc_name, style_hint }) => {
      const warnings = [];

      const npc = readNpc(npc_name);
      if (!npc) {
        const available = listFiles("04 - NPCs");
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({ error: `NPC "${npc_name}" not found`, available }, null, 2) }],
        };
      }

      const ref = readPortraitAsReference(npc_name);
      if (!ref) {
        const slug = slugify(npc_name);
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({ error: `No portrait found at assets/npcs/${slug}-portrait.png`, suggestion: "Generate a portrait first using generate_npc_portrait" }, null, 2) }],
        };
      }

      const appearance = npc.sections.appearance || "";
      const geminiResult = await craftNpcTokenPrompt({
        name: npc_name,
        race: npc.frontmatter.race || "",
        className: npc.frontmatter.class || "",
        appearance,
        styleHint: style_hint,
      });

      const slug = slugify(npc_name);
      const filename = `${slug}-token.png`;
      const outputPath = getAssetPath("npcs", filename);
      const relativePath = getRelativeAssetPath("npcs", filename);

      const imgResult = await generateImage(geminiResult.prompt, {
        aspectRatio: "1:1",
        outputPath,
        referenceImages: [ref],
      });

      if (!imgResult.success) {
        return blockedResponse(imgResult, "Try adding a style_hint like 'simplified token art' or 'clean headshot token'");
      }

      return successResponse({ imagePath: relativePath, prompt: geminiResult.prompt, reasoning: geminiResult.reasoning, warnings });
    }
  );
}
