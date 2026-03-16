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

const { register } = await import("../../src/tools/generate-location-art.js");
register(mockServer);

describe("generate_location_art", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("generates artwork for a location from vault data", async () => {
    mockCraftLocationPrompt.mockResolvedValue({ prompt: "test prompt", reasoning: "test reasoning" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "test.png", bytesWritten: 2000 });
    mockEmbedImage.mockReturnValue({ inserted: true });

    const result = await handler({ location_name: "Drayik", aspect_ratio: "16:9" });

    expect(mockCraftLocationPrompt).toHaveBeenCalledOnce();
    const promptArg = mockCraftLocationPrompt.mock.calls[0][0];
    expect(promptArg.name).toBe("Drayik");
    expect(promptArg.locationType).toBe("Settlement");
    expect(promptArg.region).toBe("Southeast Coast");
    expect(promptArg.parentData).toBeNull();

    expect(mockGenerateImage).toHaveBeenCalledWith("test prompt", expect.objectContaining({
      aspectRatio: "16:9",
    }));

    expect(mockEmbedImage).toHaveBeenCalledOnce();

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.imagePath).toContain("assets/locations/drayik.png");
    expect(body.prompt).toBe("test prompt");
    expect(body.reasoning).toBe("test reasoning");
  });

  it("passes parent location data to the prompt when provided", async () => {
    mockCraftLocationPrompt.mockResolvedValue({ prompt: "test", reasoning: "test" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "test.png", bytesWritten: 2000 });
    mockEmbedImage.mockReturnValue({ inserted: true });

    await handler({ location_name: "Drayik", parent_location: "Drayik", aspect_ratio: "16:9" });

    const promptArg = mockCraftLocationPrompt.mock.calls[0][0];
    expect(promptArg.parentData).not.toBeNull();
    expect(promptArg.parentData.name).toBe("Drayik");
    expect(typeof promptArg.parentData.description).toBe("string");
  });

  it("returns an error with available list when location is not found", async () => {
    const result = await handler({ location_name: "Atlantis", aspect_ratio: "16:9" });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("not found");
    expect(body.error).toContain("Atlantis");
    expect(Array.isArray(body.available)).toBe(true);

    expect(mockCraftLocationPrompt).not.toHaveBeenCalled();
    expect(mockGenerateImage).not.toHaveBeenCalled();
  });

  it("succeeds with a warning when parent location is not found", async () => {
    mockCraftLocationPrompt.mockResolvedValue({ prompt: "test", reasoning: "test" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "test.png", bytesWritten: 2000 });
    mockEmbedImage.mockReturnValue({ inserted: true });

    const result = await handler({ location_name: "Drayik", parent_location: "Nonexistent", aspect_ratio: "16:9" });

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.warnings).toEqual(expect.arrayContaining([
      expect.stringContaining("Nonexistent"),
    ]));

    const promptArg = mockCraftLocationPrompt.mock.calls[0][0];
    expect(promptArg.parentData).toBeNull();
  });

  it("returns a blocked error when image generation is blocked", async () => {
    mockCraftLocationPrompt.mockResolvedValue({ prompt: "blocked prompt", reasoning: "test" });
    mockGenerateImage.mockResolvedValue({ success: false, blocked: true, blockedPrompt: "blocked prompt" });

    const result = await handler({ location_name: "Drayik", aspect_ratio: "16:9" });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("blocked");
    expect(body.blockedPrompt).toBe("blocked prompt");
    expect(body.suggestion).toBeDefined();

    expect(mockEmbedImage).not.toHaveBeenCalled();
  });

  it("succeeds with a warning when embed fails", async () => {
    mockCraftLocationPrompt.mockResolvedValue({ prompt: "test prompt", reasoning: "test reasoning" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "test.png", bytesWritten: 2000 });
    mockEmbedImage.mockImplementation(() => {
      throw new Error("write failed");
    });

    const result = await handler({ location_name: "Drayik", aspect_ratio: "16:9" });

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.warnings).toEqual(expect.arrayContaining([
      expect.stringContaining("embed failed"),
    ]));
  });
});
