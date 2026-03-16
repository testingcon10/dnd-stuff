import { writeFileSync } from "fs";
import { getAI } from "./gemini-director.js";

const BLOCKED_REASONS = new Set(["SAFETY", "IMAGE_SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"]);
const BLOCKED_MSG = "Image generation was blocked by the content filter. Try adjusting the style_hint to use a more stylized, environmental, or silhouette-based approach.";

export async function generateImage(prompt, { aspectRatio = "3:4", outputPath, referenceImages = [] }) {
  const ai = getAI();
  const refNames = referenceImages.map(r => r.name).join(", ");
  const fullPrompt = referenceImages.length
    ? `IMPORTANT: The attached ${referenceImages.length} images are character reference portraits for: ${refNames}. Each character in the generated scene MUST match their reference portrait's face, hair, skin, and features exactly. Do not deviate from the reference - if a reference shows a human-looking face with scale patches, draw a human-looking face with scale patches, not a reptile. If a reference shows an upright humanoid turtle, draw them standing upright on two legs like a human.\n\n${prompt}\n\nGenerate this image in ${aspectRatio} aspect ratio.`
    : `${prompt}\n\nGenerate this image in ${aspectRatio} aspect ratio.`;

  const contents = referenceImages.length
    ? [
        ...referenceImages.flatMap(img => [
          { text: `Reference portrait for ${img.name}:` },
          { inlineData: { mimeType: img.mimeType, data: img.data } },
        ]),
        { text: fullPrompt },
      ]
    : fullPrompt;
  let lastError;

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const response = await ai.models.generateContent({
        model: "gemini-3-pro-image-preview",
        contents,
        config: {
          responseModalities: ["IMAGE"],
        },
      });

      if (response.promptFeedback?.blockReason) {
        return { success: false, blocked: true, message: BLOCKED_MSG, blockedPrompt: prompt };
      }

      const candidate = response.candidates?.[0];
      if (candidate && BLOCKED_REASONS.has(candidate.finishReason)) {
        return { success: false, blocked: true, message: BLOCKED_MSG, blockedPrompt: prompt };
      }

      const imagePart = candidate?.content?.parts?.find(p => p.inlineData);
      if (!imagePart) {
        return { success: false, blocked: true, message: BLOCKED_MSG, blockedPrompt: prompt };
      }

      const buffer = Buffer.from(imagePart.inlineData.data, "base64");
      writeFileSync(outputPath, buffer);

      return {
        success: true,
        outputPath,
        bytesWritten: buffer.length,
      };
    } catch (e) {
      lastError = e;
      if (e.status === 429 && attempt === 0) {
        await new Promise(r => setTimeout(r, 2000));
        continue;
      }
      throw e;
    }
  }
  throw lastError;
}
