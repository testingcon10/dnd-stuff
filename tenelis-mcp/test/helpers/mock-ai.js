export function mockGeminiResponse(jsonObj) {
  return { text: JSON.stringify(jsonObj), promptFeedback: null };
}

export function mockBlockedResponse() {
  return { text: null, promptFeedback: { blockReason: "SAFETY" } };
}

export function mockImageResponse(base64Data) {
  return {
    candidates: [
      {
        content: {
          parts: [{ inlineData: { data: base64Data, mimeType: "image/png" } }],
        },
        finishReason: "STOP",
      },
    ],
    promptFeedback: null,
  };
}

export function mockBlockedImageResponse() {
  return {
    candidates: [
      {
        finishReason: "SAFETY",
        content: { parts: [] },
      },
    ],
    promptFeedback: null,
  };
}

export const SAMPLE_PROMPT_RESULT = {
  prompt: "A detailed fantasy portrait...",
  reasoning: "Based on the NPC context",
};
