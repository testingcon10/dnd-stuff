#!/usr/bin/env python3
"""
Reorganize Spells and Races in the Tenelis Obsidian vault.

Spells  -> Spells/{School}/{Level}/
Races   -> Subraces into Races/{parent_race}/, base races with subraces too.
Also deletes stray Tenelis/Chain Shirt.md.

Usage:
    python reorganize_vault.py            # dry run (default)
    python reorganize_vault.py --dry-run  # explicit dry run
    python reorganize_vault.py --execute  # actually move files
"""

import argparse
import json
import os
import re
import shutil

VAULT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tenelis")
SPELLS_DIR = os.path.join(VAULT_ROOT, "07 - Reference", "Spells")
RACES_DIR = os.path.join(VAULT_ROOT, "07 - Reference", "Races")
STRAY_FILE = os.path.join(VAULT_ROOT, "Chain Shirt.md")

LEVEL_NAMES = {
    0: "Cantrip",
    1: "1st Level",
    2: "2nd Level",
    3: "3rd Level",
    4: "4th Level",
    5: "5th Level",
    6: "6th Level",
    7: "7th Level",
    8: "8th Level",
    9: "9th Level",
}


def parse_frontmatter(filepath):
    """Extract YAML frontmatter as a dict of key: value (simple parser)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    fm_block = content[4:end]  # skip opening ---\n
    result = {}
    for line in fm_block.split("\n"):
        m = re.match(r'^(\w+):\s*(.+)$', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            # Try to parse as int
            try:
                val = int(val)
            except (ValueError, TypeError):
                pass
            result[key] = val
    return result


def plan_spell_moves():
    """Plan moves for all spell files into School/Level subfolders."""
    moves = []
    if not os.path.isdir(SPELLS_DIR):
        return moves
    for fname in os.listdir(SPELLS_DIR):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(SPELLS_DIR, fname)
        if not os.path.isfile(filepath):
            continue
        fm = parse_frontmatter(filepath)
        school = fm.get("school")
        level = fm.get("spell_level")
        if school is None or level is None:
            print(f"  WARNING: Missing school/spell_level in {fname}, skipping")
            continue
        level_name = LEVEL_NAMES.get(level)
        if level_name is None:
            print(f"  WARNING: Unknown spell_level {level} in {fname}, skipping")
            continue
        dest_dir = os.path.join(SPELLS_DIR, school, level_name)
        dest_path = os.path.join(dest_dir, fname)
        if filepath != dest_path:
            moves.append((filepath, dest_path))
    return moves


def plan_race_moves():
    """Plan moves for race files with parent_race into parent subfolders."""
    moves = []
    if not os.path.isdir(RACES_DIR):
        return moves

    # First pass: find all parent_race values
    parent_races = set()
    for fname in os.listdir(RACES_DIR):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(RACES_DIR, fname)
        if not os.path.isfile(filepath):
            continue
        fm = parse_frontmatter(filepath)
        pr = fm.get("parent_race")
        if pr:
            parent_races.add(pr)

    # Second pass: move subraces and their base race files
    for fname in os.listdir(RACES_DIR):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(RACES_DIR, fname)
        if not os.path.isfile(filepath):
            continue
        fm = parse_frontmatter(filepath)
        pr = fm.get("parent_race")
        name = fname[:-3]

        if pr:
            # This is a subrace -> move into Races/{parent_race}/
            dest_dir = os.path.join(RACES_DIR, pr)
            dest_path = os.path.join(dest_dir, fname)
            moves.append((filepath, dest_path))
        elif name in parent_races:
            # This is a base race that has subraces -> move into its own subfolder
            dest_dir = os.path.join(RACES_DIR, name)
            dest_path = os.path.join(dest_dir, fname)
            moves.append((filepath, dest_path))

    return moves


def execute_moves(moves, dry_run=True):
    """Execute (or preview) file moves."""
    dirs_created = set()
    for src, dst in moves:
        dst_dir = os.path.dirname(dst)
        if dst_dir not in dirs_created and not os.path.isdir(dst_dir):
            if dry_run:
                print(f"  MKDIR  {os.path.relpath(dst_dir, VAULT_ROOT)}")
            else:
                os.makedirs(dst_dir, exist_ok=True)
            dirs_created.add(dst_dir)
        rel_src = os.path.relpath(src, VAULT_ROOT)
        rel_dst = os.path.relpath(dst, VAULT_ROOT)
        if dry_run:
            print(f"  MOVE   {rel_src}  ->  {rel_dst}")
        else:
            shutil.move(src, dst)
            print(f"  MOVED  {rel_src}  ->  {rel_dst}")


def main():
    parser = argparse.ArgumentParser(description="Reorganize Tenelis vault Spells and Races")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", default=True,
                       help="Preview changes without moving files (default)")
    group.add_argument("--execute", action="store_true",
                       help="Actually move files")
    args = parser.parse_args()

    dry_run = not args.execute
    mode = "DRY RUN" if dry_run else "EXECUTE"
    print(f"=== Reorganize Vault ({mode}) ===\n")

    manifest = {"mode": mode, "spells": [], "races": [], "deleted": []}

    # --- Spells ---
    print("Planning spell moves...")
    spell_moves = plan_spell_moves()
    print(f"  {len(spell_moves)} spells to move\n")
    if spell_moves:
        print("Spell moves:")
        execute_moves(spell_moves, dry_run)
        for src, dst in spell_moves:
            manifest["spells"].append({
                "from": os.path.relpath(src, VAULT_ROOT),
                "to": os.path.relpath(dst, VAULT_ROOT),
            })
    print()

    # --- Races ---
    print("Planning race moves...")
    race_moves = plan_race_moves()
    print(f"  {len(race_moves)} races to move\n")
    if race_moves:
        print("Race moves:")
        execute_moves(race_moves, dry_run)
        for src, dst in race_moves:
            manifest["races"].append({
                "from": os.path.relpath(src, VAULT_ROOT),
                "to": os.path.relpath(dst, VAULT_ROOT),
            })
    print()

    # --- Stray file ---
    if os.path.isfile(STRAY_FILE):
        rel = os.path.relpath(STRAY_FILE, VAULT_ROOT)
        if dry_run:
            print(f"DELETE   {rel}")
        else:
            os.remove(STRAY_FILE)
            print(f"DELETED  {rel}")
        manifest["deleted"].append(rel)
    else:
        print("Stray file Chain Shirt.md not found (already removed or missing)")
    print()

    # --- Write manifest ---
    manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reorganize_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written to {manifest_path}")
    print(f"\nTotal: {len(spell_moves)} spell moves, {len(race_moves)} race moves, {len(manifest['deleted'])} deletions")


if __name__ == "__main__":
    main()
