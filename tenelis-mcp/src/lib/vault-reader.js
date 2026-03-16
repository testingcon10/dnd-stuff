import { readFileSync, readdirSync, statSync } from "fs";
import path from "path";
import YAML from "yaml";
import { VAULT_ROOT } from "./file-utils.js";

export function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return { frontmatter: {}, body: content };
  const frontmatter = YAML.parse(match[1]) || {};
  const body = content.slice(match[0].length).replace(/^\r?\n/, "");
  return { frontmatter, body };
}

export function stripWikilinks(text) {
  return text.replace(/\[{2,}([^\[\]]*?)(?:\\?\|[^\]]*?)?\]{2,}/g, "$1");
}

function toCamelCase(heading) {
  const stripped = stripWikilinks(heading).replace(/[^a-zA-Z0-9\s]/g, "").trim();
  const words = stripped.split(/\s+/).filter(w => w);
  if (!words.length) return "";
  return words[0].toLowerCase() + words.slice(1).map(w => w[0].toUpperCase() + w.slice(1).toLowerCase()).join("");
}

export function parseSections(body) {
  const sections = {};
  const lines = body.split(/\r?\n/);
  let currentKey = null;
  let currentLines = [];

  for (const line of lines) {
    const h2Match = line.match(/^## (.+)$/);
    if (h2Match) {
      if (currentKey) {
        sections[currentKey] = currentLines.join("\n").trim();
      }
      currentKey = toCamelCase(h2Match[1]);
      currentLines = [];
    } else if (currentKey) {
      currentLines.push(line);
    }
  }
  if (currentKey) {
    sections[currentKey] = currentLines.join("\n").trim();
  }
  return sections;
}

export function extractWikilinks(markdown) {
  const matches = [];
  const imageExts = /\.(png|jpg|jpeg|gif|webp)$/i;
  const regex = /\[{2,}([^\[\]]*?)(?:\\?\|[^\]]*?)?\]{2,}/g;
  let m;
  while ((m = regex.exec(markdown)) !== null) {
    const target = m[1].replace(/^\[+/, "").replace(/\]+$/, "").trim();
    if (target && !target.includes("/") && !imageExts.test(target)) matches.push(target);
  }
  return [...new Set(matches)];
}

function findFile(directory, name, recursive = false) {
  const absDir = path.join(VAULT_ROOT, directory);
  const target = name.toLowerCase() + ".md";

  function searchDir(dir) {
    let entries;
    try { entries = readdirSync(dir, { withFileTypes: true }); } catch { return null; }

    for (const entry of entries) {
      if (entry.isFile() && entry.name.toLowerCase() === target) {
        return { filePath: path.join(dir, entry.name), fileName: entry.name };
      }
    }

    if (recursive) {
      for (const entry of entries) {
        if (entry.isDirectory()) {
          const result = searchDir(path.join(dir, entry.name));
          if (result) return result;
        }
      }
    }

    return null;
  }

  return searchDir(absDir);
}

function readAndParse(filePath) {
  const content = readFileSync(filePath, "utf-8");
  const { frontmatter, body } = parseFrontmatter(content);
  const sections = parseSections(body);
  return { filePath, frontmatter, sections };
}

export function readNpc(name) {
  const found = findFile("04 - NPCs", name);
  if (!found) return null;
  return readAndParse(found.filePath);
}

export function readLocation(name) {
  const found = findFile("06 - World/Locations", name, true);
  if (!found) return null;
  return readAndParse(found.filePath);
}

export function readSession(number) {
  const found = findFile("02 - Sessions", `Session ${number} Recap`);
  if (!found) return null;
  const content = readFileSync(found.filePath, "utf-8");
  const { frontmatter, body } = parseFrontmatter(content);
  const sections = parseSections(body);
  return { filePath: found.filePath, frontmatter, sections, fullMarkdown: content };
}

export function readPartyMember(name) {
  const found = findFile("01 - Party", name);
  if (!found) return null;
  return readAndParse(found.filePath);
}

export function readReferenceImages(aliasMap) {
  const refsDir = path.join(VAULT_ROOT, "assets", "references");
  const results = [];
  let entries;
  try { entries = readdirSync(refsDir); } catch { return results; }
  for (const [fullName, fileBase] of Object.entries(aliasMap)) {
    const match = entries.find(f =>
      f.replace(/\.[^.]+$/, "").toLowerCase() === fileBase.toLowerCase()
    );
    if (match) {
      const ext = path.extname(match).toLowerCase();
      const mimeTypes = { ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif" };
      const mimeType = mimeTypes[ext] || "image/jpeg";
      const data = readFileSync(path.join(refsDir, match), { encoding: "base64" });
      results.push({ name: fullName, mimeType, data });
    }
  }
  return results;
}

const RARITY_KEYWORDS = ["legendary", "very rare", "rare", "uncommon"];

const CLASS_WEAPON_PREFS = {
  barbarian: ["greataxe", "greatsword", "maul"],
  bard: ["rapier", "staff", "dagger"],
  fighter: ["longsword", "greatsword", "battleaxe"],
  ranger: ["longbow", "shortbow", "crossbow"],
  rogue: ["shortsword", "dagger", "rapier"],
};

function parseTableRows(markdown) {
  if (!markdown) return [];
  const rows = [];
  for (const line of markdown.split(/\r?\n/)) {
    if (!line.includes("|") || /^[|\s-]+$/.test(line) || line.startsWith("###")) continue;
    const cols = line.split("|").map(c => c.trim()).filter(c => c);
    if (cols.length < 2) continue;
    rows.push(cols);
  }
  return rows;
}

function findRarity(text) {
  const lower = (text || "").toLowerCase();
  return RARITY_KEYWORDS.find(r => lower.includes(r)) || null;
}

function fmtRarity(rarity) {
  return rarity.split(" ").map(w => w[0].toUpperCase() + w.slice(1)).join(" ");
}

export function extractVisualGear(sections, className) {
  const armor = [];
  const notableItems = [];

  for (const row of parseTableRows(sections.equipment)) {
    if (row[0] === "Item") continue;
    const itemName = stripWikilinks(row[0]);
    const notes = row[3] || "";
    const notesLower = notes.toLowerCase();

    if (notesLower.includes("equipped")) {
      armor.push(itemName);
    }

    const rarity = findRarity(notes);
    if (rarity && !itemName.toLowerCase().startsWith("potion")) {
      notableItems.push(`${itemName} (${fmtRarity(rarity)})`);
    }
  }

  let primaryWeapon = null;
  const weapons = [];
  for (const row of parseTableRows(sections.attacksSpellcasting)) {
    if (row[0] === "Name") continue;
    const name = stripWikilinks(row[0]);
    const notes = row[4] || "";
    const rarity = findRarity(notes);
    weapons.push({ name, rarity });
  }

  const rareWeapon = weapons.find(w => w.rarity);
  if (rareWeapon) {
    primaryWeapon = `${rareWeapon.name} (${fmtRarity(rareWeapon.rarity)})`;
  } else {
    const prefs = CLASS_WEAPON_PREFS[(className || "").toLowerCase()] || [];
    for (const pref of prefs) {
      const match = weapons.find(w => w.name.toLowerCase().includes(pref));
      if (match) { primaryWeapon = match.name; break; }
    }
    if (!primaryWeapon) {
      const nonClaws = weapons.find(w => w.name !== "Claws");
      primaryWeapon = nonClaws ? nonClaws.name : weapons[0]?.name || null;
    }
  }

  const lines = [];
  if (armor.length) lines.push(`Armor: ${armor.join(", ")}`);
  if (primaryWeapon) lines.push(`Weapon: ${primaryWeapon}`);
  if (notableItems.length) lines.push(`Notable items: ${notableItems.join(", ")}`);
  return lines.join(". ");
}

export function listFiles(directory, recursive = false) {
  const absDir = path.join(VAULT_ROOT, directory);
  try {
    const names = readdirSync(absDir, { withFileTypes: true });
    const results = names
      .filter(e => e.isFile() && e.name.endsWith(".md"))
      .map(e => e.name.replace(/\.md$/, ""));
    if (recursive) {
      for (const entry of names) {
        if (entry.isDirectory()) {
          const subDir = path.join(absDir, entry.name);
          try {
            const subNames = readdirSync(subDir)
              .filter(f => f.endsWith(".md"))
              .map(f => f.replace(/\.md$/, ""));
            results.push(...subNames);
          } catch { /* skip unreadable subdirs */ }
        }
      }
    }
    return results;
  } catch {
    return [];
  }
}
