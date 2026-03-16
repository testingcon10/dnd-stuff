import { z } from "zod";
import { readSession, readNpc, readLocation, readPartyMember, extractWikilinks, extractVisualGear, listFiles, readReferenceImages } from "../lib/vault-reader.js";
import { craftScenePrompt } from "../lib/gemini-director.js";
import { generateImage } from "../lib/imagen-generator.js";
import { embedImage } from "../lib/vault-embedder.js";
import { slugifyScene, getAssetPath, getRelativeAssetPath } from "../lib/file-utils.js";
import { blockedResponse, successResponse } from "../lib/tool-responses.js";

const REF_ALIASES = {
  "Netanyahu D. Kirkuenly": "Net",
  "Booker Locke": "Booker",
  "Cassius Bellona": "Cassius",
  "Old Shell": "OldShell",
  "Ryan-Nigamus": "RyanNigamus",
};

const REF_MATCH_PATTERNS = {
  "Netanyahu D. Kirkuenly": [/\bnetanyahu\b/i, /\bnet\b/i],
  "Booker Locke": [/\bbooker\b/i],
  "Cassius Bellona": [/\bcassius\b/i],
  "Old Shell": [/\bold shell\b/i],
  "Ryan-Nigamus": [/\bryan-nigamus\b/i, /\bryan\b/i, /\bnigamus\b/i],
};

export function register(server) {
  server.tool(
    "generate_scene",
    "Generate a scene illustration from a session recap using vault context and AI image generation",
    {
      session_number: z.number().describe("Session number to illustrate"),
      scene_description: z.string().describe("Description of the specific scene to illustrate"),
      style_hint: z.string().optional().describe("Optional style direction to override/augment the default art style"),
      aspect_ratio: z.string().default("16:9").describe("Image aspect ratio (default 16:9 for scenes)"),
    },
    async ({ session_number, scene_description, style_hint, aspect_ratio }) => {
      const warnings = [];

      const session = readSession(session_number);
      if (!session) {
        const available = listFiles("02 - Sessions");
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify({ error: `Session ${session_number} not found`, available }, null, 2) }],
        };
      }

      const wikilinks = extractWikilinks(session.fullMarkdown);
      const referencedEntities = [];
      let entityCount = 0;

      for (const link of wikilinks) {
        if (entityCount >= 5) break;
        const npc = readNpc(link);
        if (npc) {
          referencedEntities.push({
            name: link,
            race: npc.frontmatter.race || "",
            appearance: npc.sections.appearance || "",
            notableItems: npc.sections.notableItems || "",
          });
          entityCount++;
          continue;
        }
        const loc = readLocation(link);
        if (loc) {
          referencedEntities.push({
            name: link,
            description: loc.sections.description || "",
          });
          entityCount++;
        }
      }

      const mentionedAliases = {};
      for (const [fullName, fileBase] of Object.entries(REF_ALIASES)) {
        const patterns = REF_MATCH_PATTERNS[fullName] || [new RegExp(`\\b${fullName.split(" ")[0]}\\b`, "i")];
        if (patterns.some(p => p.test(scene_description))) {
          mentionedAliases[fullName] = fileBase;
        }
      }
      const partyGear = [];
      for (const fullName of Object.keys(mentionedAliases)) {
        const member = readPartyMember(fullName);
        if (member) {
          const gear = extractVisualGear(member.sections, member.frontmatter.class);
          if (gear) {
            partyGear.push({
              name: fullName,
              race: member.frontmatter.race || "",
              className: member.frontmatter.class || "",
              gear,
            });
          }
        }
      }

      const referenceImages = readReferenceImages(mentionedAliases);

      const geminiResult = await craftScenePrompt({
        sceneDescription: scene_description,
        sessionNumber: session_number,
        summary: session.sections.summary || "",
        keyEvents: session.sections.keyEvents || "",
        highlights: session.sections.highlights || "",
        memorableQuotes: session.sections.memorableQuotes || "",
        characterMoments: session.sections.characterMoments || "",
        referencedEntities,
        partyGear,
        styleHint: style_hint,
      });

      const sceneSlug = slugifyScene(scene_description);
      const filename = `session-${session_number}-${sceneSlug}.png`;
      const outputPath = getAssetPath("scenes", filename);
      const relativePath = getRelativeAssetPath("scenes", filename);

      const imgResult = await generateImage(geminiResult.prompt, { aspectRatio: aspect_ratio, outputPath, referenceImages });

      if (!imgResult.success) {
        return blockedResponse(imgResult, "Try adding a style_hint like 'wide establishing shot', 'atmospheric landscape', or 'stylized battle scene'");
      }

      try {
        embedImage(session.filePath, "Illustrations", relativePath);
      } catch (e) {
        warnings.push(`Image saved but embed failed: ${e.message}`);
      }

      return successResponse({ imagePath: relativePath, prompt: geminiResult.prompt, reasoning: geminiResult.reasoning, warnings });
    }
  );
}
