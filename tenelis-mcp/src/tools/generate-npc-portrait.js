import { z } from "zod";
import { readNpc, readLocation, listFiles } from "../lib/vault-reader.js";
import { craftNpcPrompt } from "../lib/gemini-director.js";
import { generateImage } from "../lib/imagen-generator.js";
import { embedImage } from "../lib/vault-embedder.js";
import { slugify, getAssetPath, getRelativeAssetPath } from "../lib/file-utils.js";

export function register(server) {
  server.tool(
    "generate_npc_portrait",
    "Generate a portrait for an NPC using vault context and AI image generation",
    {
      npc_name: z.string().describe("Name of the NPC as it appears in the vault"),
      style_hint: z.string().optional().describe("Optional style direction to override/augment the default art style"),
      aspect_ratio: z.string().default("3:4").describe("Image aspect ratio (default 3:4 for portraits)"),
    },
    async ({ npc_name, style_hint, aspect_ratio }) => {
      const warnings = [];

      const npc = readNpc(npc_name);
      if (!npc) {
        const available = listFiles("04 - NPCs");
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({ error: `NPC "${npc_name}" not found`, available }, null, 2) }],
        };
      }

      let locationData = null;
      const locName = npc.frontmatter.location;
      if (locName && typeof locName === "string" && locName.trim()) {
        const loc = readLocation(locName);
        if (loc) {
          locationData = {
            description: loc.sections.description || "",
            locationType: loc.frontmatter.location_type || "",
          };
        } else {
          warnings.push(`Location "${locName}" not found in vault, skipping location context`);
        }
      }

      const appearance = npc.sections.appearance || "";
      const personality = npc.sections.personality || "";
      if (!appearance.trim()) warnings.push("NPC has no appearance description - Gemini will infer from other context");

      const geminiResult = await craftNpcPrompt({
        name: npc_name,
        race: npc.frontmatter.race || "",
        className: npc.frontmatter.class || "",
        faction: npc.frontmatter.faction || "",
        appearance,
        personality,
        location: locName || "",
        locationData,
        styleHint: style_hint,
      });

      const slug = slugify(npc_name);
      const filename = `${slug}-portrait.png`;
      const outputPath = getAssetPath("npcs", filename);
      const relativePath = getRelativeAssetPath("npcs", filename);

      const imgResult = await generateImage(geminiResult.prompt, { aspectRatio: aspect_ratio, outputPath });

      if (!imgResult.success) {
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({
            error: "Image generation blocked by content filter",
            blockedPrompt: imgResult.blockedPrompt,
            suggestion: "Try adding a style_hint like 'environmental portrait', 'silhouette style', or 'stylized illustration'",
          }, null, 2) }],
        };
      }

      try {
        embedImage(npc.filePath, "Appearance", relativePath);
      } catch (e) {
        warnings.push(`Image saved but embed failed: ${e.message}`);
      }

      const result = {
        imagePath: relativePath,
        prompt: geminiResult.prompt,
        reasoning: geminiResult.reasoning,
        warnings,
        reminder: "Run link_vault.py if you added new entity names.",
      };

      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    }
  );
}
