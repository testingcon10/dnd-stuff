#!/usr/bin/env python3
"""Update all 2024-sourced spell files with XPHB data from 5e.tools."""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.join(SCRIPT_DIR, "Tenelis")
SPELL_DIR = os.path.join(VAULT_ROOT, "07 - Reference", "Spells")
XPHB_JSON = os.path.join(SCRIPT_DIR, "xphb_spells.json")
SOURCES_JSON = os.path.join(SCRIPT_DIR, "spell_sources.json")

SCHOOL_MAP = {
    "A": "Abjuration", "C": "Conjuration", "D": "Divination",
    "E": "Enchantment", "V": "Evocation", "I": "Illusion",
    "N": "Necromancy", "T": "Transmutation",
}

LEVEL_NAMES = {
    0: "Cantrip", 1: "1st Level", 2: "2nd Level", 3: "3rd Level",
    4: "4th Level", 5: "5th Level", 6: "6th Level",
    7: "7th Level", 8: "8th Level", 9: "9th Level",
}


# ── 5e.tools tag stripping ───────────────────────────────────────────────────

def strip_tags(text):
    """Strip 5e.tools {@tag content|source|display} tags to plain text."""
    def replace_tag(m):
        tag_type = m.group(1)
        content = m.group(2)

        # Some tags have display text after pipes: {@tag name|source|display}
        parts = content.split("|")

        # Tags where the display text (last part) should be preferred
        if tag_type in ("variantrule", "condition", "status", "hazard",
                        "creature", "item", "spell", "sense", "skill",
                        "action", "classFeature", "race", "feat",
                        "optfeature", "quickref"):
            # Use display text if present (3rd part), else first part
            if len(parts) >= 3 and parts[2]:
                return parts[2]
            return parts[0]

        # Damage/dice: {@damage 1d4 + 1} → "1d4 + 1"
        if tag_type in ("damage", "dice", "hit", "d20", "recharge"):
            return parts[0]

        # Scaled damage: {@scaledamage 8d6|3-9|1d6} → "1d6"
        if tag_type == "scaledamage":
            return parts[-1] if len(parts) >= 3 else parts[0]

        # Chance: {@chance 50} → "50 percent"
        if tag_type == "chance":
            return f"{parts[0]} percent"

        # Filter: {@filter display text|...} → display text
        if tag_type == "filter":
            return parts[0]

        # Default: use first part
        return parts[0]

    # Match {@tagname content}
    result = re.sub(r"\{@(\w+)\s+([^}]+)\}", replace_tag, text)
    return result


def format_entries(entries, depth=0):
    """Convert 5e.tools entries array to markdown text."""
    lines = []
    for entry in entries:
        if isinstance(entry, str):
            lines.append(strip_tags(entry))
        elif isinstance(entry, dict):
            etype = entry.get("type", "")
            if etype == "entries":
                name = entry.get("name", "")
                sub_entries = entry.get("entries", [])
                if name:
                    lines.append(f"\n**{name}.** {format_entries(sub_entries)}")
                else:
                    lines.append(format_entries(sub_entries))
            elif etype == "list":
                items = entry.get("items", [])
                for item in items:
                    if isinstance(item, str):
                        lines.append(f"- {strip_tags(item)}")
                    elif isinstance(item, dict):
                        name = item.get("name", "")
                        item_entries = item.get("entries", [])
                        if name:
                            lines.append(f"- **{name}.** {format_entries(item_entries)}")
                        else:
                            entry_text = item.get("entry", "")
                            if entry_text:
                                lines.append(f"- {strip_tags(entry_text)}")
                            else:
                                lines.append(f"- {format_entries(item_entries)}")
            elif etype == "table":
                caption = entry.get("caption", "")
                col_labels = entry.get("colLabels", [])
                rows = entry.get("rows", [])
                if caption:
                    lines.append(f"\n**{caption}**\n")
                if col_labels:
                    header = "| " + " | ".join(strip_tags(c) for c in col_labels) + " |"
                    sep = "| " + " | ".join("---" for _ in col_labels) + " |"
                    lines.append(header)
                    lines.append(sep)
                for row in rows:
                    cells = []
                    for cell in row:
                        if isinstance(cell, str):
                            cells.append(strip_tags(cell))
                        elif isinstance(cell, dict):
                            cells.append(strip_tags(cell.get("entry", str(cell))))
                        else:
                            cells.append(str(cell))
                    lines.append("| " + " | ".join(cells) + " |")
            elif etype == "quote":
                quote_entries = entry.get("entries", [])
                by = entry.get("by", "")
                for qe in quote_entries:
                    lines.append(f"> {strip_tags(qe) if isinstance(qe, str) else format_entries([qe])}")
                if by:
                    lines.append(f"> — {by}")
            elif etype == "inset":
                inset_entries = entry.get("entries", [])
                name = entry.get("name", "")
                if name:
                    lines.append(f"\n> **{name}**")
                for ie in inset_entries:
                    lines.append(f"> {strip_tags(ie) if isinstance(ie, str) else format_entries([ie])}")
            else:
                # Fallback for unknown types
                sub_entries = entry.get("entries", [])
                if sub_entries:
                    lines.append(format_entries(sub_entries))
    return "\n".join(lines)


def format_time(time_data):
    """Format casting time from 5e.tools data."""
    if not time_data:
        return "1 action"
    t = time_data[0]
    number = t.get("number", 1)
    unit = t.get("unit", "action")
    condition = t.get("condition", "")

    if unit == "bonus":
        unit = "bonus action"
    elif unit == "reaction":
        cond_text = f" ({condition})" if condition else ""
        return f"1 reaction{cond_text}"

    if number == 1:
        return f"1 {unit}"
    return f"{number} {unit}s"


def format_range(range_data):
    """Format range from 5e.tools data."""
    if not range_data:
        return "Self"
    rtype = range_data.get("type", "")
    if rtype == "special":
        return "Special"
    dist = range_data.get("distance", {})
    dist_type = dist.get("type", "")
    amount = dist.get("amount", 0)

    if dist_type == "self":
        return "Self"
    elif dist_type == "touch":
        return "Touch"
    elif dist_type == "sight":
        return "Sight"
    elif dist_type == "unlimited":
        return "Unlimited"
    elif dist_type in ("feet", "ft"):
        return f"{amount} feet"
    elif dist_type in ("miles", "mi"):
        return f"{amount} mile{'s' if amount != 1 else ''}"
    return f"{amount} {dist_type}"


def format_components(comp_data):
    """Format components from 5e.tools data."""
    if not comp_data:
        return "V, S"
    parts = []
    if comp_data.get("v"):
        parts.append("V")
    if comp_data.get("s"):
        parts.append("S")
    if comp_data.get("m"):
        m = comp_data["m"]
        if isinstance(m, str):
            parts.append(f"M ({m})")
        elif isinstance(m, dict):
            parts.append(f"M ({m.get('text', '')})")
    return ", ".join(parts)


def format_duration(dur_data):
    """Format duration from 5e.tools data."""
    if not dur_data:
        return "Instantaneous"
    d = dur_data[0]
    dtype = d.get("type", "")
    conc = d.get("concentration", False)

    if dtype == "instant":
        return "Instantaneous"
    elif dtype == "permanent":
        return "Until dispelled"
    elif dtype == "special":
        return "Special"
    elif dtype == "timed":
        dur = d.get("duration", {})
        amount = dur.get("amount", 1)
        unit = dur.get("type", "minute")
        if amount != 1:
            unit += "s"
        time_str = f"{amount} {unit}"
        if conc:
            return f"Concentration, up to {time_str}"
        return time_str

    return "Instantaneous"


def is_concentration(dur_data):
    """Check if spell requires concentration."""
    if not dur_data:
        return False
    return dur_data[0].get("concentration", False)


def is_ritual(spell_data):
    """Check if spell can be cast as a ritual."""
    meta = spell_data.get("meta", {})
    return meta.get("ritual", False)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Load XPHB spell data
    with open(XPHB_JSON, "r", encoding="utf-8") as f:
        xphb_data = json.load(f)
    spells_by_name = {s["name"]: s for s in xphb_data["spell"]}
    spells_by_lower = {s["name"].lower(): s for s in xphb_data["spell"]}

    # Load class associations
    with open(SOURCES_JSON, "r", encoding="utf-8") as f:
        sources_data = json.load(f)
    xphb_sources = sources_data.get("XPHB", {})

    print(f"Loaded {len(spells_by_name)} XPHB spells")
    print(f"Loaded {len(xphb_sources)} class association entries")
    print()

    # Walk all spell files
    updated = 0
    skipped = 0
    not_found = 0

    for root, dirs, files in os.walk(SPELL_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue

            filepath = os.path.join(root, fname)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Only update 2024-sourced spells
            if 'source: "2024"' not in content:
                skipped += 1
                continue

            spell_name = fname[:-3]  # Remove .md

            # Handle filename variants
            lookup_name = spell_name
            if lookup_name not in spells_by_name:
                # Try with slash
                lookup_name = spell_name.replace("-", "/")
            if lookup_name not in spells_by_name:
                # Try original
                lookup_name = spell_name

            if lookup_name not in spells_by_name:
                # Case-insensitive fallback
                lower = lookup_name.lower()
                if lower in spells_by_lower:
                    lookup_name = spells_by_lower[lower]["name"]
                else:
                    not_found += 1
                    print(f"  NOT FOUND in XPHB data: {spell_name}")
                    continue

            spell = spells_by_name[lookup_name]

            # Get class list from sources
            classes = []
            spell_sources = xphb_sources.get(lookup_name, {})
            if "class" in spell_sources:
                # Only include XPHB classes (not Artificer from other sources)
                classes = sorted(set(
                    c["name"] for c in spell_sources["class"]
                    if c.get("source") in ("XPHB", "PHB")
                ))
            # Include Artificer if present from any source
            for c in spell_sources.get("class", []):
                if c["name"] == "Artificer" and "Artificer" not in classes:
                    classes.append("Artificer")

            # Build new file content
            school = SCHOOL_MAP.get(spell.get("school", ""), "Evocation")
            level = spell.get("level", 0)
            casting_time = format_time(spell.get("time"))
            spell_range = format_range(spell.get("range"))
            components = format_components(spell.get("components"))
            duration = format_duration(spell.get("duration"))
            concentration = is_concentration(spell.get("duration"))
            ritual = is_ritual(spell)

            # Format description
            desc = format_entries(spell.get("entries", []))

            # Higher level text
            higher = spell.get("entriesHigherLevel", [])
            higher_text = ""
            if higher:
                for h in higher:
                    h_entries = h.get("entries", [])
                    higher_text = format_entries(h_entries)

            # Build class list string
            if classes:
                classes_yaml = "[" + ", ".join(f'"{c}"' for c in classes) + "]"
            else:
                # Fallback: keep existing classes from file
                m = re.search(r'classes:\s*\[([^\]]*)\]', content)
                classes_yaml = f"[{m.group(1)}]" if m else '[]'

            # URL-encode spell name for 5e.tools link
            url_name = lookup_name.lower().replace(" ", "%20").replace("/", "%2f").replace("'", "%27")
            link = f"https://5e.tools/spells.html#{url_name}_xphb"

            # Build markdown
            lines = []
            lines.append("---")
            lines.append("tags: [spell, reference]")
            lines.append(f"spell_level: {level}")
            lines.append(f'school: "{school}"')
            lines.append(f'casting_time: "{strip_tags(casting_time)}"')
            lines.append(f'range: "{spell_range}"')
            lines.append(f'components: "{components}"')
            lines.append(f'duration: "{duration}"')
            lines.append(f"classes: {classes_yaml}")
            lines.append(f"ritual: {'true' if ritual else 'false'}")
            lines.append(f"concentration: {'true' if concentration else 'false'}")
            lines.append('source: "2024"')
            lines.append("---")
            lines.append(f"# {spell_name}")
            lines.append("")
            lines.append(desc)

            if higher_text:
                lines.append("")
                lines.append("## At Higher Levels")
                lines.append(higher_text)

            lines.append("")
            lines.append("---")
            lines.append(f"🔗 [Full Details on 5e.tools]({link})")
            lines.append("")

            new_content = "\n".join(lines)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated += 1

    print(f"Updated: {updated}")
    print(f"Skipped (non-2024): {skipped}")
    print(f"Not found in XPHB data: {not_found}")


if __name__ == "__main__":
    main()
