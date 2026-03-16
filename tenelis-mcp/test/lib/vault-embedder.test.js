import { vi, describe, it, expect, beforeEach } from "vitest";
import { readFileSync, writeFileSync } from "fs";

vi.mock("fs", async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, readFileSync: vi.fn(), writeFileSync: vi.fn() };
});

import { embedImage, embedBeforeSection } from "../../src/lib/vault-embedder.js";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("embedImage", () => {
  it("inserts embed after blank line when section exists with no embeds", () => {
    readFileSync.mockReturnValue(
      "---\nname: Watkins\n---\n\n## Appearance\n\nA halfling bartender.\n\n## Background\nSome background.\n"
    );

    const result = embedImage("test.md", "Appearance", "assets/npcs/watkins-portrait.png");

    expect(result).toEqual({ inserted: true });
    expect(writeFileSync).toHaveBeenCalledOnce();
    const written = writeFileSync.mock.calls[0][1];
    expect(written).toContain("![[assets/npcs/watkins-portrait.png]]");
    const lines = written.split("\n");
    const headingIdx = lines.indexOf("## Appearance");
    const embedIdx = lines.indexOf("![[assets/npcs/watkins-portrait.png]]");
    expect(embedIdx).toBeGreaterThan(headingIdx);
    expect(embedIdx).toBeLessThan(lines.indexOf("## Background"));
  });

  it("inserts after existing embed when section already has one", () => {
    readFileSync.mockReturnValue(
      "## Appearance\n![[assets/npcs/old-portrait.png]]\nSome description.\n\n## Background\n"
    );

    const result = embedImage("test.md", "Appearance", "assets/npcs/new-portrait.png");

    expect(result).toEqual({ inserted: true });
    const written = writeFileSync.mock.calls[0][1];
    const lines = written.split("\n");
    const oldIdx = lines.indexOf("![[assets/npcs/old-portrait.png]]");
    const newIdx = lines.indexOf("![[assets/npcs/new-portrait.png]]");
    expect(newIdx).toBe(oldIdx + 1);
  });

  it("returns alreadyExists when same embed filename is present", () => {
    readFileSync.mockReturnValue(
      "## Appearance\n![[assets/npcs/watkins-portrait.png]]\nDescription.\n\n## Background\n"
    );

    const result = embedImage("test.md", "Appearance", "assets/npcs/watkins-portrait.png");

    expect(result).toEqual({ replaced: false, alreadyExists: true });
    expect(writeFileSync).not.toHaveBeenCalled();
  });

  it("creates section before DM Notes when heading not found", () => {
    readFileSync.mockReturnValue(
      "## Background\nSome background.\n\n## DM Notes\nSecret info.\n"
    );

    const result = embedImage("test.md", "Appearance", "assets/npcs/portrait.png");

    expect(result).toEqual({ created: true });
    const written = writeFileSync.mock.calls[0][1];
    const lines = written.split("\n");
    const appearanceIdx = lines.indexOf("## Appearance");
    const dmNotesIdx = lines.indexOf("## DM Notes");
    expect(appearanceIdx).toBeGreaterThan(-1);
    expect(appearanceIdx).toBeLessThan(dmNotesIdx);
    expect(written).toContain("![[assets/npcs/portrait.png]]");
  });

  it("appends section at end when heading not found and no DM Notes", () => {
    readFileSync.mockReturnValue(
      "## Background\nSome background.\n"
    );

    const result = embedImage("test.md", "Appearance", "assets/npcs/portrait.png");

    expect(result).toEqual({ created: true });
    const written = writeFileSync.mock.calls[0][1];
    expect(written).toContain("## Appearance");
    expect(written).toContain("![[assets/npcs/portrait.png]]");
    const lines = written.split("\n");
    const appearanceIdx = lines.indexOf("## Appearance");
    expect(appearanceIdx).toBeGreaterThan(lines.indexOf("## Background"));
  });

  it("preserves \\r\\n line endings", () => {
    readFileSync.mockReturnValue(
      "## Appearance\r\n\r\nA description.\r\n\r\n## Background\r\nSome background.\r\n"
    );

    embedImage("test.md", "Appearance", "assets/npcs/portrait.png");

    const written = writeFileSync.mock.calls[0][1];
    expect(written).toContain("\r\n");
    expect(written).not.toMatch(/(?<!\r)\n/);
  });

  it("converts backslashes to forward slashes in embed path", () => {
    readFileSync.mockReturnValue(
      "## Appearance\n\nDescription.\n"
    );

    embedImage("test.md", "Appearance", "assets\\npcs\\test.png");

    const written = writeFileSync.mock.calls[0][1];
    expect(written).toContain("![[assets/npcs/test.png]]");
    expect(written).not.toContain("\\");
  });
});

describe("embedBeforeSection", () => {
  it("creates new heading before target section", () => {
    readFileSync.mockReturnValue(
      "## Stats\nSome stats.\n\n## Ability Scores\nSTR 10 DEX 14\n"
    );

    const result = embedBeforeSection("test.md", "Portrait", "img.png", "Ability Scores");

    expect(result).toEqual({ created: true });
    const written = writeFileSync.mock.calls[0][1];
    const lines = written.split("\n");
    const portraitIdx = lines.indexOf("## Portrait");
    const abilityIdx = lines.indexOf("## Ability Scores");
    expect(portraitIdx).toBeGreaterThan(-1);
    expect(portraitIdx).toBeLessThan(abilityIdx);
    expect(written).toContain("![[img.png]]");
  });

  it("adds embed under existing heading (updated)", () => {
    readFileSync.mockReturnValue(
      "## Portrait\nExisting content.\n\n## Ability Scores\nSTR 10\n"
    );

    const result = embedBeforeSection("test.md", "Portrait", "img.png", "Ability Scores");

    expect(result).toEqual({ updated: true });
    const written = writeFileSync.mock.calls[0][1];
    expect(written).toContain("![[img.png]]");
  });

  it("inserts after existing embed when heading exists with embed", () => {
    readFileSync.mockReturnValue(
      "## Portrait\n![[old.png]]\n\n## Ability Scores\n"
    );

    const result = embedBeforeSection("test.md", "Portrait", "new.png", "Ability Scores");

    expect(result).toEqual({ inserted: true });
    const written = writeFileSync.mock.calls[0][1];
    const lines = written.split("\n");
    const oldIdx = lines.indexOf("![[old.png]]");
    const newIdx = lines.indexOf("![[new.png]]");
    expect(newIdx).toBe(oldIdx + 1);
  });

  it("returns alreadyExists when embed filename already present", () => {
    readFileSync.mockReturnValue(
      "## Portrait\n![[img.png]]\n\n## Ability Scores\n"
    );

    const result = embedBeforeSection("test.md", "Portrait", "img.png", "Ability Scores");

    expect(result).toEqual({ replaced: false, alreadyExists: true });
    expect(writeFileSync).not.toHaveBeenCalled();
  });

  it("appends at end when target beforeHeading not found", () => {
    readFileSync.mockReturnValue(
      "## Stats\nSome stats.\n"
    );

    const result = embedBeforeSection("test.md", "Portrait", "img.png", "Ability Scores");

    expect(result).toEqual({ created: true });
    const written = writeFileSync.mock.calls[0][1];
    const lines = written.split("\n");
    const portraitIdx = lines.indexOf("## Portrait");
    expect(portraitIdx).toBeGreaterThan(lines.indexOf("## Stats"));
    expect(written).toContain("![[img.png]]");
  });

  it("matches heading containing wikilinks", () => {
    readFileSync.mockReturnValue(
      "## Stats\nSome stats.\n\n## [[Ability Scores]]\nSTR 10\n"
    );

    const result = embedBeforeSection("test.md", "Portrait", "img.png", "Ability Scores");

    expect(result).toEqual({ created: true });
    const written = writeFileSync.mock.calls[0][1];
    const lines = written.split("\n");
    const portraitIdx = lines.indexOf("## Portrait");
    const abilityIdx = lines.indexOf("## [[Ability Scores]]");
    expect(portraitIdx).toBeGreaterThan(-1);
    expect(portraitIdx).toBeLessThan(abilityIdx);
  });
});
