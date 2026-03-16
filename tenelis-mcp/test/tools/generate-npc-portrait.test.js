import { describe, it, expect, vi, beforeEach } from "vitest";

const mockCraftNpcPrompt = vi.fn();
const mockCraftLocationPrompt = vi.fn();
const mockGenerateImage = vi.fn();
const mockEmbedImage = vi.fn();

vi.mock("../../src/lib/gemini-director.js", () => ({
  craftNpcPrompt: mockCraftNpcPrompt,
  craftLocationPrompt: mockCraftLocationPrompt,
}));

vi.mock("../../src/lib/imagen-generator.js", () => ({
  generateImage: mockGenerateImage,
}));

vi.mock("../../src/lib/vault-embedder.js", () => ({
  embedImage: mockEmbedImage,
}));

let handler;
const mockServer = {
  tool: (_name, _desc, _schema, fn) => { handler = fn; },
};

const { register } = await import("../../src/tools/generate-npc-portrait.js");
register(mockServer);

describe("generate_npc_portrait", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("generates a portrait for an NPC with location context", async () => {
    mockCraftNpcPrompt.mockResolvedValue({ prompt: "test prompt", reasoning: "test reasoning" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "test.png", bytesWritten: 1000 });
    mockEmbedImage.mockReturnValue({ inserted: true });

    const result = await handler({ npc_name: "Watkins", aspect_ratio: "3:4" });

    expect(mockCraftNpcPrompt).toHaveBeenCalledOnce();
    const promptArg = mockCraftNpcPrompt.mock.calls[0][0];
    expect(promptArg.name).toBe("Watkins");
    expect(promptArg.race).toBe("Halfling");
    expect(promptArg.className).toBe("Bartender");
    expect(promptArg.location).toBe("Drayik");
    expect(promptArg.locationData).not.toBeNull();
    expect(promptArg.locationData.locationType).toBe("Settlement");

    expect(mockGenerateImage).toHaveBeenCalledWith("test prompt", expect.objectContaining({
      aspectRatio: "3:4",
    }));

    expect(mockEmbedImage).toHaveBeenCalledOnce();

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.imagePath).toContain("assets/npcs/watkins-portrait.png");
    expect(body.prompt).toBe("test prompt");
    expect(body.reasoning).toBe("test reasoning");
  });

  it("returns an error with available NPC list when NPC is not found", async () => {
    const result = await handler({ npc_name: "Gandalf", aspect_ratio: "3:4" });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("not found");
    expect(body.error).toContain("Gandalf");
    expect(Array.isArray(body.available)).toBe(true);
    expect(body.available.length).toBeGreaterThan(0);
    expect(body.available).toContain("Watkins");

    expect(mockCraftNpcPrompt).not.toHaveBeenCalled();
    expect(mockGenerateImage).not.toHaveBeenCalled();
  });

  it("returns a blocked error when image generation is blocked", async () => {
    mockCraftNpcPrompt.mockResolvedValue({ prompt: "blocked prompt", reasoning: "test" });
    mockGenerateImage.mockResolvedValue({ success: false, blocked: true, blockedPrompt: "blocked prompt" });

    const result = await handler({ npc_name: "Watkins", aspect_ratio: "3:4" });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("blocked");
    expect(body.blockedPrompt).toBe("blocked prompt");
    expect(body.suggestion).toBeDefined();

    expect(mockEmbedImage).not.toHaveBeenCalled();
  });

  it("returns success with a warning when embed fails", async () => {
    mockCraftNpcPrompt.mockResolvedValue({ prompt: "test prompt", reasoning: "test" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "test.png", bytesWritten: 1000 });
    mockEmbedImage.mockImplementation(() => { throw new Error("write failed"); });

    const result = await handler({ npc_name: "Watkins", aspect_ratio: "3:4" });

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.imagePath).toContain("assets/npcs/watkins-portrait.png");
    expect(body.warnings).toEqual(expect.arrayContaining([
      expect.stringContaining("write failed"),
    ]));
  });

  it("passes a custom style_hint through to craftNpcPrompt", async () => {
    mockCraftNpcPrompt.mockResolvedValue({ prompt: "watercolor prompt", reasoning: "styled" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "test.png", bytesWritten: 1000 });
    mockEmbedImage.mockReturnValue({ inserted: true });

    await handler({ npc_name: "Watkins", style_hint: "watercolor", aspect_ratio: "3:4" });

    const promptArg = mockCraftNpcPrompt.mock.calls[0][0];
    expect(promptArg.styleHint).toBe("watercolor");
  });
});
