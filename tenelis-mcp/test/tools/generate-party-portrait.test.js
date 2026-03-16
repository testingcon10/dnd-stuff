import { describe, it, expect, vi, beforeEach } from "vitest";

const mockCraftPartyPrompt = vi.fn();
const mockGenerateImage = vi.fn();
const mockEmbedBeforeSection = vi.fn();

vi.mock("../../src/lib/gemini-director.js", () => ({
  craftPartyPrompt: mockCraftPartyPrompt,
}));

vi.mock("../../src/lib/imagen-generator.js", () => ({
  generateImage: mockGenerateImage,
}));

vi.mock("../../src/lib/vault-embedder.js", () => ({
  embedBeforeSection: mockEmbedBeforeSection,
}));

let handler;
const mockServer = {
  tool: (_name, _desc, _schema, fn) => {
    handler = fn;
  },
};
const { register } = await import("../../src/tools/generate-party-portrait.js");
register(mockServer);

describe("generate_party_portrait handler", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockCraftPartyPrompt.mockResolvedValue({ prompt: "test prompt", reasoning: "test reasoning" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "/fake/path.png", bytesWritten: 1024 });
    mockEmbedBeforeSection.mockReturnValue({ created: true });
  });

  it("happy path - reads character, gathers moments, and returns success", async () => {
    const result = await handler({
      character_name: "Netanyahu D. Kirkuenly",
      aspect_ratio: "3:4",
    });

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.imagePath).toBeDefined();
    expect(body.prompt).toBe("test prompt");
    expect(body.reasoning).toBe("test reasoning");

    expect(mockCraftPartyPrompt).toHaveBeenCalledOnce();
    const args = mockCraftPartyPrompt.mock.calls[0][0];
    expect(args.name).toBe("Netanyahu D. Kirkuenly");
    expect(args.race).toBe("Yuan-ti");
    expect(args.className).toBe("Bard");
    expect(args.subclass).toBe("College of Lore");
    expect(typeof args.characterMoments).toBe("string");
    expect(args.characterMoments.length).toBeGreaterThan(0);
  });

  it("returns isError with available characters when character is not found", async () => {
    const result = await handler({
      character_name: "Gandalf",
      aspect_ratio: "3:4",
    });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("Gandalf");
    expect(body.error).toContain("not found");
    expect(Array.isArray(body.available)).toBe(true);
    expect(body.available.length).toBeGreaterThan(0);

    expect(mockCraftPartyPrompt).not.toHaveBeenCalled();
    expect(mockGenerateImage).not.toHaveBeenCalled();
  });

  it("returns isError when image generation is blocked", async () => {
    mockGenerateImage.mockResolvedValue({
      success: false,
      blocked: true,
      message: "blocked by content filter",
      blockedPrompt: "test prompt",
    });

    const result = await handler({
      character_name: "Netanyahu D. Kirkuenly",
      aspect_ratio: "3:4",
    });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("blocked");
    expect(body.blockedPrompt).toBe("test prompt");
    expect(body.suggestion).toBeDefined();
  });

  it("returns success with warning when embed fails", async () => {
    mockEmbedBeforeSection.mockImplementation(() => {
      throw new Error("File is read-only");
    });

    const result = await handler({
      character_name: "Netanyahu D. Kirkuenly",
      aspect_ratio: "3:4",
    });

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.imagePath).toBeDefined();
    expect(body.warnings).toBeDefined();
    expect(body.warnings.length).toBeGreaterThan(0);
    expect(body.warnings[0]).toContain("embed failed");
  });

  it("passes custom style_hint to craftPartyPrompt", async () => {
    const result = await handler({
      character_name: "Netanyahu D. Kirkuenly",
      style_hint: "heroic",
      aspect_ratio: "3:4",
    });

    expect(result.isError).toBeUndefined();

    const args = mockCraftPartyPrompt.mock.calls[0][0];
    expect(args.styleHint).toBe("heroic");
  });
});
