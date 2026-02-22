#!/usr/bin/env python3
"""
Generate item .md files for the Tenelis Obsidian vault.

Reads item data from items_data.json and renders each item as a markdown
file using the vault's standard item template format.

Usage:
    python generate_items.py           # Generate all missing .md files
    python generate_items.py --dry-run # Validate data and show what would be created
"""

import json
import os
import re
import sys
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ITEMS_ROOT = os.path.join(SCRIPT_DIR, "Tenelis", "07 - Reference", "Items")
DATA_FILE = os.path.join(SCRIPT_DIR, "items_data.json")

SOURCE_URL_SLUGS = {
    "DMG": "dmg",
    "PHB": "phb",
    "XGtE": "xgte",
    "TCoE": "tce",
}

VALID_RARITIES = {
    "Mundane", "Common", "Uncommon", "Rare", "Very Rare", "Legendary", "Artifact",
}


def make_url_slug(item):
    """Generate the 5e.tools URL slug for an item."""
    name = item.get("url_name", item["title"]).lower()
    source_slug = SOURCE_URL_SLUGS.get(item["source"], item["source"].lower())
    encoded = urllib.parse.quote(name, safe="")
    # Convert percent-encoding to lowercase to match 5e.tools convention
    encoded = re.sub(r"%[0-9A-Fa-f]{2}", lambda m: m.group(0).lower(), encoded)
    return f"{encoded}_{source_slug}"


def render_item(item):
    """Render an item dict to markdown content."""
    att = item["attunement"]
    if isinstance(att, str):
        att_yaml = "true"
        att_display = f"Yes ({att})"
    elif att:
        att_yaml = "true"
        att_display = "Yes"
    else:
        att_yaml = "false"
        att_display = "No"

    url_slug = make_url_slug(item)

    lines = [
        "---",
        "tags: [item, reference]",
        f'item_type: "{item["item_type"]}"',
        f'rarity: "{item["rarity"]}"',
        f"attunement: {att_yaml}",
        f'source: "{item["source"]}"',
        "---",
        f"# {item['title']}",
        "",
        item["description"],
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| **Type** | {item['item_type']} |",
        f"| **Rarity** | {item['rarity']} |",
        f"| **Attunement** | {att_display} |",
        "",
        "---",
        f"\U0001f517 [Full Details on 5e.tools](https://5e.tools/items.html#{url_slug})",
    ]
    return "\n".join(lines) + "\n"


def validate_items(items):
    """Validate all items for required fields and consistency."""
    errors = []
    seen = {}
    required_fields = [
        "title", "filename", "folder", "item_type",
        "rarity", "attunement", "source", "description",
    ]

    for i, item in enumerate(items):
        prefix = f"Item #{i} ({item.get('title', '???')})"

        for field in required_fields:
            if field not in item:
                errors.append(f"{prefix}: missing required field '{field}'")

        if item.get("rarity") and item["rarity"] not in VALID_RARITIES:
            errors.append(f"{prefix}: invalid rarity '{item['rarity']}'")

        if item.get("source") and item["source"] not in SOURCE_URL_SLUGS:
            errors.append(f"{prefix}: unknown source '{item['source']}'")

        key = (item.get("folder", ""), item.get("filename", ""))
        if key in seen:
            errors.append(
                f"{prefix}: duplicate path {key[0]}/{key[1]}.md (first: {seen[key]})"
            )
        else:
            seen[key] = item.get("title", "???")

    return errors


def main():
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found")
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} items from {os.path.basename(DATA_FILE)}")

    errors = validate_items(items)
    if errors:
        print(f"\nValidation errors ({len(errors)}):")
        for err in errors:
            print(f"  \u2717 {err}")
        if not dry_run:
            print("\nAborting due to validation errors.")
            return 1

    created = 0
    skipped = 0

    for item in items:
        folder = os.path.join(ITEMS_ROOT, item["folder"])
        filepath = os.path.join(folder, item["filename"] + ".md")

        if os.path.exists(filepath):
            skipped += 1
            continue

        if dry_run:
            rel = os.path.relpath(filepath, ITEMS_ROOT)
            print(f"  + {rel}")
        else:
            os.makedirs(folder, exist_ok=True)
            content = render_item(item)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

        created += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  {'Would create' if dry_run else 'Created'}: {created}")
    print(f"  Skipped (exist): {skipped}")
    print(f"  Total in data: {len(items)}")
    if errors:
        print(f"  Validation errors: {len(errors)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
