import { describe, it, expect } from "vitest";
import {
  slugify,
  slugifyScene,
  getAssetPath,
  getRelativeAssetPath,
  VAULT_ROOT,
  ASSETS_DIR,
} from "../../src/lib/file-utils.js";

describe("slugify", () => {
  it("converts spaced names to lowercase kebab-case", () => {
    expect(slugify("Payton Hightower")).toBe("payton-hightower");
  });

  it("replaces apostrophes with hyphens", () => {
    expect(slugify("Kay'Dara")).toBe("kay-dara");
  });

  it("handles dot-space abbreviations", () => {
    expect(slugify("Netanyahu D. Kirkuenly")).toBe("netanyahu-d-kirkuenly");
  });

  it("handles multi-word names with articles", () => {
    expect(slugify("Amos the Storm")).toBe("amos-the-storm");
  });

  it("passes through already-lowercase single words", () => {
    expect(slugify("watkins")).toBe("watkins");
  });
});

describe("slugifyScene", () => {
  it("truncates to first 5 words then slugifies", () => {
    expect(slugifyScene("The party confronts Watkins at The Half Mast")).toBe(
      "the-party-confronts-watkins-at"
    );
  });

  it("handles a single word", () => {
    expect(slugifyScene("Battle")).toBe("battle");
  });
});

describe("getRelativeAssetPath", () => {
  it("returns assets/<category>/<filename> format", () => {
    expect(getRelativeAssetPath("npcs", "watkins.png")).toBe(
      "assets/npcs/watkins.png"
    );
  });

  it("works for different categories", () => {
    expect(getRelativeAssetPath("scenes", "tavern.png")).toBe(
      "assets/scenes/tavern.png"
    );
  });
});

describe("VAULT_ROOT and ASSETS_DIR", () => {
  it("VAULT_ROOT ends with Tenelis", () => {
    expect(VAULT_ROOT.replace(/\\/g, "/")).toMatch(/\/Tenelis$/);
  });

  it("ASSETS_DIR ends with Tenelis/assets", () => {
    expect(ASSETS_DIR.replace(/\\/g, "/")).toMatch(/\/Tenelis\/assets$/);
  });
});

describe("getAssetPath", () => {
  it("returns a path within ASSETS_DIR for an existing category", () => {
    const result = getAssetPath("npcs", "watkins.png");
    expect(result.replace(/\\/g, "/")).toContain("/assets/npcs/watkins.png");
    expect(result.startsWith(ASSETS_DIR)).toBe(true);
  });
});
