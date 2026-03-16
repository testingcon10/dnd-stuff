import { GoogleGenAI } from "@google/genai";

let aiInstance = null;

export function getAI() {
  if (!aiInstance) {
    if (!process.env.GOOGLE_API_KEY) {
      throw new Error("GOOGLE_API_KEY environment variable is not set");
    }
    aiInstance = new GoogleGenAI({ apiKey: process.env.GOOGLE_API_KEY });
  }
  return aiInstance;
}

const SYSTEM_PROMPT = `You are a visual director for a dark fantasy D&D 5e campaign called Tenelis.

Your job: Given context about a character, location, scene, or party member, craft a detailed image generation prompt. Write the prompt as a flowing descriptive paragraph, not a keyword list. Describe the scene narratively.

Art style baseline: detailed fantasy illustration, painterly, D&D sourcebook art style. Dark fantasy tone - gritty, atmospheric, muted earth tones with selective vivid accents. High-quality, detailed.

Camera & Composition:
- For character portraits: use close-up or medium shot framing, 85mm portrait lens, shallow depth of field with soft bokeh background
- For location art: use wide-angle establishing shot, 24mm lens, deep focus to show the full environment
- For scenes with multiple characters: use medium wide shot, 35mm lens, enough depth to show character interactions and setting
- Always specify a camera angle that fits the subject's personality or mood (low-angle for imposing figures, eye-level for approachable characters, high-angle for vulnerability)

Lighting & Atmosphere:
- Always specify a concrete lighting setup, not just "atmospheric". Use terms like: golden hour light, cold moonlight, warm firelight, dramatic side-lighting, soft diffused light, rim lighting, candlelit, overcast ambient light
- Describe the quality of light: harsh shadows, dappled light through trees, hazy volumetric light, sharp contrast

Materials & Textures:
- Be specific about materials rather than generic. Not "armor" but "battered iron plate armor with leather straps and tarnished rivets". Not "robe" but "threadbare wool robes with frayed hems"
- Include surface details: weathered, polished, rusted, scarred, sun-bleached, mud-spattered

Rules:
- Focus on visually distinctive details from the provided context
- Write prompts of approximately 200 words
- Never include text, labels, speech bubbles, or UI elements in the image
- Never reference game mechanics, stats, or numbers
- When data is sparse, infer visual details from faction, race, class, or name
- Describe what you want to see positively rather than listing things to exclude
- Character body language must match the social context of the scene, not class stereotypes. Read the session notes: if characters are meeting an ally, they should look relaxed and conversational - a rogue at a friendly meeting stands casually, not skulking with a drawn blade. Reserve combat-ready postures for actual combat or hostility. Allies talk, strangers observe, friends joke - reflect the relationship dynamics in body language
- ALL characters must stand and pose like real humans would in the situation, regardless of race. Non-human races (Tortle, Yuan-ti, etc.) are humanoid and stand upright like people - they lean, cross arms, shift weight, gesture while talking. Avoid stiff "character select screen" posing
- CRITICAL: When reference images are provided for characters, describe the character's appearance to match the reference image exactly. Do NOT use generic race descriptions that contradict the reference. For example, a Yuan-ti Pureblood with a reference showing a mostly-human face with green scale patches should be described as "a human-looking man with patches of green scales on his skin" - NOT as "a reptilian Yuan-ti" or "a lizard-like figure"
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

      if (response.promptFeedback?.blockReason) {
        return { prompt: "blocked", reasoning: "Content was filtered by the API" };
      }
      const text = response.text;
      if (!text) {
        return { prompt: "blocked", reasoning: "Content was filtered by the API" };
      }
      return JSON.parse(text.trim());
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

export async function craftNpcPrompt({ name, race, className, faction, appearance, personality, background, location, locationData, notableItems, styleHint }) {
  let prompt = `Craft an image prompt for this NPC portrait.\n\n`;
  prompt += buildCtxBlock("Name", name);
  prompt += buildCtxBlock("Race", race);
  prompt += buildCtxBlock("Class", className);
  prompt += buildCtxBlock("Faction", faction);
  prompt += buildCtxBlock("Appearance", appearance);
  prompt += buildCtxBlock("Personality", personality);
  prompt += buildCtxBlock("Background", background);
  prompt += buildCtxBlock("Notable Items", notableItems);
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

export async function craftScenePrompt({ sceneDescription, sessionNumber, summary, keyEvents, highlights, memorableQuotes, characterMoments, referencedEntities, partyGear, styleHint }) {
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
      if (entity.notableItems) prompt += `. Items: ${entity.notableItems}`;
      prompt += "\n";
    }
  }
  if (partyGear?.length) {
    prompt += `\nParty members in scene (reference images are attached for these characters - match their appearance closely, do NOT use generic race descriptions):\n`;
    for (const member of partyGear) {
      prompt += `- ${member.name} (${member.race} ${member.className}): ${member.gear}\n`;
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
