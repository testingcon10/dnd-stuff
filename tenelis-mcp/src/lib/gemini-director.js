import { GoogleGenAI } from "@google/genai";

let aiInstance = null;

export function getAI() {
  if (!aiInstance) {
    aiInstance = new GoogleGenAI({ apiKey: process.env.GOOGLE_API_KEY });
  }
  return aiInstance;
}

const SYSTEM_PROMPT = `You are a visual director for a dark fantasy D&D 5e campaign called Tenelis.

Your job: Given context about a character, location, scene, or party member, craft a detailed image generation prompt.

Art style baseline: detailed fantasy illustration, painterly, D&D sourcebook art style. Dark fantasy tone - gritty, atmospheric, muted earth tones with selective vivid accents.

Rules:
- Focus on visually distinctive details from the provided context
- Write prompts of approximately 200 words
- Never include text, labels, speech bubbles, or UI elements in the image
- Never reference game mechanics, stats, or numbers
- When data is sparse, infer visual details from faction, race, class, or name
- Always include lighting, atmosphere, and mood
- Output valid JSON: { "prompt": "...", "reasoning": "..." }
- The reasoning field explains your visual choices (1-2 sentences)`;

async function callGemini(userPrompt) {
  const ai = getAI();
  let lastError;

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: userPrompt,
        config: {
          systemInstruction: SYSTEM_PROMPT,
          responseMimeType: "application/json",
        },
      });

      const text = response.text.trim();
      return JSON.parse(text);
    } catch (e) {
      lastError = e;
      if (e.status === 429 && attempt === 0) {
        await new Promise(r => setTimeout(r, 2000));
        continue;
      }
      if (e instanceof SyntaxError && attempt === 0) {
        continue;
      }
      throw e;
    }
  }
  throw lastError;
}

function buildCtxBlock(label, value) {
  if (!value || (typeof value === "string" && !value.trim())) return "";
  return `${label}: ${value}\n`;
}

export async function craftNpcPrompt({ name, race, className, faction, appearance, personality, location, locationData, styleHint }) {
  let prompt = `Craft an image prompt for this NPC portrait.\n\n`;
  prompt += buildCtxBlock("Name", name);
  prompt += buildCtxBlock("Race", race);
  prompt += buildCtxBlock("Class", className);
  prompt += buildCtxBlock("Faction", faction);
  prompt += buildCtxBlock("Appearance", appearance);
  prompt += buildCtxBlock("Personality", personality);
  prompt += buildCtxBlock("Location", location);
  if (locationData) {
    prompt += buildCtxBlock("Location Description", locationData.description);
    prompt += buildCtxBlock("Location Type", locationData.locationType);
  }
  if (styleHint) prompt += `\nStyle direction: ${styleHint}`;
  return callGemini(prompt);
}

export async function craftLocationPrompt({ name, locationType, region, description, notableFeatures, parentData, styleHint }) {
  let prompt = `Craft an image prompt for this D&D location.\n\n`;
  prompt += buildCtxBlock("Name", name);
  prompt += buildCtxBlock("Type", locationType);
  prompt += buildCtxBlock("Region", region);
  prompt += buildCtxBlock("Description", description);
  prompt += buildCtxBlock("Notable Features", notableFeatures);
  if (parentData) {
    prompt += buildCtxBlock("Parent Location", parentData.name);
    prompt += buildCtxBlock("Parent Description", parentData.description);
  }
  if (styleHint) prompt += `\nStyle direction: ${styleHint}`;
  return callGemini(prompt);
}

export async function craftScenePrompt({ sceneDescription, sessionNumber, summary, keyEvents, highlights, memorableQuotes, characterMoments, referencedEntities, styleHint }) {
  let prompt = `Craft an image prompt for this scene from Session ${sessionNumber}.\n\n`;
  prompt += buildCtxBlock("Scene Description", sceneDescription);
  prompt += buildCtxBlock("Session Summary", summary);
  prompt += buildCtxBlock("Key Events", keyEvents);
  prompt += buildCtxBlock("Highlights", highlights);
  prompt += buildCtxBlock("Memorable Quotes", memorableQuotes);
  prompt += buildCtxBlock("Character Moments", characterMoments);
  if (referencedEntities?.length) {
    prompt += `\nReferenced entities:\n`;
    for (const entity of referencedEntities) {
      prompt += `- ${entity.name}`;
      if (entity.race) prompt += ` (${entity.race})`;
      if (entity.appearance) prompt += `: ${entity.appearance}`;
      prompt += "\n";
    }
  }
  if (styleHint) prompt += `\nStyle direction: ${styleHint}`;
  return callGemini(prompt);
}

export async function craftPartyPrompt({ name, race, className, subclass, equipment, backstory, characterMoments, styleHint }) {
  let prompt = `Craft an image prompt for this D&D player character portrait.\n\n`;
  prompt += buildCtxBlock("Name", name);
  prompt += buildCtxBlock("Race", race);
  prompt += buildCtxBlock("Class", className);
  prompt += buildCtxBlock("Subclass", subclass);
  prompt += buildCtxBlock("Equipment", equipment);
  prompt += buildCtxBlock("Backstory", backstory);
  if (characterMoments) {
    prompt += `\nNotable character moments from sessions:\n${characterMoments}\n`;
  }
  if (styleHint) prompt += `\nStyle direction: ${styleHint}`;
  return callGemini(prompt);
}
