# Tenelis Project - Workflow Diagram

## Project Architecture

```
C:\Users\cfpor\Projects\Tenelis\
|
|-- CLAUDE.md                          # Project instructions for Claude
|-- .mcp.json                          # MCP server config (tenelis-imagegen)
|-- .gitignore
|-- update-vault.bat                   # Quick vault sync (git fetch + reset)
|
|-- [Python Scripts - Vault Automation]
|   |-- populate_sheets.py             # Step 1: Foundry VTT JSON -> character sheets
|   |-- link_vault.py                  # Step 2: Auto-wikilink entity names
|   |-- generate_reference_content.py  # Generate 5e reference pages
|   |-- generate_items.py              # Generate item pages from items_data.json
|   |-- generate_index_files.py        # Generate index/hub pages
|   |-- add_spells.py                  # Add spell reference pages
|   |-- update_spells_2024.py          # Update spells (2024 revision)
|   |-- update_spells_xphb.py          # Update spells (XPHB data)
|   |-- update_feats_2024.py           # Update feats (2024 revision)
|   |-- add_tce_scc_content.py         # Add Tasha's/Strixhaven content
|   |-- reorganize_vault.py            # Vault structure reorganization
|
|-- [Data Files]
|   |-- items_data.json                # Item definitions
|   |-- spell_sources.json             # Spell source data
|   |-- xphb_spells.json               # XPHB spell data
|   |-- reorganize_manifest.json       # Vault reorg manifest
|
|-- tenelis-mcp/                       # MCP Server - Image Generation
|   |-- src/
|   |   |-- index.js                   # MCP server entry point
|   |   |-- lib/
|   |   |   |-- gemini-director.js     # Gemini AI - prompt direction
|   |   |   |-- imagen-generator.js    # Google Imagen - image generation
|   |   |   |-- vault-reader.js        # Read vault markdown files
|   |   |   |-- vault-embedder.js      # Embed images into vault files
|   |   |   |-- file-utils.js          # File system utilities
|   |   |   |-- tool-responses.js      # Standardized tool responses
|   |   |-- tools/
|   |       |-- generate-npc-portrait.js    # NPC portrait generation
|   |       |-- generate-location-art.js    # Location artwork generation
|   |       |-- generate-party-portrait.js  # Party portrait generation
|   |       |-- generate-scene.js           # Scene illustration generation
|
|-- Tenelis/                           # Obsidian Vault Root
    |-- 00 - Home.md                   # Campaign dashboard
    |-- 00 - Player Setup Guide.md     # Player onboarding
    |-- 01 - Party/                    # 5 character sheets
    |-- 02 - Sessions/                 # Session recaps (4-6)
    |-- 03 - Quests/                   # Active + completed quests
    |-- 04 - NPCs/                     # 20 NPC profiles
    |-- 05 - Loot Log/                 # Party loot tracking
    |-- 06 - World/                    # Locations, Factions, Lore
    |-- 07 - Reference/                # 5e SRD (Spells, Classes, Races, etc.)
    |-- 99 - Templates/                # Note templates
    |-- assets/                        # Images (world map, portraits, scenes)
```

## Core Workflows

### 1. Post-Session Character Update

```
Foundry VTT (Game Session)
        |
        v
Export actor JSON files
        |
        v
C:\Users\cfpor\Desktop\DndObsidian\
  fvtt-Actor-*.json
        |
        v
+-------------------+     +----------------+
| populate_sheets.py | --> | 01 - Party/*.md |
+-------------------+     +----------------+
        |                        |
        v                        v
  Parses: abilities,       Updated character
  skills, spells,          sheets with stats,
  features, inventory,     inventory, spells,
  HP, AC                   proficiencies
        |
        v
+----------------+     +---------------------+
| link_vault.py  | --> | All vault .md files  |
+----------------+     +---------------------+
        |
        v
  Auto-wikilinks entity names
  (spells, items, classes, etc.)
```

### 2. Session Recap Workflow

```
DM writes session recap
        |
        v
+---------------------------+
| 02 - Sessions/            |
| Session N Recap.md        |
+---------------------------+
        |
        +------+------+
        |      |      |
        v      v      v
  New NPCs  New      New
  created   Quests   Locations
  04-NPCs/  03-Q/    06-World/
        |      |      |
        +------+------+
               |
               v
      +----------------+
      | link_vault.py  |
      +----------------+
               |
               v
      All cross-references
      auto-wikilinked
```

### 3. Image Generation (MCP Server)

```
Claude Code (user request)
        |
        v
+-------------------+
| tenelis-imagegen   |
| MCP Server         |
+-------------------+
        |
        +--------+----------+-----------+
        |        |          |           |
        v        v          v           v
   NPC       Location    Party      Scene
   Portrait  Art         Portrait   Illustration
        |        |          |           |
        v        v          v           v
+----------------+  Reads vault files for context
| vault-reader   |  (character descriptions, locations)
+----------------+
        |
        v
+-----------------+  Crafts detailed image prompts
| gemini-director |  using Gemini AI
+-----------------+
        |
        v
+-------------------+  Generates images via
| imagen-generator  |  Google Imagen API
+-------------------+
        |
        v
+-----------------+  Saves to assets/ and
| vault-embedder  |  embeds in vault .md files
+-----------------+
        |
        v
  assets/npcs/        assets/locations/
  assets/scenes/      assets/references/
```

### 4. Reference Content Pipeline

```
+---------------------+     +-------------------+
| Source Data          |     | Generation Scripts|
+---------------------+     +-------------------+
| items_data.json     | --> | generate_items.py |
| spell_sources.json  | --> | add_spells.py     |
| xphb_spells.json    | --> | update_spells_*   |
| (hardcoded data)    | --> | update_feats_2024 |
|                     | --> | add_tce_scc_*.py  |
+---------------------+     +-------------------+
                                    |
                                    v
                          +--------------------+
                          | 07 - Reference/    |
                          | Spells/, Classes/, |
                          | Items/, Feats/,    |
                          | Races/, etc.       |
                          +--------------------+
                                    |
                                    v
                          +--------------------+
                          | generate_index_    |
                          | files.py           |
                          +--------------------+
                                    |
                                    v
                          Hub/index pages for
                          graph navigation
                                    |
                                    v
                          +----------------+
                          | link_vault.py  |
                          +----------------+
```

### 5. Vault Distribution

```
DM (this machine)
        |
        v
  git add -A
  git commit -m "..."
  git push origin master
        |
        v
+---------------------------+
| GitHub                    |
| testingcon10/dnd-stuff    |
| (master branch)           |
+---------------------------+
        |
        v
  Players run update-vault.bat
  (git fetch + git reset --hard origin/master)
        |
        v
  Players open vault in Obsidian
```

## Data Flow Summary

```
External Sources              Python Scripts              Obsidian Vault
================              ==============              ==============

Foundry VTT JSON  --------> populate_sheets.py -------> 01 - Party/
                                                              |
DM session notes  --(manual)-------------------------> 02 - Sessions/
                                                       03 - Quests/
                                                       04 - NPCs/
                                                       06 - World/
                                                              |
5e SRD data       --------> generate_*.py ------------> 07 - Reference/
(JSON files)                add_spells.py
                            update_*.py
                                                              |
                            link_vault.py <----(runs after all content changes)
                                                              |
                                                              v
Claude + MCP      --------> tenelis-imagegen ---------> assets/
(image requests)            (Gemini + Imagen)                 |
                                                              v
                                                     vault-embedder
                                                     (embeds in .md files)
```
