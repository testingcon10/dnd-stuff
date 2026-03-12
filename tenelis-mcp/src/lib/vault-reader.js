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

function stripWikilinks(text) {
  return text.replace(/\[{2,}([^\[\]]*?)(?:\\?\|[^\]]*?)?\]{2,}/g, "$1");
}

function toCamelCase(heading) {
  const stripped = stripWikilinks(heading).replace(/[^a-zA-Z0-9\s]/g, "").trim();
  const words = stripped.split(/\s+/);
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
  const regex = /\[{2,}([^\[\]]*?)(?:\\?\|[^\]]*?)?\]{2,}/g;
  let m;
  while ((m = regex.exec(markdown)) !== null) {
    const target = m[1].replace(/^\[+/, "").replace(/\]+$/, "").trim();
    if (target) matches.push(target);
  }
  return [...new Set(matches)];
}

function findFile(directory, name, recursive = false) {
  const absDir = path.join(VAULT_ROOT, directory);
  const target = name.toLowerCase() + ".md";

  try {
    const entries = readdirSync(absDir, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isFile() && entry.name.toLowerCase() === target) {
        return { filePath: path.join(absDir, entry.name), fileName: entry.name };
      }
    }

    if (recursive) {
      for (const entry of entries) {
        if (entry.isDirectory()) {
          const subDir = path.join(absDir, entry.name);
          const subEntries = readdirSync(subDir, { withFileTypes: true });
          for (const sub of subEntries) {
            if (sub.isFile() && sub.name.toLowerCase() === target) {
              return { filePath: path.join(subDir, sub.name), fileName: sub.name };
            }
          }
        }
      }
    }
  } catch (e) {
    return null;
  }
  return null;
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

export function listFiles(directory) {
  const absDir = path.join(VAULT_ROOT, directory);
  try {
    return readdirSync(absDir)
      .filter(f => f.endsWith(".md"))
      .map(f => f.replace(/\.md$/, ""));
  } catch {
    return [];
  }
}
