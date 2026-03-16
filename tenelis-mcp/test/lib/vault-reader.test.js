import { describe, it, expect } from "vitest";
import {
  parseFrontmatter,
  stripWikilinks,
  parseSections,
  extractWikilinks,
  readNpc,
  readLocation,
  readSession,
  readPartyMember,
  readReferenceImages,
  extractVisualGear,
  listFiles,
} from "../../src/lib/vault-reader.js";

describe("parseFrontmatter", () => {
  it("parses standard YAML frontmatter into an object", () => {
    const content = [
      "---",
      'race: "Halfling"',
      'class: "Bartender"',
      "status: alive",
      "---",
      "",
      "## Appearance",
      "A short halfling.",
    ].join("\n");

    const { frontmatter, body } = parseFrontmatter(content);
    expect(frontmatter).toEqual({
      race: "Halfling",
      class: "Bartender",
      status: "alive",
    });
    expect(body).toContain("## Appearance");
  });

  it("returns empty frontmatter and full content as body when no frontmatter exists", () => {
    const content = "Just some plain markdown text.\n\n## Section";
    const { frontmatter, body } = parseFrontmatter(content);
    expect(frontmatter).toEqual({});
    expect(body).toBe(content);
  });

  it("handles empty content", () => {
    const { frontmatter, body } = parseFrontmatter("");
    expect(frontmatter).toEqual({});
    expect(body).toBe("");
  });

  it("handles frontmatter with arrays and nested values", () => {
    const content = [
      "---",
      "aliases:",
      "  - Net",
      "  - Nety",
      "tags: [character]",
      "---",
      "",
      "Body text",
    ].join("\n");

    const { frontmatter, body } = parseFrontmatter(content);
    expect(frontmatter.aliases).toEqual(["Net", "Nety"]);
    expect(frontmatter.tags).toEqual(["character"]);
    expect(body).toContain("Body text");
  });
});

describe("stripWikilinks", () => {
  it("removes wikilink brackets from a simple link", () => {
    expect(stripWikilinks("[[Booker Locke]]")).toBe("Booker Locke");
  });

  it("resolves aliased wikilinks to the target name", () => {
    expect(stripWikilinks("[[Netanyahu D. Kirkuenly|Net]]")).toBe(
      "Netanyahu D. Kirkuenly"
    );
  });

  it("strips multiple wikilinks from mixed text", () => {
    const input = "Talked to [[Watkins]] at [[The Half Mast]]";
    const result = stripWikilinks(input);
    expect(result).toBe("Talked to Watkins at The Half Mast");
  });

  it("returns unchanged text when no wikilinks are present", () => {
    const plain = "No links here, just text.";
    expect(stripWikilinks(plain)).toBe(plain);
  });

  it("handles empty string", () => {
    expect(stripWikilinks("")).toBe("");
  });
});

describe("parseSections", () => {
  it("keys sections by camelCase heading name", () => {
    const body = [
      "## Key Events",
      "Something happened.",
      "",
      "## Party Loot",
      "Found gold.",
    ].join("\n");

    const sections = parseSections(body);
    expect(sections).toHaveProperty("keyEvents");
    expect(sections).toHaveProperty("partyLoot");
    expect(sections.keyEvents).toContain("Something happened.");
    expect(sections.partyLoot).toContain("Found gold.");
  });

  it("handles multiple sections with content", () => {
    const body = [
      "## Appearance",
      "Tall and strong.",
      "",
      "## Personality",
      "Quiet but determined.",
      "",
      "## Background",
      "Grew up on a farm.",
    ].join("\n");

    const sections = parseSections(body);
    expect(Object.keys(sections)).toHaveLength(3);
    expect(sections.appearance).toContain("Tall");
    expect(sections.personality).toContain("Quiet");
    expect(sections.background).toContain("farm");
  });

  it("returns empty object for empty body", () => {
    expect(parseSections("")).toEqual({});
  });

  it("returns empty object for body with no h2 headings", () => {
    const body = "Just some text without any headings.";
    expect(parseSections(body)).toEqual({});
  });

  it("strips wikilinks from heading names when building keys", () => {
    const body = "## [[Ability Scores]]\n| STR | 10 |";
    const sections = parseSections(body);
    expect(sections).toHaveProperty("abilityScores");
  });
});

describe("extractWikilinks", () => {
  it("extracts unique entity names from wikilinks", () => {
    const md =
      "Met [[Watkins]] and [[Payton Hightower]] at [[The Half Mast]].";
    const links = extractWikilinks(md);
    expect(links).toContain("Watkins");
    expect(links).toContain("Payton Hightower");
    expect(links).toContain("The Half Mast");
  });

  it("deduplicates repeated wikilinks", () => {
    const md = "[[Watkins]] said hello. Later [[Watkins]] left.";
    const links = extractWikilinks(md);
    const watkinsCounts = links.filter((l) => l === "Watkins");
    expect(watkinsCounts).toHaveLength(1);
  });

  it("excludes image paths (file extensions)", () => {
    const md = "![[assets/npcs/watkins-portrait.png]]\n[[Watkins]]";
    const links = extractWikilinks(md);
    expect(links).not.toContain("assets/npcs/watkins-portrait.png");
    expect(links).toContain("Watkins");
  });

  it("excludes targets with slashes (paths)", () => {
    const md = "[[06 - World/Locations/Drayik]] and [[Drayik]]";
    const links = extractWikilinks(md);
    expect(links.some((l) => l.includes("/"))).toBe(false);
    expect(links).toContain("Drayik");
  });

  it("returns empty array for text with no wikilinks", () => {
    expect(extractWikilinks("No links here.")).toEqual([]);
  });

  it("handles aliased wikilinks by extracting the target", () => {
    const md = "[[Netanyahu D. Kirkuenly|Net]] cast a spell.";
    const links = extractWikilinks(md);
    expect(links).toContain("Netanyahu D. Kirkuenly");
  });
});

describe("readNpc", () => {
  it("returns correct frontmatter for an existing NPC (Watkins)", () => {
    const result = readNpc("Watkins");
    expect(result).not.toBeNull();
    expect(result.frontmatter.race).toBe("Halfling");
    expect(result.frontmatter.class).toBe("Bartender");
    expect(result.frontmatter.location).toBe("Drayik");
    expect(result.frontmatter.status).toBe("alive");
  });

  it("returns parsed sections for an existing NPC", () => {
    const result = readNpc("Watkins");
    expect(result).not.toBeNull();
    expect(result.sections).toHaveProperty("appearance");
    expect(result.sections).toHaveProperty("background");
    expect(result.sections).toHaveProperty("relationships");
  });

  it("includes filePath in the result", () => {
    const result = readNpc("Watkins");
    expect(result).not.toBeNull();
    expect(result.filePath).toBeDefined();
    expect(result.filePath.replace(/\\/g, "/")).toContain("04 - NPCs/Watkins");
  });

  it("returns sections with content for Payton Hightower", () => {
    const result = readNpc("Payton Hightower");
    expect(result).not.toBeNull();
    expect(result.sections).toHaveProperty("background");
    expect(result.sections.background.length).toBeGreaterThan(0);
    expect(result.sections).toHaveProperty("relationships");
    expect(result.sections.relationships.length).toBeGreaterThan(0);
  });

  it("returns null for a non-existent NPC", () => {
    expect(readNpc("Nonexistent McFakeName")).toBeNull();
  });

  it("is case-insensitive for NPC name lookup", () => {
    const result = readNpc("watkins");
    expect(result).not.toBeNull();
    expect(result.frontmatter.race).toBe("Halfling");
  });
});

describe("readLocation", () => {
  it("returns data for a top-level location (Drayik)", () => {
    const result = readLocation("Drayik");
    expect(result).not.toBeNull();
    expect(result.frontmatter.location_type).toBe("Settlement");
    expect(result.frontmatter.region).toBeDefined();
    expect(result.filePath).toBeDefined();
  });

  it("returns null for a non-existent location", () => {
    expect(readLocation("Atlantis the Lost City")).toBeNull();
  });
});

describe("readSession", () => {
  it("returns session data for session 6", () => {
    const result = readSession(6);
    expect(result).not.toBeNull();
    expect(result.fullMarkdown).toBeDefined();
    expect(typeof result.fullMarkdown).toBe("string");
    expect(result.fullMarkdown.length).toBeGreaterThan(0);
  });

  it("includes frontmatter with session metadata", () => {
    const result = readSession(6);
    expect(result).not.toBeNull();
    expect(result.frontmatter.session_number).toBe(6);
    expect(result.frontmatter.tags).toBeDefined();
  });

  it("includes parsed sections", () => {
    const result = readSession(6);
    expect(result).not.toBeNull();
    expect(typeof result.sections).toBe("object");
    expect(Object.keys(result.sections).length).toBeGreaterThan(0);
  });

  it("includes filePath", () => {
    const result = readSession(6);
    expect(result).not.toBeNull();
    expect(result.filePath.replace(/\\/g, "/")).toContain(
      "02 - Sessions/Session 6 Recap"
    );
  });

  it("returns null for a non-existent session", () => {
    expect(readSession(999)).toBeNull();
  });
});

describe("readPartyMember", () => {
  it("returns correct data for Netanyahu D. Kirkuenly", () => {
    const result = readPartyMember("Netanyahu D. Kirkuenly");
    expect(result).not.toBeNull();
    expect(result.frontmatter.player).toBe("Conor");
    expect(result.frontmatter.race).toBe("Yuan-ti");
    expect(result.frontmatter.class).toBe("Bard");
    expect(result.frontmatter.subclass).toBe("College of Lore");
  });

  it("includes sections for the party member", () => {
    const result = readPartyMember("Netanyahu D. Kirkuenly");
    expect(result).not.toBeNull();
    expect(typeof result.sections).toBe("object");
    expect(Object.keys(result.sections).length).toBeGreaterThan(0);
  });

  it("includes filePath", () => {
    const result = readPartyMember("Netanyahu D. Kirkuenly");
    expect(result).not.toBeNull();
    expect(result.filePath.replace(/\\/g, "/")).toContain(
      "01 - Party/Netanyahu D. Kirkuenly"
    );
  });

  it("returns null for a non-existent party member", () => {
    expect(readPartyMember("Gandalf the Grey")).toBeNull();
  });
});

describe("readReferenceImages", () => {
  it("returns base64 image data for known aliases", () => {
    const aliasMap = { "Booker Locke": "Booker" };
    const results = readReferenceImages(aliasMap);
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe("Booker Locke");
    expect(results[0].mimeType).toBe("image/jpeg");
    expect(typeof results[0].data).toBe("string");
    expect(results[0].data.length).toBeGreaterThan(0);
  });

  it("returns multiple images for multiple aliases", () => {
    const aliasMap = {
      "Booker Locke": "Booker",
      "Cassius Bellona": "Cassius",
      "Netanyahu D. Kirkuenly": "Net",
      "Old Shell": "OldShell",
    };
    const results = readReferenceImages(aliasMap);
    expect(results).toHaveLength(4);
    const names = results.map((r) => r.name);
    expect(names).toContain("Booker Locke");
    expect(names).toContain("Cassius Bellona");
    expect(names).toContain("Netanyahu D. Kirkuenly");
    expect(names).toContain("Old Shell");
  });

  it("returns correct mimeType for jpg files", () => {
    const results = readReferenceImages({ "Cassius Bellona": "Cassius" });
    expect(results).toHaveLength(1);
    expect(results[0].mimeType).toBe("image/jpeg");
  });

  it("returns empty array for non-existent reference", () => {
    const results = readReferenceImages({ "Nobody Real": "nobody" });
    expect(results).toEqual([]);
  });

  it("returns empty array for empty alias map", () => {
    const results = readReferenceImages({});
    expect(results).toEqual([]);
  });
});

describe("extractVisualGear", () => {
  it("produces a gear string from a known party member's sections", () => {
    const member = readPartyMember("Netanyahu D. Kirkuenly");
    expect(member).not.toBeNull();
    const gear = extractVisualGear(member.sections, "Bard");
    expect(typeof gear).toBe("string");
  });

  it("returns empty string when sections lack equipment and attacks", () => {
    const emptySections = {};
    const gear = extractVisualGear(emptySections, "Fighter");
    expect(gear).toBe("");
  });

  it("returns empty string when equipment table has no rows", () => {
    const sections = {
      equipment: "| Item | Qty | Weight | Notes |\n|---|---|---|---|",
      attacksSpellcasting: "| Name | Atk | Dmg | Type | Notes |\n|---|---|---|---|---|",
    };
    const gear = extractVisualGear(sections, "Rogue");
    expect(gear).toBe("");
  });

  it("picks up equipped armor from the equipment table notes column", () => {
    const sections = {
      equipment: [
        "| Item | Qty | Weight | Notes |",
        "| --- | --- | --- | --- |",
        "| Studded Leather | 1 | 13 lb | Equipped |",
        "| Backpack | 1 | 5 lb | |",
      ].join("\n"),
    };
    const gear = extractVisualGear(sections, "Rogue");
    expect(gear).toContain("Armor: Studded Leather");
    expect(gear).not.toContain("Backpack");
  });

  it("includes rare items with formatted rarity", () => {
    const sections = {
      equipment: [
        "| Item | Qty | Weight | Notes |",
        "| --- | --- | --- | --- |",
        "| Staff of Healing | 1 | 4 lb | Rare, Attuned |",
        "| Rope | 1 | 10 lb | |",
      ].join("\n"),
    };
    const gear = extractVisualGear(sections, "Bard");
    expect(gear).toContain("Staff of Healing (Rare)");
    expect(gear).not.toContain("Rope");
  });

  it("selects preferred weapon based on class weapon preferences", () => {
    const sections = {
      attacksSpellcasting: [
        "| Name | Atk Bonus | Damage | Range | Notes |",
        "| --- | --- | --- | --- | --- |",
        "| Rapier | +5 | 1d8+3 | Melee | |",
        "| Dagger | +5 | 1d4+3 | 20/60 | |",
      ].join("\n"),
    };
    const gear = extractVisualGear(sections, "Bard");
    expect(gear).toContain("Weapon: Rapier");
  });

  it("filters Claws from weapon fallback selection", () => {
    const sections = {
      attacksSpellcasting: [
        "| Name | Atk Bonus | Damage | Range | Notes |",
        "| --- | --- | --- | --- | --- |",
        "| Claws | +4 | 1d4+2 | Melee | |",
        "| Dagger | +5 | 1d4+3 | 20/60 | |",
      ].join("\n"),
    };
    const gear = extractVisualGear(sections, "Wizard");
    expect(gear).toContain("Weapon: Dagger");
    expect(gear).not.toContain("Claws");
  });
});

describe("listFiles", () => {
  it("lists NPC files from the vault", () => {
    const files = listFiles("04 - NPCs");
    expect(Array.isArray(files)).toBe(true);
    expect(files.length).toBeGreaterThan(0);
    expect(files).toContain("Watkins");
    expect(files).toContain("Payton Hightower");
  });

  it("returns strings without .md extension", () => {
    const files = listFiles("04 - NPCs");
    for (const f of files) {
      expect(f).not.toMatch(/\.md$/);
    }
  });

  it("returns empty array for a non-existent directory", () => {
    const files = listFiles("nonexistent-directory-xyz");
    expect(files).toEqual([]);
  });

  it("lists party member files", () => {
    const files = listFiles("01 - Party");
    expect(files.length).toBeGreaterThan(0);
    expect(files).toContain("Netanyahu D. Kirkuenly");
  });

  it("lists session files", () => {
    const files = listFiles("02 - Sessions");
    expect(files.length).toBeGreaterThan(0);
    expect(files).toContain("Session 6 Recap");
  });
});
