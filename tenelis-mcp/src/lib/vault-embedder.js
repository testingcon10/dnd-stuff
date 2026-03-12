import { readFileSync, writeFileSync } from "fs";

function stripWikilinks(text) {
  return text.replace(/\[{2,}([^\[\]]*?)(?:\\?\|[^\]]*?)?\]{2,}/g, "$1");
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
    writeFileSync(filePath, lines.join("\n"));
    return { created: true };
  }

  for (let i = sectionIdx + 1; i < lines.length; i++) {
    if (lines[i].match(/^!\[\[.*\]\]$/)) {
      const existingFilename = lines[i].match(/!\[\[(.+)\]\]/)?.[1]?.split("/").pop();
      if (existingFilename === embedFilename) {
        return { replaced: false, alreadyExists: true };
      }
      lines[i] = embed;
      writeFileSync(filePath, lines.join("\n"));
      return { replaced: true };
    }
    if (lines[i].match(/^## /)) break;
  }

  let insertIdx = sectionIdx + 1;
  while (insertIdx < lines.length && lines[insertIdx].trim() === "") {
    insertIdx++;
  }

  lines.splice(insertIdx, 0, embed, "");
  writeFileSync(filePath, lines.join("\n"));
  return { inserted: true };
}

export function embedBeforeSection(filePath, newHeading, imagePath, beforeHeading) {
  const content = readFileSync(filePath, "utf-8");
  const lines = content.split(/\r?\n/);
  const embed = makeEmbed(imagePath);
  const embedFilename = imagePath.replace(/\\/g, "/").split("/").pop();

  for (let i = 0; i < lines.length; i++) {
    if (headingMatches(lines[i], newHeading)) {
      for (let j = i + 1; j < lines.length; j++) {
        if (lines[j].match(/^!\[\[.*\]\]$/)) {
          const existingFilename = lines[j].match(/!\[\[(.+)\]\]/)?.[1]?.split("/").pop();
          if (existingFilename === embedFilename) {
            return { replaced: false, alreadyExists: true };
          }
          lines[j] = embed;
          writeFileSync(filePath, lines.join("\n"));
          return { replaced: true };
        }
        if (lines[j].match(/^## /)) break;
      }
      const insertIdx = i + 1;
      lines.splice(insertIdx, 0, "", embed);
      writeFileSync(filePath, lines.join("\n"));
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
  writeFileSync(filePath, lines.join("\n"));
  return { created: true };
}
