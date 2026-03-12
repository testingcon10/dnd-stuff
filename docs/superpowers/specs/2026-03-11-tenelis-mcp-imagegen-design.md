# Tenelis Image Generation MCP Server - Design Spec

## Overview

An MCP server that generates NPC portraits, location art, scene illustrations, and party portraits for the Tenelis D&D 5e Obsidian vault. Orchestrates two Google AI models: Gemini 2.5 Flash (crafts image prompts from vault context) and Imagen 4 (generates images). Saves images to the vault's assets directory and auto-embeds them in the source notes.

## Architecture

```
Claude Code (reads vault, picks what to generate)
    |
    v
MCP Server (tenelis-mcp) via StdioServerTransport
    |
    +-- Tool handler (one of 4)
         |
         vault-reader.js  -->  gemini-director.js  -->  imagen-generator.js  -->  vault-embedder.js
         (parse .md files)     (Gemini 2.5 Flash)      (Imagen 4 + base64)      (insert ![[img]])
```

- ESM modules (`"type": "module"` in package.json)
- Node 18+
- Single `GOOGLE_API_KEY` env var for both Gemini and Imagen (same SDK instance)
- Dependencies: `@google/genai`, `@modelcontextprotocol/sdk`, `yaml`, `zod`

## Directory Structure

```
Tenelis/
  .mcp.json
  tenelis-mcp/
    package.json
    src/
      index.js                      # MCP server entry + tool registration
      tools/
        generate-npc-portrait.js
        generate-location-art.js
        generate-scene.js
        generate-party-portrait.js
      lib/
        vault-reader.js             # Parse vault markdown files
        gemini-director.js          # Gemini prompt crafting
        imagen-generator.js         # Imagen API + file saving
        vault-embedder.js           # Update notes with image embeds
        file-utils.js               # Slugify, paths, directory creation
```

## Core Libraries

### file-utils.js

- `slugify(name)` - lowercase, strip apostrophes/special chars, spaces to hyphens. Examples: `Kay'Dara` -> `kay-dara`, `Netanyahu D. Kirkuenly` -> `netanyahu-d-kirkuenly`, `Booker Locke` -> `booker-locke`. For scene slugs, truncate to first 5 words: `"The party fights through the catacombs beneath Drayik"` -> `the-party-fights-through-the`
- `getVaultRoot()` - resolves to `Tenelis/` (inner vault dir) relative to project root
- `getAssetPath(category, filename)` - returns `assets/{category}/{filename}`, ensures directory exists
- `VAULT_ROOT`, `ASSETS_DIR` constants

### vault-reader.js

Parses YAML frontmatter with `yaml` package. Extracts sections by `##` headings. Case-insensitive file matching by filename (not aliases).

**Section key normalization:** Heading text is lowercased, `[[wikilinks]]` are stripped, and spaces are converted to camelCase. Examples: `## Notable Features` -> `notableFeatures`, `## Attacks & Spellcasting` -> `attacksSpellcasting`, `## [[History]]` -> `history`.

**Optional frontmatter fields:** Many fields are optional or empty strings across different file types. The reader returns whatever exists; consumers handle missing data gracefully.

| Function | Source Directory | Returns |
|----------|-----------------|---------|
| `readNpc(name)` | `04 - NPCs/` | `{ filePath, frontmatter: { race, class, faction, status, attitude?, location? }, sections }` - returns all sections (appearance, personality, background, relationships, interactionLog, notes, etc.) |
| `readLocation(name)` | `06 - World/Locations/` (recursive) | `{ filePath, frontmatter: { location_type, region, population? }, sections: { description, notableFeatures } }` |
| `readSession(number)` | `02 - Sessions/` | `{ filePath, frontmatter: { session_number, session_date }, fullMarkdown, sections }` - returns ALL sections (summary, keyEvents, characterMoments, combatEncounters, highlights, memorableQuotes, npcsEncountered, openThreads, etc.) plus `fullMarkdown` for wikilink extraction |
| `readPartyMember(name)` | `01 - Party/` | `{ filePath, frontmatter: { race, class, subclass, level, player }, sections }` - returns all sections (attacksSpellcasting, featuresTraits, equipment, backstory, personality, spellcasting?, etc.) |
| `listFiles(directory)` | any | Available filenames (for "file not found" error messages) |

**Notes:**
- `readLocation` searches recursively since locations nest under region dirs (e.g., `Drayik/Catacombs.md`). Filename match takes priority.
- `readSession` returns all sections and full markdown because scene generation needs the complete recap for wikilink extraction and context. The highlights and memorable quotes sections often contain the most evocative descriptions.
- `readPartyMember` returns all sections but `personality` has limited visual utility for image prompts (some characters have it filled, most don't). Primary visual context comes from race/class/equipment in frontmatter and character moments from session recaps.
- NPC `frontmatter.location` is often an empty string - callers must check before attempting `readLocation`.

### gemini-director.js

Single `GoogleGenAI` instance. Model: `gemini-2.5-flash`.

System prompt establishes it as a "visual director for a dark fantasy D&D 5e campaign." Default art style baseline: "detailed fantasy illustration, painterly, D&D sourcebook art style."

| Function | Input | Output |
|----------|-------|--------|
| `craftNpcPrompt(context)` | NPC data + optional location context | `{ prompt, reasoning }` |
| `craftLocationPrompt(context)` | Location data + optional parent location | `{ prompt, reasoning }` |
| `craftScenePrompt(context)` | Session recap + referenced NPC/location data + scene description | `{ prompt, reasoning }` |
| `craftPartyPrompt(context)` | Character sheet + character moments from recaps | `{ prompt, reasoning }` |

- Prompt output capped at ~200 words
- User's `style_hint` appended to override/augment the default style
- Reasoning explains visual choices made

### imagen-generator.js

Same `GoogleGenAI` instance. Model: `imagen-4.0-generate-001`.

`generateImage(prompt, { aspectRatio, outputPath })`

Config:
- `numberOfImages: 1`
- `enhancePrompt: false` (Gemini already crafted the prompt - avoids double-rewriting and preserves vault-context fidelity)
- `personGeneration: "ALLOW_ADULT"` (default, appropriate for D&D characters)

Process:
1. Call `ai.models.generateImages()`
2. Decode base64 `imageBytes` from response
3. Write PNG to `outputPath`

### vault-embedder.js

`embedImage(filePath, sectionHeading, imagePath)`

- Finds `## {heading}` in the target file. Matching strips `[[wikilinks]]` from heading text before comparing (e.g., searching for "Ability Scores" matches `## [[Ability Scores]]`).
- Inserts `![[{imagePath}]]` on first blank line after heading
- Idempotent - replaces existing embed for same path
- If target section doesn't exist, creates it before `## DM Notes` or at end of file

`embedBeforeSection(filePath, newHeading, imagePath, beforeHeading)` - variant for party portraits: creates `## Portrait` section with embed, placed before `beforeHeading` (e.g., "Ability Scores"). Also handles wikilink-wrapped headings when matching `beforeHeading`.

## MCP Tools

### generate_npc_portrait

**Schema:** `{ npc_name: string (required), style_hint?: string, aspect_ratio?: string (default "3:4") }`

**Pipeline:**
1. `readNpc(name)` - get NPC data
2. If `frontmatter.location` is non-empty, `readLocation(frontmatter.location)` for environmental context (skip if empty)
3. `craftNpcPrompt(context)` - Gemini crafts the image prompt
4. `generateImage(prompt, { aspectRatio, outputPath: assets/npcs/{slug}-portrait.png })`
5. `embedImage(npcFile, "Appearance", relativePath)`

**Returns:** `{ imagePath, prompt, reasoning, warnings[] }`

### generate_location_art

**Schema:** `{ location_name: string (required), parent_location?: string, style_hint?: string, aspect_ratio?: string (default "16:9") }`

**Pipeline:**
1. `readLocation(name)`
2. Optionally `readLocation(parent)` for regional context
3. `craftLocationPrompt(context)`
4. `generateImage(...)` -> `assets/locations/{slug}.png`
5. `embedImage(locationFile, "Description", relativePath)`

### generate_scene

**Schema:** `{ session_number: number (required), scene_description: string (required), style_hint?: string, aspect_ratio?: string (default "16:9") }`

**Pipeline:**
1. `readSession(number)`
2. Extract referenced NPCs/locations from `[[wikilinks]]` in recap
3. `readNpc`/`readLocation` for each (best-effort, skip failures)
4. `craftScenePrompt(context)`
5. `generateImage(...)` -> `assets/scenes/session-{N}-{slug}.png`
6. `embedImage(sessionFile, "Illustrations", relativePath)` - creates `## Illustrations` before `## DM Notes` if missing

### generate_party_portrait

**Schema:** `{ character_name: string (required), style_hint?: string, aspect_ratio?: string (default "3:4") }`

**Pipeline:**
1. `readPartyMember(name)` - visual context primarily from race/class/subclass/equipment
2. Scan session recaps for character moments mentioning this character (match by wikilink target e.g. `[[Netanyahu D. Kirkuenly|Netanyahu]]`, not display alias)
3. `craftPartyPrompt(context)`
4. `generateImage(...)` -> `assets/party/{slug}-portrait.png`
5. `embedBeforeSection(characterFile, "Portrait", relativePath, "Ability Scores")` - adds `## Portrait` section with image embed, placed before `## [[Ability Scores]]`. Creates the section if missing.

### Common Response Shape

All tools return: `{ imagePath, prompt, reasoning, warnings[] }`

All tools include a reminder: "Run link_vault.py if you added new entity names."

## MCP Server Config

`.mcp.json` at project root:

```json
{
  "mcpServers": {
    "tenelis-imagegen": {
      "command": "node",
      "args": ["tenelis-mcp/src/index.js"],
      "env": {
        "GOOGLE_API_KEY": "{{env:GOOGLE_API_KEY}}"
      }
    }
  }
}
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| File not found | Return available file list so Claude can correct the name |
| Sparse vault data | Proceed anyway - Gemini infers from race/class/faction. Note in `warnings[]` |
| Content filter block | Return the blocked prompt with suggestion to adjust `style_hint` |
| Rate limit (Imagen) | Retry once with 2s delay, then return error |
| Gemini failure | Retry once, then return error |
| Embed failure | Image still saved, report embed failure separately in response |

## Edge Cases

- NPC names with apostrophes: `Kay'Dara` -> `kay-dara` (strip in slugify)
- Person generation: `ALLOW_ADULT` is the default, appropriate for D&D. If blocked, error suggests environmental/silhouette style via `style_hint`
- Obsidian image paths: use `![[assets/npcs/filename.png]]` with full vault-relative path. Obsidian is configured with default "shortest path" link format and `attachmentFolderPath: "assets"` - full paths resolve correctly.
- `link_vault.py`: NOT auto-run from MCP server - remind in tool response
- Location search is recursive (locations nested under region dirs like `Drayik/`). Filename match takes priority over directory names.
- NPC `location` frontmatter is often empty string - check before attempting location read for environmental context.

## Implementation Phases

### Phase 1: Scaffold + Core Libs
1. Create `tenelis-mcp/` with `package.json`, `npm install`
2. `file-utils.js` - slugify, path resolution, ensureDir
3. `vault-reader.js` - markdown parsing, frontmatter extraction, section extraction
4. Verify vault reading works against known files (Eileen Whitebeak, Drayik, Session 5)

### Phase 2: Gemini Integration
5. `gemini-director.js` - prompt crafting for all 4 tool types
6. Test: log crafted prompts without generating images

### Phase 3: Imagen Integration
7. `imagen-generator.js` - image generation + file writing
8. Create `assets/npcs/`, `assets/locations/`, `assets/scenes/`, `assets/party/`
9. End-to-end test: generate one NPC portrait

### Phase 4: Vault Embedding
10. `vault-embedder.js` - markdown note updates
11. Test embedding against a vault file

### Phase 5: MCP Wiring
12. `index.js` - McpServer setup with StdioServerTransport
13. Four tool handlers in `src/tools/`
14. `.mcp.json` at project root

### Phase 6: Verify
15. Restart Claude Code, test each tool
16. Run `link_vault.py` after vault updates
17. Open Obsidian, confirm images render

## Key Design Decisions

1. **Approach A (spec as-written):** 4 separate tool files, 4 lib modules, clean pipeline pattern. No premature abstraction.
2. **`enhancePrompt: false`:** Gemini Flash crafts context-aware prompts; Imagen executes them as-is. Avoids double-rewriting and preserves vault-context fidelity. Also improves debuggability - one clear chain from context to image.
3. **ESM modules:** Aligns with `@google/genai` SDK examples and modern Node.js.
4. **Single SDK instance:** Both Gemini and Imagen use the same `@google/genai` package and `GOOGLE_API_KEY`.
