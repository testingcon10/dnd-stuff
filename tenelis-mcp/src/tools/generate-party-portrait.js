import { z } from "zod";
import { readPartyMember, readSession, extractWikilinks, listFiles } from "../lib/vault-reader.js";
import { craftPartyPrompt } from "../lib/gemini-director.js";
import { generateImage } from "../lib/imagen-generator.js";
import { embedBeforeSection } from "../lib/vault-embedder.js";
import { slugify, getAssetPath, getRelativeAssetPath } from "../lib/file-utils.js";
import { readdirSync } from "fs";
import path from "path";
import { VAULT_ROOT } from "../lib/file-utils.js";

export function register(server) {
  server.tool(
    "generate_party_portrait",
    "Generate a portrait for a party member using character sheet and session moments",
    {
      character_name: z.string().describe("Name of the character as it appears in the vault"),
      style_hint: z.string().optional().describe("Optional style direction to override/augment the default art style"),
      aspect_ratio: z.string().default("3:4").describe("Image aspect ratio (default 3:4 for portraits)"),
    },
    async ({ character_name, style_hint, aspect_ratio }) => {
      const warnings = [];

      const member = readPartyMember(character_name);
      if (!member) {
        const available = listFiles("01 - Party");
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({ error: `Character "${character_name}" not found`, available }, null, 2) }],
        };
      }

      let characterMoments = "";
      try {
        const sessionsDir = path.join(VAULT_ROOT, "02 - Sessions");
        const sessionFiles = readdirSync(sessionsDir)
          .filter(f => f.match(/^Session \d+ Recap\.md$/))
          .sort((a, b) => {
            const na = parseInt(a.match(/\d+/)[0]);
            const nb = parseInt(b.match(/\d+/)[0]);
            return nb - na;
          })
          .slice(0, 10);

        for (const file of sessionFiles) {
          const num = parseInt(file.match(/\d+/)[0]);
          const session = readSession(num);
          if (!session) continue;
          const links = extractWikilinks(session.fullMarkdown);
          if (links.includes(character_name)) {
            const moments = session.sections.characterMoments || "";
            if (moments) characterMoments += `Session ${num}: ${moments}\n`;
          }
        }
      } catch (e) {
        warnings.push("Could not scan session recaps for character moments");
      }

      const geminiResult = await craftPartyPrompt({
        name: character_name,
        race: member.frontmatter.race || "",
        className: member.frontmatter.class || "",
        subclass: member.frontmatter.subclass || "",
        equipment: member.sections.equipment || "",
        backstory: member.sections.backstory || "",
        characterMoments: characterMoments || null,
        styleHint: style_hint,
      });

      const slug = slugify(character_name);
      const filename = `${slug}-portrait.png`;
      const outputPath = getAssetPath("party", filename);
      const relativePath = getRelativeAssetPath("party", filename);

      const imgResult = await generateImage(geminiResult.prompt, { aspectRatio: aspect_ratio, outputPath });

      if (!imgResult.success) {
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({
            error: "Image generation blocked by content filter",
            blockedPrompt: imgResult.blockedPrompt,
            suggestion: "Try adding a style_hint like 'heroic fantasy portrait', 'silhouette style', or 'stylized character art'",
          }, null, 2) }],
        };
      }

      try {
        embedBeforeSection(member.filePath, "Portrait", relativePath, "Ability Scores");
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
