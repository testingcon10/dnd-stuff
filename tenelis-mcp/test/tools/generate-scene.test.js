import { describe, it, expect, vi, beforeEach } from "vitest";

const mockCraftScenePrompt = vi.fn();
const mockGenerateImage = vi.fn();
const mockEmbedImage = vi.fn();

vi.mock("../../src/lib/gemini-director.js", () => ({
  craftScenePrompt: mockCraftScenePrompt,
}));

vi.mock("../../src/lib/imagen-generator.js", () => ({
  generateImage: mockGenerateImage,
}));

vi.mock("../../src/lib/vault-embedder.js", () => ({
  embedImage: mockEmbedImage,
}));

let handler;
const mockServer = {
  tool: (_name, _desc, _schema, fn) => {
    handler = fn;
  },
};
const { register } = await import("../../src/tools/generate-scene.js");
register(mockServer);

describe("generate_scene handler", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockCraftScenePrompt.mockResolvedValue({ prompt: "test prompt", reasoning: "test reasoning" });
    mockGenerateImage.mockResolvedValue({ success: true, outputPath: "/fake/path.png", bytesWritten: 1024 });
    mockEmbedImage.mockReturnValue({ inserted: true });
  });

  it("happy path - reads session 6, resolves entities, and returns success", async () => {
    const result = await handler({
      session_number: 6,
      scene_description: "The tavern in Drayik",
      aspect_ratio: "16:9",
    });

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.imagePath).toBeDefined();
    expect(body.prompt).toBe("test prompt");
    expect(body.reasoning).toBe("test reasoning");

    expect(mockCraftScenePrompt).toHaveBeenCalledOnce();
    const args = mockCraftScenePrompt.mock.calls[0][0];
    expect(args.sessionNumber).toBe(6);
    expect(typeof args.summary).toBe("string");
    expect(args.summary.length).toBeGreaterThan(0);
    expect(args.referencedEntities.length).toBeGreaterThan(0);
    expect(args.referencedEntities.length).toBeLessThanOrEqual(5);
    const entityNames = args.referencedEntities.map(e => e.name);
    expect(entityNames).toContain("Drayik");
    expect(entityNames).toContain("Eileen Whitebeak");
  });

  it("detects party members in scene_description and provides gear and reference images", async () => {
    const result = await handler({
      session_number: 6,
      scene_description: "Netanyahu and Booker confront Watkins",
      aspect_ratio: "16:9",
    });

    expect(result.isError).toBeUndefined();

    const args = mockCraftScenePrompt.mock.calls[0][0];
    expect(args.partyGear.length).toBeGreaterThan(0);
    const gearNames = args.partyGear.map(g => g.name);
    expect(gearNames).toContain("Netanyahu D. Kirkuenly");
    expect(gearNames).toContain("Booker Locke");

    const imgArgs = mockGenerateImage.mock.calls[0];
    const opts = imgArgs[1];
    expect(Array.isArray(opts.referenceImages)).toBe(true);
    expect(opts.referenceImages.length).toBeGreaterThan(0);
  });

  it("returns isError with available sessions when session is not found", async () => {
    const result = await handler({
      session_number: 999,
      scene_description: "anything",
      aspect_ratio: "16:9",
    });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("999");
    expect(body.error).toContain("not found");
    expect(Array.isArray(body.available)).toBe(true);
    expect(body.available.length).toBeGreaterThan(0);

    expect(mockCraftScenePrompt).not.toHaveBeenCalled();
    expect(mockGenerateImage).not.toHaveBeenCalled();
  });

  it("sends empty partyGear and referenceImages when no party members are in description", async () => {
    const result = await handler({
      session_number: 6,
      scene_description: "The library of Drayik",
      aspect_ratio: "16:9",
    });

    expect(result.isError).toBeUndefined();

    const args = mockCraftScenePrompt.mock.calls[0][0];
    expect(args.partyGear).toEqual([]);

    const imgArgs = mockGenerateImage.mock.calls[0];
    const opts = imgArgs[1];
    expect(opts.referenceImages).toEqual([]);
  });

  it("returns isError when image generation is blocked", async () => {
    mockGenerateImage.mockResolvedValue({
      success: false,
      blocked: true,
      message: "blocked by content filter",
      blockedPrompt: "test prompt",
    });

    const result = await handler({
      session_number: 6,
      scene_description: "The tavern in Drayik",
      aspect_ratio: "16:9",
    });

    expect(result.isError).toBe(true);
    const body = JSON.parse(result.content[0].text);
    expect(body.error).toContain("blocked");
    expect(body.blockedPrompt).toBe("test prompt");
    expect(body.suggestion).toBeDefined();
  });

  it("succeeds with a warning when embed fails", async () => {
    mockEmbedImage.mockImplementation(() => {
      throw new Error("write failed");
    });

    const result = await handler({
      session_number: 6,
      scene_description: "The tavern in Drayik",
      aspect_ratio: "16:9",
    });

    expect(result.isError).toBeUndefined();
    const body = JSON.parse(result.content[0].text);
    expect(body.warnings).toEqual(expect.arrayContaining([
      expect.stringContaining("embed failed"),
    ]));
  });
});
