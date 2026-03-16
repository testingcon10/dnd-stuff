import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  mockGeminiResponse,
  mockBlockedResponse,
  SAMPLE_PROMPT_RESULT,
} from "../helpers/mock-ai.js";

const mockGenerateContent = vi.fn();
vi.mock("@google/genai", () => ({
  GoogleGenAI: vi.fn(function () {
    this.models = { generateContent: mockGenerateContent };
  }),
}));

import {
  getAI,
  craftNpcPrompt,
  craftLocationPrompt,
  craftScenePrompt,
  craftPartyPrompt,
} from "../../src/lib/gemini-director.js";

beforeEach(() => {
  process.env.GOOGLE_API_KEY = "test-key";
  mockGenerateContent.mockReset();
});

describe("getAI", () => {
  it("throws when GOOGLE_API_KEY is not set", async () => {
    vi.resetModules();

    vi.doMock("@google/genai", () => ({
      GoogleGenAI: vi.fn(function () {
        this.models = { generateContent: vi.fn() };
      }),
    }));

    const origKey = process.env.GOOGLE_API_KEY;
    delete process.env.GOOGLE_API_KEY;

    try {
      const mod = await import("../../src/lib/gemini-director.js");
      expect(() => mod.getAI()).toThrow("GOOGLE_API_KEY environment variable is not set");
    } finally {
      process.env.GOOGLE_API_KEY = origKey;
    }
  });
});

describe("craftNpcPrompt", () => {
  it("returns prompt and reasoning with full context", async () => {
    mockGenerateContent.mockResolvedValue(mockGeminiResponse(SAMPLE_PROMPT_RESULT));

    const result = await craftNpcPrompt({
      name: "Watkins",
      race: "Human",
      className: "Fighter",
      faction: "The Dockworkers",
      appearance: "Scarred, weathered face",
      personality: "Gruff but loyal",
      background: "Former soldier",
      location: "The Half Mast",
      locationData: { description: "A seedy tavern", locationType: "Tavern" },
      notableItems: "Rusty cutlass",
      styleHint: "gritty realism",
    });

    expect(result.prompt).toBe(SAMPLE_PROMPT_RESULT.prompt);
    expect(result.reasoning).toBe(SAMPLE_PROMPT_RESULT.reasoning);
    expect(mockGenerateContent).toHaveBeenCalledOnce();

    const callArgs = mockGenerateContent.mock.calls[0][0];
    expect(callArgs.contents).toContain("Watkins");
    expect(callArgs.contents).toContain("Human");
    expect(callArgs.contents).toContain("Fighter");
    expect(callArgs.contents).toContain("gritty realism");
  });

  it("works with sparse context (only name and race)", async () => {
    mockGenerateContent.mockResolvedValue(mockGeminiResponse(SAMPLE_PROMPT_RESULT));

    const result = await craftNpcPrompt({ name: "Grig", race: "Goblin" });

    expect(result.prompt).toBe(SAMPLE_PROMPT_RESULT.prompt);
    expect(result.reasoning).toBe(SAMPLE_PROMPT_RESULT.reasoning);

    const callArgs = mockGenerateContent.mock.calls[0][0];
    expect(callArgs.contents).toContain("Grig");
    expect(callArgs.contents).toContain("Goblin");
  });
});

describe("craftLocationPrompt", () => {
  it("returns prompt and reasoning", async () => {
    mockGenerateContent.mockResolvedValue(mockGeminiResponse(SAMPLE_PROMPT_RESULT));

    const result = await craftLocationPrompt({
      name: "Drayik",
      locationType: "City",
      region: "The Northern Wastes",
      description: "A crumbling port city",
      notableFeatures: "Ancient lighthouse",
      parentData: { name: "The Northern Wastes", description: "A frozen expanse" },
      styleHint: "dark atmosphere",
    });

    expect(result.prompt).toBe(SAMPLE_PROMPT_RESULT.prompt);
    expect(result.reasoning).toBe(SAMPLE_PROMPT_RESULT.reasoning);

    const callArgs = mockGenerateContent.mock.calls[0][0];
    expect(callArgs.contents).toContain("Drayik");
    expect(callArgs.contents).toContain("City");
    expect(callArgs.contents).toContain("dark atmosphere");
  });
});

describe("craftScenePrompt", () => {
  it("includes referencedEntities and partyGear in the prompt", async () => {
    mockGenerateContent.mockResolvedValue(mockGeminiResponse(SAMPLE_PROMPT_RESULT));

    const result = await craftScenePrompt({
      sceneDescription: "The party enters the tavern",
      sessionNumber: 6,
      summary: "A tense meeting",
      keyEvents: "Confrontation with Watkins",
      highlights: "Bar fight",
      memorableQuotes: "You dare?",
      characterMoments: "Netanyahu talked his way out",
      referencedEntities: [
        { name: "Watkins", race: "Human", appearance: "Scarred face", notableItems: "Cutlass" },
      ],
      partyGear: [
        { name: "Netanyahu", race: "Yuan-ti", className: "Bard", gear: "Lute, rapier" },
      ],
      styleHint: "cinematic",
    });

    expect(result.prompt).toBe(SAMPLE_PROMPT_RESULT.prompt);

    const callArgs = mockGenerateContent.mock.calls[0][0];
    expect(callArgs.contents).toContain("Watkins");
    expect(callArgs.contents).toContain("Scarred face");
    expect(callArgs.contents).toContain("Cutlass");
    expect(callArgs.contents).toContain("Netanyahu");
    expect(callArgs.contents).toContain("Lute, rapier");
    expect(callArgs.contents).toContain("Session 6");
  });
});

describe("craftPartyPrompt", () => {
  it("returns prompt and reasoning", async () => {
    mockGenerateContent.mockResolvedValue(mockGeminiResponse(SAMPLE_PROMPT_RESULT));

    const result = await craftPartyPrompt({
      name: "Old Shell",
      race: "Tortle",
      className: "Ranger",
      subclass: "Hunter",
      equipment: "Longbow, leather armor",
      backstory: "A wandering hermit",
      characterMoments: "Tracked the beast through the forest",
      styleHint: "naturalistic",
    });

    expect(result.prompt).toBe(SAMPLE_PROMPT_RESULT.prompt);
    expect(result.reasoning).toBe(SAMPLE_PROMPT_RESULT.reasoning);

    const callArgs = mockGenerateContent.mock.calls[0][0];
    expect(callArgs.contents).toContain("Old Shell");
    expect(callArgs.contents).toContain("Tortle");
    expect(callArgs.contents).toContain("Hunter");
    expect(callArgs.contents).toContain("naturalistic");
  });
});

describe("blocked response handling", () => {
  it("returns blocked result when API returns blocked promptFeedback", async () => {
    mockGenerateContent.mockResolvedValue(mockBlockedResponse());

    const result = await craftNpcPrompt({ name: "Evil Guy", race: "Demon" });

    expect(result.prompt).toBe("blocked");
    expect(result.reasoning).toContain("filtered");
  });

  it("returns blocked result when text is null", async () => {
    mockGenerateContent.mockResolvedValue({ text: null, promptFeedback: null });

    const result = await craftNpcPrompt({ name: "Nobody", race: "Unknown" });

    expect(result.prompt).toBe("blocked");
    expect(result.reasoning).toContain("filtered");
  });
});

describe("429 retry", () => {
  it("retries on 429 and succeeds on second attempt", async () => {
    mockGenerateContent
      .mockRejectedValueOnce({ status: 429 })
      .mockResolvedValueOnce(mockGeminiResponse(SAMPLE_PROMPT_RESULT));

    const result = await craftNpcPrompt({ name: "Retry NPC", race: "Elf" });

    expect(result.prompt).toBe(SAMPLE_PROMPT_RESULT.prompt);
    expect(mockGenerateContent).toHaveBeenCalledTimes(2);
  });
});

describe("SyntaxError retry", () => {
  it("retries on invalid JSON and succeeds on second attempt", async () => {
    mockGenerateContent
      .mockResolvedValueOnce({ text: "not valid json", promptFeedback: null })
      .mockResolvedValueOnce(mockGeminiResponse(SAMPLE_PROMPT_RESULT));

    const result = await craftNpcPrompt({ name: "Parse NPC", race: "Dwarf" });

    expect(result.prompt).toBe(SAMPLE_PROMPT_RESULT.prompt);
    expect(result.reasoning).toBe(SAMPLE_PROMPT_RESULT.reasoning);
    expect(mockGenerateContent).toHaveBeenCalledTimes(2);
  });
});

describe("non-retryable error", () => {
  it("propagates errors that are not 429 or SyntaxError", async () => {
    mockGenerateContent.mockRejectedValue(new Error("API failure"));

    await expect(
      craftNpcPrompt({ name: "Error NPC", race: "Orc" })
    ).rejects.toThrow("API failure");
  });
});
