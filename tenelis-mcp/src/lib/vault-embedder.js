import { readFileSync, writeFileSync } from "fs";
import { stripWikilinks } from "./vault-reader.js";

function scanEmbeds(lines, startIdx, embedFilename) {
  let lastEmbedIdx = -1;
  for (let i = startIdx; i < lines.length; i++) {
    if (lines[i].match(/^## /)) break;
    if (lines[i].match(/^!\[\[.*\]\]$/)) {
      const existing = lines[i].match(/!\[\[(.+)\]\]/)?.[1]?.split("/").pop();
      if (existing === embedFilename) return { alreadyExists: true, lastEmbedIdx: -1 };
      lastEmbedIdx = i;
    }
  }
  return { alreadyExists: false, lastEmbedIdx };
}

function headingMatches(headingLine, target) {
  const match = headingLine.match(/^## (.+)$/);
  if (!match) return false;
  return stripWikilinks(match[1]).trim().toLowerCase() === target.toLowerCase();
}

function makeEmbed(imagePath) {
  return `![[${imagePath.replace(/\\/g, "/")}]]`;
}

export function embedImage(filePath, sectionHeading, imagePath) {
  const content = readFileSync(filePath, "utf-8");
  const lineEnding = content.includes("\r\n") ? "\r\n" : "\n";
  const lines = content.split(/\r?\n/);
  const embed = makeEmbed(imagePath);
  const embedFilename = imagePath.replace(/\\/g, "/").split("/").pop();

  let sectionIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (headingMatches(lines[i], sectionHeading)) {
      sectionIdx = i;
      break;
    }
  }

  if (sectionIdx === -1) {
    let insertIdx = lines.length;
    for (let i = 0; i < lines.length; i++) {
      if (headingMatches(lines[i], "DM Notes")) {
        insertIdx = i;
        break;
      }
    }
    lines.splice(insertIdx, 0, "", `## ${sectionHeading}`, "", embed, "");
    writeFileSync(filePath, lines.join(lineEnding));
    return { created: true };
  }

  const scan = scanEmbeds(lines, sectionIdx + 1, embedFilename);
  if (scan.alreadyExists) return { replaced: false, alreadyExists: true };

  if (scan.lastEmbedIdx !== -1) {
    lines.splice(scan.lastEmbedIdx + 1, 0, embed);
    writeFileSync(filePath, lines.join(lineEnding));
    return { inserted: true };
  }

  let insertIdx = sectionIdx + 1;
  while (insertIdx < lines.length && lines[insertIdx].trim() === "") {
    insertIdx++;
  }

  lines.splice(insertIdx, 0, embed, "");
  writeFileSync(filePath, lines.join(lineEnding));
  return { inserted: true };
}

export function embedBeforeSection(filePath, newHeading, imagePath, beforeHeading) {
  const content = readFileSync(filePath, "utf-8");
  const lineEnding = content.includes("\r\n") ? "\r\n" : "\n";
  const lines = content.split(/\r?\n/);
  const embed = makeEmbed(imagePath);
  const embedFilename = imagePath.replace(/\\/g, "/").split("/").pop();

  for (let i = 0; i < lines.length; i++) {
    if (headingMatches(lines[i], newHeading)) {
      const scan = scanEmbeds(lines, i + 1, embedFilename);
      if (scan.alreadyExists) return { replaced: false, alreadyExists: true };
      if (scan.lastEmbedIdx !== -1) {
        lines.splice(scan.lastEmbedIdx + 1, 0, embed);
        writeFileSync(filePath, lines.join(lineEnding));
        return { inserted: true };
      }
      const insertIdx = i + 1;
      lines.splice(insertIdx, 0, "", embed);
      writeFileSync(filePath, lines.join(lineEnding));
      return { updated: true };
    }
  }

  let beforeIdx = lines.length;
  for (let i = 0; i < lines.length; i++) {
    if (headingMatches(lines[i], beforeHeading)) {
      beforeIdx = i;
      break;
    }
  }

  lines.splice(beforeIdx, 0, `## ${newHeading}`, "", embed, "");
  writeFileSync(filePath, lines.join(lineEnding));
  return { created: true };
}
