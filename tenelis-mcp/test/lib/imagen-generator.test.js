import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  mockImageResponse,
  mockBlockedImageResponse,
} from "../helpers/mock-ai.js";

const mockGenerateContent = vi.fn();
vi.mock("@google/genai", () => ({
  GoogleGenAI: vi.fn(function () {
    this.models = { generateContent: mockGenerateContent };
  }),
}));

vi.mock("fs", async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, writeFileSync: vi.fn() };
});

import { generateImage } from "../../src/lib/imagen-generator.js";
import { writeFileSync } from "fs";

const SAMPLE_BASE64 = Buffer.from("fake-image-data").toString("base64");

beforeEach(() => {
  process.env.GOOGLE_API_KEY = "test-key";
  mockGenerateContent.mockReset();
  writeFileSync.mockClear();
});

describe("generateImage", () => {
  it("succeeds without reference images", async () => {
    mockGenerateContent.mockResolvedValue(mockImageResponse(SAMPLE_BASE64));

    const result = await generateImage("A fantasy tavern", {
      aspectRatio: "16:9",
      outputPath: "/tmp/tavern.png",
    });

    expect(result.success).toBe(true);
    expect(result.outputPath).toBe("/tmp/tavern.png");
    expect(result.bytesWritten).toBeGreaterThan(0);

    const callArgs = mockGenerateContent.mock.calls[0][0];
    expect(callArgs.model).toBe("gemini-3-pro-image-preview");
    expect(callArgs.config.responseModalities).toEqual(["IMAGE"]);
    expect(typeof callArgs.contents).toBe("string");
  });

  it("succeeds with reference images and interleaves image parts", async () => {
    mockGenerateContent.mockResolvedValue(mockImageResponse(SAMPLE_BASE64));

    const refImages = [
      { name: "Netanyahu", mimeType: "image/png", data: "abc123" },
      { name: "Old Shell", mimeType: "image/jpeg", data: "def456" },
    ];

    const result = await generateImage("A party scene", {
      outputPath: "/tmp/party.png",
      referenceImages: refImages,
    });

    expect(result.success).toBe(true);

    const callArgs = mockGenerateContent.mock.calls[0][0];
    expect(Array.isArray(callArgs.contents)).toBe(true);

    const textParts = callArgs.contents.filter(p => p.text);
    const imageParts = callArgs.contents.filter(p => p.inlineData);
    expect(imageParts).toHaveLength(2);
    expect(imageParts[0].inlineData.data).toBe("abc123");
    expect(imageParts[1].inlineData.data).toBe("def456");
    expect(textParts.length).toBeGreaterThanOrEqual(3);
  });

  it("returns blocked when promptFeedback has blockReason", async () => {
    mockGenerateContent.mockResolvedValue({
      promptFeedback: { blockReason: "SAFETY" },
      candidates: [],
    });

    const result = await generateImage("Violent scene", {
      outputPath: "/tmp/blocked.png",
    });

    expect(result.success).toBe(false);
    expect(result.blocked).toBe(true);
    expect(result.message).toContain("content filter");
  });

  it("returns blocked when candidate finishReason is SAFETY", async () => {
    mockGenerateContent.mockResolvedValue(mockBlockedImageResponse());

    const result = await generateImage("Dark scene", {
      outputPath: "/tmp/blocked2.png",
    });

    expect(result.success).toBe(false);
    expect(result.blocked).toBe(true);
  });

  it("returns blocked when no image part in response", async () => {
    mockGenerateContent.mockResolvedValue({
      promptFeedback: null,
      candidates: [
        {
          finishReason: "STOP",
          content: { parts: [{ text: "Sorry, I cannot generate that image." }] },
        },
      ],
    });

    const result = await generateImage("Ambiguous prompt", {
      outputPath: "/tmp/no-image.png",
    });

    expect(result.success).toBe(false);
    expect(result.blocked).toBe(true);
  });

  it("retries on 429 and succeeds on second attempt", async () => {
    mockGenerateContent
      .mockRejectedValueOnce({ status: 429 })
      .mockResolvedValueOnce(mockImageResponse(SAMPLE_BASE64));

    const result = await generateImage("Retry prompt", {
      outputPath: "/tmp/retry.png",
    });

    expect(result.success).toBe(true);
    expect(mockGenerateContent).toHaveBeenCalledTimes(2);
  });

  it("calls writeFileSync with the decoded buffer", async () => {
    mockGenerateContent.mockResolvedValue(mockImageResponse(SAMPLE_BASE64));

    await generateImage("Write test", {
      outputPath: "/tmp/write-test.png",
    });

    expect(writeFileSync).toHaveBeenCalledOnce();
    const [path, buffer] = writeFileSync.mock.calls[0];
    expect(path).toBe("/tmp/write-test.png");
    expect(Buffer.isBuffer(buffer)).toBe(true);
    expect(buffer.toString()).toBe("fake-image-data");
  });

  it("propagates non-429 errors", async () => {
    mockGenerateContent.mockRejectedValue(new Error("Internal server error"));

    await expect(
      generateImage("Error prompt", { outputPath: "/tmp/error.png" })
    ).rejects.toThrow("Internal server error");
  });
});
