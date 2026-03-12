import { writeFileSync } from "fs";
import { getAI } from "./gemini-director.js";

export async function generateImage(prompt, { aspectRatio = "3:4", outputPath }) {
  const ai = getAI();
  let lastError;

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const response = await ai.models.generateImages({
        model: "imagen-4.0-generate-001",
        prompt,
        config: {
          numberOfImages: 1,
          aspectRatio,
          enhancePrompt: false,
          personGeneration: "ALLOW_ADULT",
        },
      });

      if (!response.generatedImages?.length) {
        return {
          success: false,
          blocked: true,
          message: "Image generation was blocked by the content filter. Try adjusting the style_hint to use a more stylized, environmental, or silhouette-based approach.",
          blockedPrompt: prompt,
        };
      }

      const imageBytes = response.generatedImages[0].image.imageBytes;
      const buffer = Buffer.from(imageBytes, "base64");
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
