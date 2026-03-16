import { describe, it, expect } from "vitest";
import { blockedResponse, successResponse } from "../../src/lib/tool-responses.js";

describe("blockedResponse", () => {
  it("returns isError true", () => {
    const result = blockedResponse({ blockedPrompt: "bad prompt" }, "Try again");
    expect(result.isError).toBe(true);
  });

  it("includes error message, blockedPrompt, and suggestion in content", () => {
    const result = blockedResponse(
      { blockedPrompt: "bad prompt" },
      "Rephrase the description"
    );
    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.error).toBe("Image generation blocked by content filter");
    expect(parsed.blockedPrompt).toBe("bad prompt");
    expect(parsed.suggestion).toBe("Rephrase the description");
  });

  it("returns valid parseable JSON in content", () => {
    const result = blockedResponse({ blockedPrompt: "x" }, "y");
    expect(() => JSON.parse(result.content[0].text)).not.toThrow();
  });
});

describe("successResponse", () => {
  it("includes imagePath, prompt, reasoning, warnings, and reminder", () => {
    const input = {
      imagePath: "assets/npcs/watkins.png",
      prompt: "A grizzled sailor",
      reasoning: "Used pirate aesthetic",
      warnings: ["Low resolution"],
    };
    const result = successResponse(input);
    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.imagePath).toBe("assets/npcs/watkins.png");
    expect(parsed.prompt).toBe("A grizzled sailor");
    expect(parsed.reasoning).toBe("Used pirate aesthetic");
    expect(parsed.warnings).toEqual(["Low resolution"]);
    expect(parsed.reminder).toBe("Run link_vault.py if you added new entity names.");
  });

  it("does not set isError", () => {
    const result = successResponse({
      imagePath: "x",
      prompt: "y",
      reasoning: "z",
      warnings: [],
    });
    expect(result.isError).toBeUndefined();
  });

  it("works with empty warnings array", () => {
    const result = successResponse({
      imagePath: "assets/scenes/battle.png",
      prompt: "A battle scene",
      reasoning: "Epic fight",
      warnings: [],
    });
    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.warnings).toEqual([]);
  });

  it("returns valid parseable JSON in content", () => {
    const result = successResponse({
      imagePath: "a",
      prompt: "b",
      reasoning: "c",
      warnings: [],
    });
    expect(result.content[0].type).toBe("text");
    expect(() => JSON.parse(result.content[0].text)).not.toThrow();
  });
});
