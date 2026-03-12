import { z } from "zod";
import { readLocation, listFiles } from "../lib/vault-reader.js";
import { craftLocationPrompt } from "../lib/gemini-director.js";
import { generateImage } from "../lib/imagen-generator.js";
import { embedImage } from "../lib/vault-embedder.js";
import { slugify, getAssetPath, getRelativeAssetPath } from "../lib/file-utils.js";

export function register(server) {
  server.tool(
    "generate_location_art",
    "Generate artwork for a location using vault context and AI image generation",
    {
      location_name: z.string().describe("Name of the location as it appears in the vault"),
      parent_location: z.string().optional().describe("Optional parent location for regional context"),
      style_hint: z.string().optional().describe("Optional style direction to override/augment the default art style"),
      aspect_ratio: z.string().default("16:9").describe("Image aspect ratio (default 16:9 for landscapes)"),
    },
    async ({ location_name, parent_location, style_hint, aspect_ratio }) => {
      const warnings = [];

      const loc = readLocation(location_name);
      if (!loc) {
        const available = listFiles("06 - World/Locations");
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({ error: `Location "${location_name}" not found`, available }, null, 2) }],
        };
      }

      let parentData = null;
      if (parent_location) {
        const parent = readLocation(parent_location);
        if (parent) {
          parentData = {
            name: parent_location,
            description: parent.sections.description || "",
          };
        } else {
          warnings.push(`Parent location "${parent_location}" not found, skipping parent context`);
        }
      }

      const geminiResult = await craftLocationPrompt({
        name: location_name,
        locationType: loc.frontmatter.location_type || "",
        region: loc.frontmatter.region || "",
        description: loc.sections.description || "",
        notableFeatures: loc.sections.notableFeatures || "",
        parentData,
        styleHint: style_hint,
      });

      const slug = slugify(location_name);
      const filename = `${slug}.png`;
      const outputPath = getAssetPath("locations", filename);
      const relativePath = getRelativeAssetPath("locations", filename);

      const imgResult = await generateImage(geminiResult.prompt, { aspectRatio: aspect_ratio, outputPath });

      if (!imgResult.success) {
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({
            error: "Image generation blocked by content filter",
            blockedPrompt: imgResult.blockedPrompt,
            suggestion: "Try adding a style_hint like 'aerial view', 'map illustration', or 'watercolor landscape'",
          }, null, 2) }],
        };
      }

      try {
        embedImage(loc.filePath, "Description", relativePath);
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
