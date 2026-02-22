#!/usr/bin/env python3
"""
Cross-link all entity references across the Tenelis Obsidian vault.

Scans every .md file and replaces plain-text entity names with [[wikilinks]].
Entities are collected from: Spells, Classes (with subclasses), Races, Conditions, Feats, Items.
"""

import os
import re
import uuid

# ── Configuration ──────────────────────────────────────────────────────────────

VAULT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tenelis")

ENTITY_DIRS = [
    "07 - Reference/Conditions",
    "07 - Reference/Backgrounds",
    "07 - Reference/Rules",
]

# Directories that contain nested subdirectories of .md entity files
RECURSIVE_ENTITY_DIRS = [
    "07 - Reference/Classes",
    "07 - Reference/Feats",
    "07 - Reference/Items",
    "07 - Reference/Spells",
    "07 - Reference/Races",
]

# Slash-variant aliases: filename uses hyphen, but text may use slash
SLASH_ALIASES = {
    "Blindness-Deafness": "Blindness/Deafness",
    "Enlarge-Reduce": "Enlarge/Reduce",
    "Antipathy-Sympathy": "Antipathy/Sympathy",
}

# Single-word entity names that are too ambiguous in D&D text.
# These commonly appear as generic game terms, not references to the
# specific spell/feat/item they share a name with.
SKIP_ENTITIES = {
    "Resistance",    # cantrip — "fire resistance", "damage resistance" everywhere
    "Darkvision",    # spell — every race file says "Darkvision: 60 ft."
    "Friends",       # cantrip — common English word
    "Symbol",        # spell — "holy symbol" is standard D&D terminology
    "Healer",        # feat — appears inside feature names like "Blessed Healer"
    "Hunter",        # subclass — "bounty hunter", "hunter's mark" (possessive)
    "Guidance",      # cantrip — common English word in D&D context
    "Message",       # cantrip — common English word
    "Wish",          # spell — common English word
    "Knock",         # spell — common English word
    "Mending",       # cantrip — common English word
    "Sending",       # spell — common English word
    "Commune",       # spell — common English word
    "Creation",      # spell — common English word
    "Dream",         # spell — common English word
    "Gust",          # cantrip — common English word
    "Gate",          # spell — common English word
    "Alarm",         # spell — common English word
    "Light",         # cantrip — "Light crossbows", "Light armor", "bright light"
    "Befuddlement",  # spell — common English word for confusion
    # Fighting Style feat names that appear as generic terms in class descriptions:
    "Archery",       # feat — appears in fighting style class feature descriptions
    "Defense",       # feat — common English word, appears in class descriptions
    "Dueling",       # feat — common English word, appears in class descriptions
    "Protection",    # feat — common English word, "Protection from..." spells
    # Mundane weapon/armor names that cause false-positive wikilinks:
    "Shield",        # item — "shield" appears in many item/spell descriptions
    "Club",          # item — common English word
    "Mace",          # item — appears in magic mace descriptions generically
    "Lance",         # item — common English word, appears in descriptions
    "Pike",          # item — common English word
    "Plate",         # item — "plate armor", "plate mail" in many descriptions
    "Net",           # item — common English word
    "Sling",         # item — common English word
    "Dart",          # item — common English word
    "Maul",          # item — common English word
    "Whip",          # item — common English word
    "Flail",         # item — common English word
    "Hide",          # item — "hide armor", "hide" is common English word
    "Chain",         # item — "chain mail", "chain shirt" in descriptions
    # Index hub file names that would cause false-positive wikilinks:
    "Spells",        # hub — generic term used throughout the vault
    "Cantrip",       # hub — "cantrip" appears in class/spell descriptions
    "Origin",        # hub — "Origin" appears in feat/race descriptions
    "General",       # hub — common English word
    "Epic Boon",     # hub — appears in class capstone descriptions
    "Fighting Style", # hub — appears in class feature descriptions
    # Background names that are common words:
    "Merchant",      # background — common English word
    "Noble",         # background — common English word
    "Guard",         # background — common English word
    "Hermit",        # background — common English word
    "Soldier",       # background — common English word
    "Sage",          # background — common English word
    "Sailor",        # background — common English word
    "Farmer",        # background — common English word
    "Guide",         # background — common English word
    "Scribe",        # background — common English word
    "Entertainer",   # background — common English word
    # Rule/hub names that are common words:
    "Skills",        # rule — generic term used throughout the vault
    "Cover",         # rule — common English word
    "Rules",         # hub — generic term
    "Backgrounds",   # hub — generic term
    "Languages",     # rule — common English word
    "Tools",         # rule — common English word
    "Glossary",      # reference — generic term
}

# ── Step 1: Build Entity Dictionary ───────────────────────────────────────────


def build_entity_dict():
    """Collect every entity name (filename sans .md) from reference directories."""
    entities = {}  # display_name -> canonical_name (filename without .md)

    # Flat directories
    for rel_dir in ENTITY_DIRS:
        full_dir = os.path.join(VAULT_ROOT, rel_dir)
        if not os.path.isdir(full_dir):
            continue
        for fname in os.listdir(full_dir):
            if fname.endswith(".md"):
                name = fname[:-3]
                if name not in SKIP_ENTITIES:
                    entities[name] = name

    # Recursive directories (Items has categorized subfolders)
    for rel_dir in RECURSIVE_ENTITY_DIRS:
        full_dir = os.path.join(VAULT_ROOT, rel_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _dirs, files in os.walk(full_dir):
            for fname in files:
                if fname.endswith(".md"):
                    name = fname[:-3]
                    if name not in SKIP_ENTITIES:
                        entities[name] = name

    # Add slash-variant aliases
    for canonical, alias in SLASH_ALIASES.items():
        if canonical in entities:
            entities[alias] = canonical  # alias -> links to canonical name

    return entities


# ── Step 2: Sort longest-first ────────────────────────────────────────────────


def sorted_entities(entities):
    """Return list of (display_name, canonical_name) sorted by display_name length desc."""
    return sorted(entities.items(), key=lambda x: len(x[0]), reverse=True)


# ── Step 3: Process files ────────────────────────────────────────────────────


def split_frontmatter(text):
    """Split YAML frontmatter from body. Returns (frontmatter, body).
    frontmatter includes the --- delimiters. If no frontmatter, returns ('', text)."""
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    # Find the actual end: after the closing ---
    closing = end + len("\n---")
    # Include trailing newline if present
    if closing < len(text) and text[closing] == "\n":
        closing += 1
    return text[:closing], text[closing:]


def preprocess_italic_spell_tables(body, spell_names_lower):
    """Convert italic spell names in subclass spell tables to wikilinks.

    Handles two formats:
      | 1st | *bless, cure wounds* |       (single italic block)
      | 1st | *burning hands*, *command* | (individual italics)
    """
    lines = body.split("\n")
    new_lines = []
    for line in lines:
        if re.match(r"\|\s*\d+(?:st|nd|rd|th)\s*\|", line) and "*" in line:
            parts = line.split("|")
            # parts: ['', ' 1st ', ' *spell1, spell2* ', '']
            if len(parts) >= 4:
                spell_cell = parts[2].strip()
                if "*" in spell_cell:
                    # Try multi-spell italic block first: *spell1, spell2*
                    processed = re.sub(
                        r"\*([^*]+,[^*]+)\*",
                        lambda m: expand_italic_spells(m.group(1), spell_names_lower),
                        spell_cell,
                    )
                    # If no multi-spell block found, try individual *spell* entries
                    if processed == spell_cell:
                        processed = re.sub(
                            r"\*([^*]+)\*",
                            lambda m: expand_single_italic_spell(m.group(1), spell_names_lower),
                            spell_cell,
                        )
                    parts[2] = f" {processed} "
                    line = "|".join(parts)
        new_lines.append(line)
    return "\n".join(new_lines)


def expand_italic_spells(inner, spell_names_lower):
    """Expand a comma-separated italic block like 'bless, cure wounds' to [[links]]."""
    parts = [p.strip() for p in inner.split(",")]
    linked = []
    for part in parts:
        part_lower = part.lower().strip()
        if part_lower in spell_names_lower:
            canonical = spell_names_lower[part_lower]
            linked.append(f"[[{canonical}]]")
        else:
            linked.append(part)
    return ", ".join(linked)


def expand_single_italic_spell(spell, spell_names_lower):
    """Expand a single italic spell like 'burning hands' to a [[link]]."""
    spell_lower = spell.lower().strip()
    if spell_lower in spell_names_lower:
        canonical = spell_names_lower[spell_lower]
        return f"[[{canonical}]]"
    return f"*{spell}*"


def protect_regions(body):
    """Replace regions that must not be modified with unique placeholders.
    Returns (modified_body, restore_map)."""
    placeholders = {}

    def make_placeholder(content):
        ph = f"\x00PH{uuid.uuid4().hex}\x00"
        placeholders[ph] = content
        return ph

    # 1. Code blocks (```...```)
    body = re.sub(
        r"```[\s\S]*?```",
        lambda m: make_placeholder(m.group(0)),
        body,
    )

    # 2. Inline code (`...`)
    body = re.sub(
        r"`[^`]+`",
        lambda m: make_placeholder(m.group(0)),
        body,
    )

    # 3. DM comment blocks (%% ... %%)
    body = re.sub(
        r"%%[\s\S]*?%%",
        lambda m: make_placeholder(m.group(0)),
        body,
    )

    # 4. Existing wikilinks [[...]]
    body = re.sub(
        r"\[\[[^\]]+\]\]",
        lambda m: make_placeholder(m.group(0)),
        body,
    )

    # 5. Markdown links [text](url)
    body = re.sub(
        r"\[([^\]]*)\]\([^)]+\)",
        lambda m: make_placeholder(m.group(0)),
        body,
    )

    # 6. Lines containing 5e.tools
    body = re.sub(
        r"^.*5e\.tools.*$",
        lambda m: make_placeholder(m.group(0)),
        body,
        flags=re.MULTILINE,
    )

    # 7. Bold text (**...**) — feature names, headings in bold
    body = re.sub(
        r"\*\*[^*]+\*\*",
        lambda m: make_placeholder(m.group(0)),
        body,
    )

    return body, placeholders


def restore_regions(body, placeholders):
    """Restore all placeholders with their original content.
    Reversed order ensures nested placeholders (e.g. wikilink inside bold)
    are restored correctly — outer placeholders first, then inner ones."""
    for ph, original in reversed(list(placeholders.items())):
        body = body.replace(ph, original)
    return body


def linkify_body(body, sorted_ents, self_name):
    """Replace entity names with [[wikilinks]] in the body text.

    Uses placeholders for newly created wikilinks to prevent nested linking
    (e.g., "School of Divination" won't have "Divination" re-matched inside it).
    """
    # Shared placeholder map for newly created wikilinks
    new_placeholders = {}

    def make_link_placeholder(link_text):
        ph = f"\x00LK{uuid.uuid4().hex}\x00"
        new_placeholders[ph] = link_text
        return ph

    for display_name, canonical_name in sorted_ents:
        # Skip self-references
        if canonical_name == self_name or display_name == self_name:
            continue

        # Case rules: all single-word entities are case-sensitive,
        # multi-word entities are case-insensitive
        words = display_name.split()
        is_single_word = len(words) == 1
        flags = 0 if is_single_word else re.IGNORECASE

        # Escape the display name for regex
        escaped = re.escape(display_name)

        # Build pattern with word boundaries
        pattern = rf"\b{escaped}\b"

        def make_replacement(match, canon=canonical_name):
            matched_text = match.group(0)
            if matched_text == canon:
                link = f"[[{canon}]]"
            else:
                link = f"[[{canon}|{matched_text}]]"
            # Replace with placeholder to prevent nested matches
            return make_link_placeholder(link)

        body = re.sub(pattern, make_replacement, body, flags=flags)

    # Restore all new link placeholders
    for ph, link_text in new_placeholders.items():
        body = body.replace(ph, link_text)

    return body


def process_file(filepath, sorted_ents, spell_names_lower):
    """Process a single markdown file: add wikilinks for entity references."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter from body
    frontmatter, body = split_frontmatter(content)

    # Get the file's own name (for self-reference skipping)
    self_name = os.path.splitext(os.path.basename(filepath))[0]

    # Step 3b: Preprocess italic spell tables
    body = preprocess_italic_spell_tables(body, spell_names_lower)

    # Step 3c: Protect the title heading (# Title) from being linked
    title_placeholder = None
    title_match = re.match(r"(#\s+.+?)(\n|$)", body)
    if title_match:
        ph = f"\x00TITLE{uuid.uuid4().hex}\x00"
        title_placeholder = (ph, title_match.group(0))
        body = body.replace(title_match.group(0), ph, 1)

    # Protect other regions
    body, placeholders = protect_regions(body)

    # Step 3d: Replace entity names with wikilinks
    body = linkify_body(body, sorted_ents, self_name)

    # Step 3e: Restore protected regions
    body = restore_regions(body, placeholders)
    if title_placeholder:
        body = body.replace(title_placeholder[0], title_placeholder[1])

    new_content = frontmatter + body

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def collect_all_md_files(vault_root):
    """Collect all .md files in the vault, skipping .obsidian/."""
    md_files = []
    for root, dirs, files in os.walk(vault_root):
        # Skip .obsidian directory
        dirs[:] = [d for d in dirs if d != ".obsidian"]
        for fname in files:
            if fname.endswith(".md"):
                md_files.append(os.path.join(root, fname))
    return md_files


def main():
    print(f"Vault root: {VAULT_ROOT}")
    print()

    # Step 1: Build entity dictionary
    entities = build_entity_dict()
    print(f"Collected {len(entities)} entity names")
    print(f"Skipped {len(SKIP_ENTITIES)} ambiguous entity names: {', '.join(sorted(SKIP_ENTITIES))}")

    # Build lowercase spell lookup for italic table preprocessing
    spell_dir = os.path.join(VAULT_ROOT, "07 - Reference/Spells")
    spell_names_lower = {}
    if os.path.isdir(spell_dir):
        for root, _dirs, files in os.walk(spell_dir):
            for fname in files:
                if fname.endswith(".md"):
                    canonical = fname[:-3]
                    spell_names_lower[canonical.lower()] = canonical
        # Also add slash aliases for spells
        for canonical, alias in SLASH_ALIASES.items():
            if canonical.lower() in spell_names_lower:
                spell_names_lower[alias.lower()] = spell_names_lower[canonical.lower()]

    print(f"Spell lookup table: {len(spell_names_lower)} entries")

    # Step 2: Sort longest-first
    sorted_ents = sorted_entities(entities)
    print(f"Sorted {len(sorted_ents)} entities (longest first)")
    print(f"  Longest: '{sorted_ents[0][0]}' ({len(sorted_ents[0][0])} chars)")
    print(f"  Shortest: '{sorted_ents[-1][0]}' ({len(sorted_ents[-1][0])} chars)")
    print()

    # Step 3: Process all files
    md_files = collect_all_md_files(VAULT_ROOT)
    print(f"Found {len(md_files)} markdown files to process")
    print()

    modified_count = 0
    for filepath in md_files:
        rel_path = os.path.relpath(filepath, VAULT_ROOT)
        changed = process_file(filepath, sorted_ents, spell_names_lower)
        if changed:
            modified_count += 1
            print(f"  Modified: {rel_path}")

    print()
    print(f"Done! Modified {modified_count} of {len(md_files)} files.")


if __name__ == "__main__":
    main()
