#!/usr/bin/env python3
"""
Generate index/hub .md files for the Tenelis Obsidian vault.

Creates a tree of wikilink-connected index files so the Obsidian graph
shows: Spells hub → school hubs → level hubs → individual spells,
and:   Feats hub → category hubs → individual feats.
"""

import os

VAULT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tenelis")
SPELLS_DIR = os.path.join(VAULT_ROOT, "07 - Reference", "Spells")
FEATS_DIR = os.path.join(VAULT_ROOT, "07 - Reference", "Feats")
BACKGROUNDS_DIR = os.path.join(VAULT_ROOT, "07 - Reference", "Backgrounds")
RULES_DIR = os.path.join(VAULT_ROOT, "07 - Reference", "Rules")


def write_index(filepath, content):
    """Write an index file, creating directories if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created: {os.path.relpath(filepath, VAULT_ROOT)}")


def get_spell_files(directory):
    """Return sorted list of .md filenames (sans extension) in a directory,
    excluding any file that matches the directory name (i.e. an existing index)."""
    dir_name = os.path.basename(directory)
    names = []
    for fname in sorted(os.listdir(directory)):
        if fname.endswith(".md"):
            name = fname[:-3]
            if name != dir_name:
                names.append(name)
    return names


def get_subdirs(directory):
    """Return sorted list of immediate subdirectory names."""
    return sorted(
        d for d in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, d))
    )


def level_sort_key(name):
    """Sort level folders: Cantrip first, then 1st..9th Level."""
    if name == "Cantrip":
        return (0, "")
    # Extract the number from "1st Level", "2nd Level", etc.
    parts = name.split()
    if parts:
        num_str = parts[0].rstrip("stndrdth")
        try:
            return (1, int(num_str))
        except ValueError:
            pass
    return (2, name)


def generate_spell_indexes():
    """Generate all spell index files."""
    if not os.path.isdir(SPELLS_DIR):
        print(f"Spells directory not found: {SPELLS_DIR}")
        return 0

    count = 0
    schools = get_subdirs(SPELLS_DIR)

    # 1. Top-level Spells hub
    links = " | ".join(f"[[{school}]]" for school in schools)
    content = f"# Spells\n\n{links}\n"
    write_index(os.path.join(SPELLS_DIR, "Spells.md"), content)
    count += 1

    # 2. School-level hubs
    for school in schools:
        school_dir = os.path.join(SPELLS_DIR, school)
        levels = get_subdirs(school_dir)
        # Sort levels naturally (Cantrip, 1st, 2nd, ...)
        levels.sort(key=level_sort_key)

        # Only include levels that actually have spell files
        levels_with_spells = [
            lv for lv in levels
            if get_spell_files(os.path.join(school_dir, lv))
        ]

        if not levels_with_spells:
            continue

        links = " | ".join(f"[[{lv}]]" for lv in levels_with_spells)
        content = f"# {school}\n\n{links}\n"
        write_index(os.path.join(school_dir, f"{school}.md"), content)
        count += 1

        # 3. Level-level hubs
        for lv in levels_with_spells:
            lv_dir = os.path.join(school_dir, lv)
            spells = get_spell_files(lv_dir)
            if not spells:
                continue

            links = " | ".join(f"[[{spell}]]" for spell in spells)
            content = f"# {school} — {lv}\n\n{links}\n"
            write_index(os.path.join(lv_dir, f"{lv}.md"), content)
            count += 1

    return count


def generate_feat_indexes():
    """Generate all feat index files."""
    if not os.path.isdir(FEATS_DIR):
        print(f"Feats directory not found: {FEATS_DIR}")
        return 0

    count = 0
    categories = get_subdirs(FEATS_DIR)

    # 1. Top-level Feats hub
    links = " | ".join(f"[[{cat}]]" for cat in categories)
    content = f"# Feats\n\n{links}\n"
    write_index(os.path.join(FEATS_DIR, "Feats.md"), content)
    count += 1

    # 2. Category-level hubs
    for cat in categories:
        cat_dir = os.path.join(FEATS_DIR, cat)
        feats = get_spell_files(cat_dir)  # reuse — just gets .md names
        if not feats:
            continue

        links = " | ".join(f"[[{feat}]]" for feat in feats)
        content = f"# {cat}\n\n{links}\n"
        write_index(os.path.join(cat_dir, f"{cat}.md"), content)
        count += 1

    return count


def generate_background_indexes():
    """Generate the Backgrounds hub index file."""
    if not os.path.isdir(BACKGROUNDS_DIR):
        print(f"Backgrounds directory not found: {BACKGROUNDS_DIR}")
        return 0

    backgrounds = get_spell_files(BACKGROUNDS_DIR)  # reuse — just gets .md names
    if not backgrounds:
        return 0

    links = " · ".join(f"[[{bg}]]" for bg in backgrounds)
    content = f"# Backgrounds\n\n{links}\n"
    write_index(os.path.join(BACKGROUNDS_DIR, "Backgrounds.md"), content)
    return 1


def generate_rules_indexes():
    """Generate the Rules hub index file."""
    if not os.path.isdir(RULES_DIR):
        print(f"Rules directory not found: {RULES_DIR}")
        return 0

    topics = get_spell_files(RULES_DIR)  # reuse — just gets .md names
    if not topics:
        return 0

    links = " · ".join(f"[[{topic}]]" for topic in topics)
    content = f"# Rules\n\n{links}\n"
    write_index(os.path.join(RULES_DIR, "Rules.md"), content)
    return 1


def main():
    print(f"Vault root: {VAULT_ROOT}")
    print()

    print("=== Generating Spell indexes ===")
    spell_count = generate_spell_indexes()
    print(f"  -> {spell_count} spell index files\n")

    print("=== Generating Feat indexes ===")
    feat_count = generate_feat_indexes()
    print(f"  -> {feat_count} feat index files\n")

    print("=== Generating Background indexes ===")
    bg_count = generate_background_indexes()
    print(f"  -> {bg_count} background index files\n")

    print("=== Generating Rules indexes ===")
    rules_count = generate_rules_indexes()
    print(f"  -> {rules_count} rules index files\n")

    total = spell_count + feat_count + bg_count + rules_count
    print(f"Done! Created {total} index files total.")


if __name__ == "__main__":
    main()
