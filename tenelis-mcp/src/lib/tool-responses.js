export function blockedResponse(imgResult, suggestion) {
  return {
    isError: true,
    content: [{ type: "text", text: JSON.stringify({
      error: "Image generation blocked by content filter",
      blockedPrompt: imgResult.blockedPrompt,
      suggestion,
    }, null, 2) }],
  };
}

export function successResponse({ imagePath, prompt, reasoning, warnings }) {
  const result = {
    imagePath,
    prompt,
    reasoning,
    warnings,
    reminder: "Run link_vault.py if you added new entity names.",
  };
  return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
}
