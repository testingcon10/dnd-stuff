# Tenelis - D&D 5e Campaign Vault

## What This Is

An Obsidian vault for a D&D 5e campaign called Tenelis. Contains character sheets, session recaps, quests, NPCs, loot logs, world lore, and a full 5e reference library (spells, classes, races, feats, items, conditions). Python scripts automate character sheet population and cross-linking.

## Vault Structure

The vault lives in `Tenelis/Tenelis/` (the inner directory is the Obsidian vault root).

| Folder | Contents |
|--------|----------|
| `00 - Home.md` | Campaign home page |
| `00 - Player Setup Guide.md` | Onboarding guide for players |
| `01 - Party/` | Character sheets (one per PC) |
| `02 - Sessions/` | Session recap notes |
| `03 - Quests/` | Quest tracking |
| `04 - NPCs/` | NPC profiles |
| `05 - Loot Log/` | Party loot tracking |
| `06 - World/` | World lore, locations, factions |
| `07 - Reference/` | 5e rules reference (Spells, Classes, Races, Feats, Items, Conditions, Backgrounds, Gods, Skills, Rules) |
| `99 - Templates/` | Obsidian templates for new notes |
| `assets/` | Images and media |

## Party Roster

| Character | Player | File |
|-----------|--------|------|
| Netanyahu D. Kirkuenly | Conor | `01 - Party/Netanyahu D. Kirkuenly.md` |
| Booker Locke | Tony | `01 - Party/Booker Locke.md` |
| Old Shell | Erik | `01 - Party/Old Shell.md` |
| Cassius Bellona | Jake | `01 - Party/Cassius Bellona.md` |
| Ryan-Nigamus | Nigamus | `01 - Party/Ryan-Nigamus.md` |

## Key Scripts

Scripts live in the project root (one level above the vault).

### Run Order Matters

1. **`populate_sheets.py`** -- Run FIRST. Reads Foundry VTT JSON exports from `C:\Users\cfpor\Desktop\DndObsidian\` and generates/updates character sheets in `01 - Party/`. Parses abilities, skills, spells, features, inventory, and HP from the Foundry actor JSON.

2. **`link_vault.py`** -- Run AFTER content changes. Scans all `.md` files and replaces plain-text entity names with `[[wikilinks]]`. Entities are collected from: Spells, Classes (with subclasses), Races, Conditions, Feats, Items, Backgrounds, Gods, Skills, Rules.

### Other Scripts

| Script | Purpose |
|--------|---------|
| `generate_items.py` | Generates item reference pages from `items_data.json` |
| `generate_reference_content.py` | Generates reference content pages |
| `generate_index_files.py` | Generates index/listing pages for reference sections |
| `add_spells.py` | Adds spell reference pages |
| `update_spells_2024.py` | Updates spells with 2024 revision data |
| `update_spells_xphb.py` | Updates spells from XPHB data (`xphb_spells.json`) |
| `update_feats_2024.py` | Updates feats with 2024 revision data |
| `add_tce_scc_content.py` | Adds Tasha's Cauldron / Strixhaven content |
| `reorganize_vault.py` | Reorganizes vault structure per `reorganize_manifest.json` |

## Important: link_vault.py SKIP_ENTITIES

`link_vault.py` has a `SKIP_ENTITIES` set of entity names that are excluded from auto-linking to prevent false positive wikilinks. Examples: "Resistance", "Darkvision", "Light", "Shield", "Friends", "Net", "Guidance". If a new entity creates false positives, add it to `SKIP_ENTITIES` in `link_vault.py`.

## Foundry VTT JSON Source

Character export JSONs come from: `C:\Users\cfpor\Desktop\DndObsidian\`

Filenames follow the pattern: `fvtt-Actor-<character-name>-<player>-<id>.json`

## Git Workflow

```
git add -A
git commit -m "description"
git push origin master
```

Remote: `https://github.com/testingcon10/dnd-stuff.git` (master branch)

## Common Tasks

**Updating character sheets after a session:** Get updated Foundry VTT exports into `C:\Users\cfpor\Desktop\DndObsidian\`, then run `python populate_sheets.py`.

**Adding a new NPC:** Create a new `.md` file in `Tenelis/04 - NPCs/`. Then run `link_vault.py` to auto-link any references across the vault.

**Adding a quest:** Create in `Tenelis/03 - Quests/`. Run `link_vault.py` after.

**Updating session recaps:** Add to `Tenelis/02 - Sessions/`. Follow existing naming: `Session N Recap.md`.

**Adding new reference content:** Add files to appropriate subdirectory under `Tenelis/07 - Reference/`. Run `link_vault.py` to cross-link.

**Fixing graph JSON or broken links:** Usually caused by `link_vault.py` creating a bad wikilink. Check `SKIP_ENTITIES` if a common word is being incorrectly linked.
