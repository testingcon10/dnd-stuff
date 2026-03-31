import { z } from "zod";
import { readFileSync, existsSync, readdirSync } from "fs";
import path from "path";
import { readNpc, listFiles } from "../lib/vault-reader.js";
import { craftNpcTurnaroundPrompt } from "../lib/gemini-director.js";
import { generateImage } from "../lib/imagen-generator.js";
import { slugify, getAssetPath, getRelativeAssetPath, ASSETS_DIR } from "../lib/file-utils.js";
import { blockedResponse, successResponse } from "../lib/tool-responses.js";

function findNpcReference(npcName) {
  const slug = slugify(npcName);
  const npcsDir = path.join(ASSETS_DIR, "npcs");
  const mimeTypes = { ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg" };

  // Check for token first (webp), then portrait (png)
  const candidates = [
    // Try exact name match (token style: Aya.webp)
    ...readdirSync(npcsDir)
      .filter(f => f.replace(/\.[^.]+$/, "").toLowerCase() === npcName.toLowerCase())
      .map(f => path.join(npcsDir, f)),
    // Try slug-portrait match
    path.join(npcsDir, `${slug}-portrait.png`),
    // Try slug-token match
    path.join(npcsDir, `${slug}-token.png`),
  ];

  for (const filePath of candidates) {
    if (existsSync(filePath)) {
      const ext = path.extname(filePath).toLowerCase();
      const data = readFileSync(filePath, { encoding: "base64" });
      return { name: npcName, mimeType: mimeTypes[ext] || "image/png", data };
    }
  }
  return null;
}

export function register(server) {
  server.tool(
    "generate_npc_turnaround",
    "Generate a character turnaround reference sheet for an NPC showing front, 3/4, and back views",
    {
      npc_name: z.string().describe("Name of the NPC as it appears in the vault"),
      style_hint: z.string().optional().describe("Optional style direction to augment the default turnaround style"),
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

      const ref = findNpcReference(npc_name);
      if (!ref) {
        warnings.push("No existing portrait or token found as reference - generating from text description only");
      }

      const appearance = npc.sections.appearance || "";
      if (!appearance.trim()) warnings.push("NPC has no appearance description - Gemini will infer from other context");

      const geminiResult = await craftNpcTurnaroundPrompt({
        name: npc_name,
        race: npc.frontmatter.race || "",
        className: npc.frontmatter.class || "",
        faction: npc.frontmatter.faction || "",
        appearance,
        background: npc.sections.background || "",
        notableItems: npc.sections.notableItems || "",
        styleHint: style_hint,
      });

      const slug = slugify(npc_name);
      const filename = `${slug}-turnaround.png`;
      const outputPath = getAssetPath("npcs", filename);
      const relativePath = getRelativeAssetPath("npcs", filename);

      const referenceImages = ref ? [ref] : [];
      const imgResult = await generateImage(geminiResult.prompt, {
        aspectRatio: "16:9",
        outputPath,
        referenceImages,
      });

      if (!imgResult.success) {
        return blockedResponse(imgResult, "Try adding a style_hint like 'simplified concept art' or 'clean linework turnaround'");
      }

      return successResponse({ imagePath: relativePath, prompt: geminiResult.prompt, reasoning: geminiResult.reasoning, warnings });
    }
  );
}
