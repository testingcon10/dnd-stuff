#!/usr/bin/env python3
"""Update the Tenelis spell vault to reflect 2024 PHB changes.

Phase A: Renames & file moves (school changes)
Phase B: Frontmatter property updates (source, school, concentration, classes, etc.)
Phase C: Description updates (redesigned & revised spells)
Phase D: New 2024 spells (11 brand-new files)
"""

import os
import re
import shutil
import urllib.parse

VAULT_SPELLS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Tenelis", "07 - Reference", "Spells",
)

LEVEL_DIRS = {
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_spell_file(name):
    """Find a spell .md file by name anywhere under VAULT_SPELLS."""
    target = f"{name}.md"
    for root, _dirs, files in os.walk(VAULT_SPELLS):
        if target in files:
            return os.path.join(root, target)
    return None


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def split_frontmatter(text):
    """Split into (frontmatter_lines, body). frontmatter_lines excludes --- delimiters."""
    if not text.startswith("---"):
        return [], text
    end = text.find("\n---", 3)
    if end == -1:
        return [], text
    fm_block = text[4:end]  # skip opening ---\n
    fm_lines = fm_block.split("\n")
    body_start = end + 4  # skip \n---
    if body_start < len(text) and text[body_start] == "\n":
        body_start += 1
    return fm_lines, text[body_start:]


def rebuild_file(fm_lines, body):
    """Rebuild file content from frontmatter lines and body."""
    return "---\n" + "\n".join(fm_lines) + "\n---\n" + body


def update_fm_field(fm_lines, field, value):
    """Update a frontmatter field in-place. Returns True if changed."""
    for i, line in enumerate(fm_lines):
        if line.startswith(f"{field}:"):
            if isinstance(value, bool):
                new_val = "true" if value else "false"
            elif isinstance(value, list):
                new_val = "[" + ", ".join(f'"{v}"' for v in value) + "]"
            elif isinstance(value, int):
                new_val = str(value)
            else:
                new_val = f'"{value}"'
            new_line = f"{field}: {new_val}"
            if fm_lines[i] != new_line:
                fm_lines[i] = new_line
                return True
            return False
    return False


def get_fm_field(fm_lines, field):
    """Get a frontmatter field value as raw string."""
    for line in fm_lines:
        if line.startswith(f"{field}:"):
            return line[len(field) + 1:].strip()
    return None


def update_description(body, new_desc, new_higher=None):
    """Replace the description and optional At Higher Levels in the body."""
    # Body format: # Title\n\nDescription\n\n## At Higher Levels\n...\n\n---\nlink
    lines = body.split("\n")

    # Find the title line
    title_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title_idx = i
            break

    if title_idx is None:
        return body

    # Find the footer --- line
    footer_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i] == "---":
            footer_idx = i
            break

    if footer_idx is None:
        return body

    # Rebuild body
    new_lines = lines[:title_idx + 1]  # up to and including # Title
    new_lines.append("")
    new_lines.append(new_desc)

    if new_higher:
        new_lines.append("")
        new_lines.append("## At Higher Levels")
        new_lines.append(new_higher)

    new_lines.append("")
    new_lines.extend(lines[footer_idx:])  # --- and link

    return "\n".join(new_lines)


def update_title(body, new_title):
    """Replace the # Title line in the body."""
    return re.sub(r"^# .+$", f"# {new_title}", body, count=1, flags=re.MULTILINE)


def update_tools_link(body, spell_name, source="2024"):
    """Update the 5e.tools link in the footer."""
    encoded = urllib.parse.quote(spell_name.lower(), safe="'-")
    new_url = f"https://5e.tools/spells.html#{encoded}_{source.lower()}"
    return re.sub(
        r"🔗 \[Full Details on 5e\.tools\]\([^)]+\)",
        f"🔗 [Full Details on 5e.tools]({new_url})",
        body,
    )


def generate_new_spell(spell):
    """Generate a brand-new spell .md file. Returns (path, content)."""
    school = spell["school"]
    level_dir = LEVEL_DIRS[spell["level"]]
    target_dir = os.path.join(VAULT_SPELLS, school, level_dir)
    filepath = os.path.join(target_dir, f"{spell['name']}.md")

    classes_yaml = "[" + ", ".join(f'"{c}"' for c in spell["classes"]) + "]"
    encoded_name = urllib.parse.quote(spell["name"].lower(), safe="'-")
    tools_url = f"https://5e.tools/spells.html#{encoded_name}_2024"

    lines = [
        "---",
        "tags: [spell, reference]",
        f"spell_level: {spell['level']}",
        f'school: "{school}"',
        f'casting_time: "{spell["time"]}"',
        f'range: "{spell["range"]}"',
        f'components: "{spell["comp"]}"',
        f'duration: "{spell["dur"]}"',
        f"classes: {classes_yaml}",
        f"ritual: {'true' if spell.get('ritual') else 'false'}",
        f"concentration: {'true' if spell.get('conc') else 'false'}",
        f'source: "2024"',
        "---",
        f"# {spell['name']}",
        "",
        spell["desc"],
    ]

    if spell.get("higher"):
        lines.append("")
        lines.append("## At Higher Levels")
        lines.append(spell["higher"])

    lines.append("")
    lines.append("---")
    lines.append(f"\U0001f517 [Full Details on 5e.tools]({tools_url})")
    lines.append("")

    return filepath, "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE A: Renames & File Moves
# ══════════════════════════════════════════════════════════════════════════════

def phase_a():
    """Rename and move spell files for school/name changes."""
    print("=" * 70)
    print("PHASE A: Renames & File Moves")
    print("=" * 70)
    moved = 0
    renamed = 0

    # ── A1: Rename Feeblemind -> Befuddlement ──
    old = find_spell_file("Feeblemind")
    if old and not find_spell_file("Befuddlement"):
        content = read_file(old)
        content = update_title(content, "Befuddlement")
        content = update_tools_link(content, "Befuddlement", "2024")
        new_path = os.path.join(os.path.dirname(old), "Befuddlement.md")
        write_file(new_path, content)
        os.remove(old)
        print(f"  RENAMED: Feeblemind -> Befuddlement")
        renamed += 1
    elif find_spell_file("Befuddlement"):
        print(f"  SKIP (exists): Befuddlement")

    # ── A2: Rename Branding Smite -> Shining Smite + move Evocation -> Transmutation ──
    old = find_spell_file("Branding Smite")
    if old and not find_spell_file("Shining Smite"):
        content = read_file(old)
        content = update_title(content, "Shining Smite")
        content = update_tools_link(content, "Shining Smite", "2024")
        new_dir = os.path.join(VAULT_SPELLS, "Transmutation", "2nd Level")
        os.makedirs(new_dir, exist_ok=True)
        new_path = os.path.join(new_dir, "Shining Smite.md")
        write_file(new_path, content)
        os.remove(old)
        print(f"  RENAMED+MOVED: Branding Smite -> Shining Smite (Transmutation/2nd Level)")
        renamed += 1
        moved += 1
    elif find_spell_file("Shining Smite"):
        print(f"  SKIP (exists): Shining Smite")

    # ── A3: School changes — move files to new school directories ──
    school_moves = [
        # (spell_name, old_school, new_school, level_dir)
        ("Cure Wounds", "Evocation", "Abjuration", "1st Level"),
        ("Healing Word", "Evocation", "Abjuration", "1st Level"),
        ("Mass Cure Wounds", "Evocation", "Abjuration", "5th Level"),
        ("Mass Healing Word", "Evocation", "Abjuration", "3rd Level"),
        ("Heal", "Evocation", "Abjuration", "6th Level"),
        ("Prayer of Healing", "Evocation", "Abjuration", "2nd Level"),
        ("Aura of Vitality", "Evocation", "Abjuration", "3rd Level"),
        ("Giant Insect", "Transmutation", "Conjuration", "4th Level"),
    ]

    for name, old_school, new_school, level_dir in school_moves:
        old_path = os.path.join(VAULT_SPELLS, old_school, level_dir, f"{name}.md")
        new_dir = os.path.join(VAULT_SPELLS, new_school, level_dir)
        new_path = os.path.join(new_dir, f"{name}.md")
        if os.path.exists(old_path) and not os.path.exists(new_path):
            os.makedirs(new_dir, exist_ok=True)
            shutil.move(old_path, new_path)
            print(f"  MOVED: {name} ({old_school} -> {new_school})")
            moved += 1
        elif os.path.exists(new_path):
            print(f"  SKIP (already moved): {name}")
        else:
            # Try finding it anywhere
            found = find_spell_file(name)
            if found:
                print(f"  NOTE: {name} found at {found} (not in expected location)")
            else:
                print(f"  WARN: {name} not found!")

    print(f"\n  Phase A complete: {renamed} renamed, {moved} moved")
    return renamed, moved


# ══════════════════════════════════════════════════════════════════════════════
# PHASE B: Frontmatter Property Updates
# ══════════════════════════════════════════════════════════════════════════════

# Spells that need specific frontmatter changes beyond just source->"2024"
# Format: { "Spell Name": { field: new_value, ... } }
FRONTMATTER_UPDATES = {
    # ── School changes (update school field after file move) ──
    "Cure Wounds": {"school": "Abjuration"},
    "Healing Word": {"school": "Abjuration"},
    "Mass Cure Wounds": {"school": "Abjuration"},
    "Mass Healing Word": {"school": "Abjuration"},
    "Heal": {"school": "Abjuration"},
    "Prayer of Healing": {"school": "Abjuration"},
    "Aura of Vitality": {"school": "Abjuration"},
    "Giant Insect": {"school": "Conjuration"},
    "Shining Smite": {"school": "Transmutation"},

    # ── Concentration changes ──
    # Lost concentration (now instantaneous):
    "Divine Favor": {"concentration": False, "duration": "1 minute"},
    "Hail of Thorns": {"concentration": False, "duration": "Instantaneous"},
    "Magic Weapon": {"concentration": False, "duration": "10 minutes"},
    "Lightning Arrow": {"concentration": False, "duration": "Instantaneous"},
    "Barkskin": {"concentration": False, "duration": "1 hour"},
    "Ensnaring Strike": {"concentration": False, "duration": "Instantaneous"},
    "Searing Smite": {"concentration": False, "duration": "Instantaneous"},
    "Thunderous Smite": {"concentration": False, "duration": "Instantaneous"},
    "Wrathful Smite": {"concentration": False, "duration": "1 minute"},
    "Blinding Smite": {"concentration": False, "duration": "Instantaneous"},
    "Staggering Smite": {"concentration": False, "duration": "Instantaneous"},
    "Banishing Smite": {"concentration": False, "duration": "Instantaneous"},
    "Animal Shapes": {"concentration": False},

    # Gained concentration:
    "Spiritual Weapon": {"concentration": True, "duration": "Concentration, up to 1 minute"},
    "Blade Ward": {"concentration": True, "duration": "Concentration, up to 1 round"},
    "Forcecage": {"concentration": True, "duration": "Concentration, up to 1 hour"},

    # ── True Strike — complete overhaul (school change + everything) ──
    "True Strike": {
        "school": "Divination",  # stays Divination
        "casting_time": "1 action",
        "range": "Self",
        "components": "S, M (a weapon with which you have proficiency and that is worth 1+ CP)",
        "duration": "Instantaneous",
        "concentration": False,
        "classes": ["Bard", "Sorcerer", "Warlock", "Wizard"],
    },

    # ── Guidance — now reaction ──
    "Guidance": {
        "casting_time": "1 reaction (when you or an ally within 10 feet fails an ability check)",
        "range": "10 feet",
        "duration": "Instantaneous",
        "concentration": False,
    },

    # ── Blade Ward — reworked ──
    "Blade Ward": {
        "casting_time": "1 action",
        "duration": "Concentration, up to 1 round",
        "concentration": True,
    },

    # ── Resistance — now reaction ──
    "Resistance": {
        "casting_time": "1 reaction (when you or an ally within 10 feet fails a saving throw)",
        "range": "10 feet",
        "duration": "Instantaneous",
        "concentration": False,
    },

    # ── Chill Touch — renamed effect (still Chill Touch name, but necrotic hand) ──
    "Chill Touch": {
        "range": "Touch",
        "school": "Necromancy",
    },

    # ── Friends cantrip ──
    "Friends": {
        "duration": "Concentration, up to 1 minute",
    },

    # ── Sleep — no longer uses HP pool ──
    "Sleep": {
        "components": "V, S, M (a pinch of sand)",
        "duration": "Concentration, up to 1 minute",
        "concentration": True,
    },

    # ── Color Spray ──
    "Color Spray": {
        "duration": "Instantaneous",
    },

    # ── Chromatic Orb ──
    "Chromatic Orb": {
        "components": "V, S, M (a diamond worth at least 50 gp)",
    },

    # ── Barkskin — no longer concentration, flat AC ──
    "Barkskin": {
        "duration": "1 hour",
        "concentration": False,
        "casting_time": "1 bonus action",
    },

    # ── Prayer of Healing — now 10 min cast ──
    "Prayer of Healing": {
        "casting_time": "10 minutes",
        "school": "Abjuration",
    },

    # ── Enhance Ability ──
    "Enhance Ability": {
        "classes": ["Bard", "Cleric", "Druid", "Ranger", "Sorcerer", "Wizard"],
    },

    # ── Enthrall ──
    "Enthrall": {
        "casting_time": "1 action",
        "duration": "1 hour",
        "concentration": False,
    },

    # ── Find Steed ──
    "Find Steed": {
        "duration": "Instantaneous",
        "casting_time": "1 action",
    },

    # ── Ray of Enfeeblement ──
    "Ray of Enfeeblement": {
        "duration": "Concentration, up to 1 minute",
    },

    # ── Conjure Animals — AoE now ──
    "Conjure Animals": {
        "duration": "Concentration, up to 10 minutes",
        "range": "60 feet",
    },

    # ── Counterspell — now CON save ──
    "Counterspell": {
        "casting_time": "1 reaction (when you see a creature within 60 feet casting a spell)",
    },

    # ── Conjure Minor Elementals ──
    "Conjure Minor Elementals": {
        "duration": "Concentration, up to 10 minutes",
        "range": "Self (15-foot emanation)",
    },

    # ── Conjure Woodland Beings ──
    "Conjure Woodland Beings": {
        "duration": "Concentration, up to 10 minutes",
        "range": "Self (10-foot emanation)",
    },

    # ── Grasping Vine ──
    "Grasping Vine": {
        "range": "60 feet",
    },

    # ── Animate Objects ──
    "Animate Objects": {
        "range": "120 feet",
    },

    # ── Conjure Elemental ──
    "Conjure Elemental": {
        "duration": "Concentration, up to 10 minutes",
        "range": "60 feet",
    },

    # ── Contagion — immediate effect now ──
    "Contagion": {
        "duration": "14 days",
        "concentration": False,
    },

    # ── Conjure Fey ──
    "Conjure Fey": {
        "duration": "Concentration, up to 10 minutes",
        "range": "60 feet",
    },

    # ── Conjure Celestial ──
    "Conjure Celestial": {
        "duration": "Concentration, up to 10 minutes",
        "range": "60 feet",
    },

    # ── Polymorph family — temp HP instead of replacing HP ──
    "Polymorph": {},
    "True Polymorph": {},
    "Shapechange": {},

    # ── Aura of Vitality — free action healing ──
    "Aura of Vitality": {
        "school": "Abjuration",
        "classes": ["Cleric", "Druid", "Paladin"],
    },

    # ── Cloud of Daggers — now moveable ──
    "Cloud of Daggers": {},

    # ── Ray of Sickness ──
    "Ray of Sickness": {},

    # ── Grease ──
    "Grease": {},

    # ── Wish ──
    "Wish": {},

    # ── XGE/TCE spells incorporated into 2024 (source update) ──
    "Mind Sliver": {"classes": ["Sorcerer", "Warlock", "Wizard"]},
    "Summon Beast": {"classes": ["Druid", "Ranger"]},
    "Summon Fey": {"classes": ["Druid", "Ranger", "Warlock", "Wizard"]},
    "Summon Undead": {"classes": ["Warlock", "Wizard"]},
    "Summon Aberration": {"classes": ["Warlock", "Wizard"]},
    "Summon Construct": {"classes": ["Wizard"]},
    "Summon Elemental": {"classes": ["Druid", "Ranger", "Wizard"]},
    "Summon Celestial": {"classes": ["Cleric", "Paladin"]},
    "Summon Fiend": {"classes": ["Warlock", "Wizard"]},
    "Thunderclap": {"classes": ["Bard", "Druid", "Sorcerer", "Wizard"]},
    "Toll the Dead": {"classes": ["Cleric", "Warlock"]},
    "Word of Radiance": {"classes": ["Cleric"]},
    "Ice Knife": {"classes": ["Druid", "Sorcerer", "Wizard"]},
    "Dragon's Breath": {"classes": ["Sorcerer", "Wizard"]},
    "Mind Spike": {"classes": ["Sorcerer", "Warlock", "Wizard"]},
    "Charm Monster": {"classes": ["Bard", "Druid", "Sorcerer", "Warlock", "Wizard"]},
    "Vitriolic Sphere": {"classes": ["Sorcerer", "Wizard"]},
    "Steel Wind Strike": {"classes": ["Ranger", "Wizard"]},
    "Synaptic Static": {"classes": ["Bard", "Sorcerer", "Warlock", "Wizard"]},

    # ── Smite spells — lost concentration, now instantaneous ──
    "Searing Smite": {
        "duration": "Instantaneous",
        "concentration": False,
        "classes": ["Paladin"],
    },
    "Thunderous Smite": {
        "duration": "Instantaneous",
        "concentration": False,
        "classes": ["Paladin"],
    },
    "Wrathful Smite": {
        "duration": "1 minute",
        "concentration": False,
        "classes": ["Paladin"],
    },
    "Blinding Smite": {
        "duration": "Instantaneous",
        "concentration": False,
        "classes": ["Paladin"],
    },
    "Staggering Smite": {
        "duration": "Instantaneous",
        "concentration": False,
        "classes": ["Paladin"],
    },
    "Banishing Smite": {
        "duration": "Instantaneous",
        "concentration": False,
        "classes": ["Paladin"],
    },

    # ── Other notable 2024 changes ──
    "Spiritual Weapon": {
        "concentration": True,
        "duration": "Concentration, up to 1 minute",
    },
    "Heroism": {"classes": ["Bard", "Paladin"]},
    "Command": {"classes": ["Bard", "Cleric", "Paladin"]},
    "Detect Magic": {"classes": ["Bard", "Cleric", "Druid", "Paladin", "Ranger", "Sorcerer", "Wizard"]},
    "Protection from Evil and Good": {"classes": ["Cleric", "Druid", "Paladin", "Warlock", "Wizard"]},
    "Bless": {"classes": ["Cleric", "Paladin"]},
    "Shield of Faith": {"classes": ["Cleric", "Paladin"]},
    "Aid": {"classes": ["Bard", "Cleric", "Druid", "Paladin", "Ranger"]},
    "Lesser Restoration": {"classes": ["Bard", "Cleric", "Druid", "Paladin", "Ranger"]},
    "Dispel Magic": {"classes": ["Bard", "Cleric", "Druid", "Paladin", "Sorcerer", "Warlock", "Wizard"]},
    "Revivify": {"classes": ["Cleric", "Druid", "Paladin", "Ranger"]},
    "Death Ward": {"classes": ["Cleric", "Paladin"]},
    "Greater Restoration": {"classes": ["Bard", "Cleric", "Druid"]},
    "Raise Dead": {"classes": ["Bard", "Cleric", "Paladin"]},
    "Find Greater Steed": {"classes": ["Paladin"]},
    "Magic Weapon": {
        "concentration": False,
        "duration": "10 minutes",
        "classes": ["Paladin", "Ranger", "Sorcerer", "Wizard"],
    },
    "Hail of Thorns": {
        "concentration": False,
        "duration": "Instantaneous",
        "classes": ["Ranger"],
    },
    "Lightning Arrow": {
        "concentration": False,
        "duration": "Instantaneous",
        "classes": ["Ranger"],
    },
    "Forcecage": {
        "concentration": True,
        "duration": "Concentration, up to 1 hour",
    },
    "Animal Shapes": {
        "concentration": False,
        "duration": "24 hours",
    },
    "Befuddlement": {
        "school": "Enchantment",
        "classes": ["Bard", "Druid", "Warlock", "Wizard"],
    },
}

# The 19 XGE/TCE spells that became 2024 PHB spells
XGE_TCE_TO_2024 = [
    "Mind Sliver", "Summon Beast", "Summon Fey", "Summon Undead",
    "Summon Aberration", "Summon Construct", "Summon Elemental",
    "Summon Celestial", "Summon Fiend",
    "Thunderclap", "Toll the Dead", "Word of Radiance", "Ice Knife",
    "Dragon's Breath", "Mind Spike", "Charm Monster", "Vitriolic Sphere",
    "Steel Wind Strike", "Synaptic Static",
]


def phase_b():
    """Update frontmatter properties on all PHB spells + 19 XGE/TCE spells."""
    print("\n" + "=" * 70)
    print("PHASE B: Frontmatter Property Updates")
    print("=" * 70)
    updated = 0
    source_updated = 0

    for root, _dirs, files in os.walk(VAULT_SPELLS):
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            name = fname[:-3]
            path = os.path.join(root, fname)
            content = read_file(path)
            fm_lines, body = split_frontmatter(content)
            if not fm_lines:
                continue

            changed = False
            current_source = get_fm_field(fm_lines, "source")

            # Update source to "2024" for PHB and incorporated XGE/TCE spells
            if current_source in ['"PHB"', '"2024"']:
                if current_source != '"2024"':
                    update_fm_field(fm_lines, "source", "2024")
                    changed = True
                    source_updated += 1
            elif name in XGE_TCE_TO_2024:
                update_fm_field(fm_lines, "source", "2024")
                changed = True
                source_updated += 1

            # Apply specific frontmatter updates
            if name in FRONTMATTER_UPDATES:
                updates = FRONTMATTER_UPDATES[name]
                for field, value in updates.items():
                    # Map field names
                    fm_field = {
                        "school": "school",
                        "concentration": "concentration",
                        "duration": "duration",
                        "casting_time": "casting_time",
                        "range": "range",
                        "components": "components",
                        "classes": "classes",
                        "ritual": "ritual",
                    }.get(field, field)
                    if update_fm_field(fm_lines, fm_field, value):
                        changed = True

            if changed:
                new_content = rebuild_file(fm_lines, body)
                write_file(path, new_content)
                updated += 1
                print(f"  UPDATED: {name}")

    print(f"\n  Phase B complete: {updated} files updated, {source_updated} sources -> 2024")
    return updated


# ══════════════════════════════════════════════════════════════════════════════
# PHASE C: Description Updates
# ══════════════════════════════════════════════════════════════════════════════

# Full rewrites for redesigned spells
DESCRIPTION_REWRITES = {
    "True Strike": {
        "desc": "Guided by a flash of magical insight, you make one attack with the weapon used in the spell's casting. The attack uses your spellcasting ability modifier for the attack and damage rolls. If the attack deals damage, it can be Radiant damage or the weapon's normal damage type (your choice).\n\nThis spell's damage increases when you reach certain levels. At 5th level, the attack deals an extra 1d6 Radiant damage. The extra damage increases by 1d6 at 11th level (2d6) and 17th level (3d6).",
    },
    "Blade Ward": {
        "desc": "You extend your hand and trace a sigil of warding in the air. Until the end of your next turn, you have Resistance to Bludgeoning, Piercing, and Slashing damage dealt by weapon attacks.",
    },
    "Chill Touch": {
        "desc": "You touch one creature and channel necrotic energy into it. The target must succeed on a Constitution saving throw or take 1d10 Necrotic damage. If the target is an Undead, it also has Disadvantage on attack rolls against you until the end of your next turn.\n\nThis spell's damage increases by 1d10 when you reach 5th level (2d10), 11th level (3d10), and 17th level (4d10).",
    },
    "Friends": {
        "desc": "You magically emanate a sense of friendship toward one visible creature within range. The target must succeed on a Wisdom saving throw or be Charmed by you for the duration. The Charmed creature is friendly to you. When the spell ends, the creature knows it was Charmed by you.",
    },
    "Guidance": {
        "desc": "You channel divine insight. When you or an ally within 10 feet of you fails an ability check, you can use your Reaction to give a 1d4 bonus to the check, potentially turning the failure into a success.",
    },
    "Resistance": {
        "desc": "You channel divine protection. When you or an ally within 10 feet of you fails a saving throw, you can use your Reaction to add 1d4 to the save, potentially turning the failure into a success.",
    },
    "Sleep": {
        "desc": "You send creatures into a magical slumber. Each creature of your choice that you can see within range must succeed on a Wisdom saving throw or have the Unconscious condition for the duration. An Unconscious creature wakes if it takes damage or if another creature uses an action to shake it awake.",
        "higher": "When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.",
    },
    "Color Spray": {
        "desc": "You unleash a dazzling array of flashing, colored light. Each creature in a 15-foot Cone originating from you must succeed on a Constitution saving throw or have the Blinded condition until the end of your next turn.",
    },
    "Chromatic Orb": {
        "desc": "You hurl an orb of energy at a creature you can see within range. Choose Acid, Cold, Fire, Lightning, Poison, or Thunder for the type of orb you create, and then make a ranged spell attack against the target. On a hit, the target takes 3d8 damage of the chosen type. If you roll the same number on two or more of the d8s, the orb leaps to a different target of your choice within 30 feet of the first target, requiring a new attack roll against the new target and dealing the same damage.",
        "higher": "When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st.",
    },
    "Barkskin": {
        "desc": "You touch a willing creature. Until the spell ends, the target's skin has a rough, bark-like appearance, and the target has an AC of 17 if its AC is lower than that.",
    },
    "Enhance Ability": {
        "desc": "You touch a creature and bestow upon it a magical enhancement. Choose one of the following effects; the target gains that effect until the spell ends.\n\nBear's Endurance: The target has Advantage on Constitution checks and gains 2d6 Temporary Hit Points.\nBull's Strength: The target has Advantage on Strength checks and its carrying capacity doubles.\nCat's Grace: The target has Advantage on Dexterity checks and takes no damage from falling 20 feet or less.\nEagle's Splendor: The target has Advantage on Charisma checks.\nFox's Cunning: The target has Advantage on Intelligence checks.\nOwl's Wisdom: The target has Advantage on Wisdom checks.",
        "higher": "When you cast this spell using a spell slot of 3rd level or higher, you can target one additional creature for each slot level above 2nd.",
    },
    "Enthrall": {
        "desc": "You weave a distracting string of words, causing creatures of your choice that you can see within range to make a Wisdom saving throw. Any creature you or your companions are fighting automatically succeeds. On a failed save, a target has Disadvantage on Wisdom (Perception) checks made to perceive any creature other than you until the spell ends.",
    },
    "Find Steed": {
        "desc": "You summon a spirit that assumes the form of an unusually intelligent, strong, and loyal steed, creating a lasting bond with it. The steed takes a form you choose: Camel, Elk, Draft Horse, Mastiff, Pony, or Riding Horse. The steed has the statistics of the chosen form, though it is a Celestial, Fey, or Fiend (your choice) instead of its normal creature type. While mounted on it, you can make any spell you cast that targets only you also target the steed.\n\nWhen the steed drops to 0 Hit Points, it disappears. You can dismiss the steed at any time as an action, causing it to disappear. Casting this spell again summons the same steed, restored to its Hit Point maximum.",
    },
    "Prayer of Healing": {
        "desc": "Up to five creatures of your choice that are within range each regain Hit Points equal to 2d8 + your spellcasting ability modifier.",
        "higher": "When you cast this spell using a spell slot of 3rd level or higher, the healing increases by 1d8 for each slot level above 2nd.",
    },
    "Ray of Enfeeblement": {
        "desc": "A black beam of enervating energy springs from your finger toward a creature within range. Make a ranged spell attack against the target. On a hit, the target deals only half damage with weapon attacks that use Strength until the spell ends. The target makes a Constitution saving throw at the end of each of its turns; on a success, the spell ends.",
    },
    "Conjure Animals": {
        "desc": "You conjure nature spirits that fill a 15-foot-radius Sphere centered on a point you can see within range. The spirits last for the duration and create one of the following effects within the Sphere on each of your turns as a Bonus Action: each creature of your choice in the Sphere must succeed on a Dexterity saving throw or take 2d10 Slashing damage from spectral claws and fangs.",
        "higher": "When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d10 for each slot level above 3rd.",
    },
    "Counterspell": {
        "desc": "You attempt to interrupt a creature in the process of casting a spell. The creature must make a Constitution saving throw. On a failed save, the creature's spell fails and has no effect.",
        "higher": "When you cast this spell using a spell slot of 4th level or higher, the interrupted spell has no effect if its level is equal to or less than the level of the spell slot you used.",
    },
    "Conjure Minor Elementals": {
        "desc": "You conjure elemental spirits that swirl around you. Until the spell ends, whenever you deal damage with an attack or a spell, you can deal an extra 2d8 damage of a type appropriate to the spirits: Cold, Fire, Lightning, or Thunder (your choice when you deal the damage). Once on each of your turns, you can also use this extra damage when you deal damage with a spell attack.",
        "higher": "When you cast this spell using a spell slot of 5th level or higher, the extra damage increases by 2d8 for each slot level above 4th.",
    },
    "Conjure Woodland Beings": {
        "desc": "You conjure nature spirits that fill a 10-foot-radius area around you. Until the spell ends, each creature of your choice that enters this area for the first time on a turn or starts its turn there must succeed on a Wisdom saving throw or have the Charmed condition until the spell ends. A Charmed creature also takes 4d8 Radiant damage when it enters the area or starts its turn there.",
        "higher": "When you cast this spell using a spell slot of 5th level or higher, the damage increases by 2d8 for each slot level above 4th.",
    },
    "Giant Insect": {
        "desc": "You summon a giant centipede, spider, wasp, or scorpion, and it appears in an unoccupied space you can see within range. The creature is friendly to you and your companions. In combat, the creature acts on your initiative count. It obeys your verbal commands (no action required by you). The creature disappears when it drops to 0 Hit Points or when the spell ends.",
        "higher": "When you cast this spell using a spell slot of 5th level or higher, you summon a second creature. If you use a 6th-level slot, you summon a third creature.",
    },
    "Grasping Vine": {
        "desc": "You conjure a vine that sprouts from a surface in an unoccupied space that you can see within range. The vine lasts for the duration. Make a melee spell attack against one creature within 30 feet of the vine. On a hit, the target takes 4d8 Bludgeoning damage and is pulled up to 30 feet toward the vine. On each of your subsequent turns, you can use a Bonus Action to repeat the attack against a creature within 30 feet of the vine.",
        "higher": "When you cast this spell using a spell slot of 5th level or higher, the damage increases by 1d8 for each slot level above 4th.",
    },
    "Animate Objects": {
        "desc": "Objects come to life at your command. Choose up to ten nonmagical objects within range that are not being worn or carried. Medium targets count as two objects, Large targets count as four objects, and Huge targets count as eight objects. You can't animate an object larger than Huge. Each target animates and becomes a creature under your control until the spell ends or until reduced to 0 Hit Points. The animated objects act on your turn and use a simple stat block based on their size.",
        "higher": "When you cast this spell using a spell slot of 6th level or higher, you can animate two additional objects for each slot level above 5th.",
    },
    "Conjure Elemental": {
        "desc": "You conjure elemental energy that fills a 15-foot-radius Sphere centered on a point you can see within range. The energy lasts for the duration and creates one of the following effects on each of your turns as a Bonus Action: each creature of your choice in the Sphere takes 6d8 damage of a type you choose — Acid, Cold, Fire, or Thunder.",
        "higher": "When you cast this spell using a spell slot of 6th level or higher, the damage increases by 2d8 for each slot level above 5th.",
    },
    "Contagion": {
        "desc": "Your touch inflicts a disease. Make a melee spell attack against a creature within your reach. On a hit, you afflict the creature with a disease of your choice from the list below. The disease's effects begin immediately.\n\nBlinding Sickness: The creature has Disadvantage on Wisdom checks and Wisdom saving throws and has the Blinded condition.\nFilth Fever: The creature has Disadvantage on Strength checks, Strength saving throws, and attack rolls that use Strength.\nFlesh Rot: The creature has Disadvantage on Charisma checks and is Vulnerable to all damage.\nMindfire: The creature has Disadvantage on Intelligence checks and Intelligence saving throws, and it behaves as if under the confusion spell during combat.\nSeizure: The creature has Disadvantage on Dexterity checks, Dexterity saving throws, and attack rolls that use Dexterity.\nSlimy Doom: The creature has Disadvantage on Constitution checks and Constitution saving throws, and it has the Stunned condition whenever it takes damage.\n\nThe diseased creature makes a Constitution saving throw at the end of each of its turns. After three failed saves, the disease lasts for 14 days. After three successful saves, the creature recovers.",
    },
    "Conjure Fey": {
        "desc": "You conjure a swirling mass of fey energy in a 10-foot-radius Sphere centered on a point you can see within range. Each creature of your choice in the Sphere when it appears must succeed on a Wisdom saving throw or have the Charmed condition for the duration. On each of your turns, you can use a Bonus Action to move the Sphere up to 30 feet. Each creature of your choice that enters the Sphere or starts its turn there must also save or take 6d12 Psychic damage.",
    },
    "Conjure Celestial": {
        "desc": "You conjure a pillar of divine energy that fills a 20-foot-radius, 40-foot-high Cylinder centered on a point you can see within range. Each creature of your choice in the Cylinder when it appears regains Hit Points equal to 4d12 + your spellcasting ability modifier. Each creature of your choice that enters the Cylinder or starts its turn there also regains the same amount of Hit Points. Additionally, the Cylinder is Difficult Terrain for creatures of your choice.",
    },
    "Befuddlement": {
        "desc": "You blast the mind of one creature you can see within range. The target must make an Intelligence saving throw. On a failed save, the target takes 10d12 Psychic damage and can't cast spells or take the Magic action until the spell ends. At the end of every 30 days, the target repeats the save, ending the effect on a success. The effect can also be ended by the Greater Restoration, Heal, or Wish spell.",
    },
}

# Targeted edits for revised spells (just key changes, not full rewrites)
DESCRIPTION_EDITS = {
    "Polymorph": {
        "desc": "This spell transforms a creature you can see within range into a new form. An unwilling creature must make a Wisdom saving throw to avoid the effect. A shapechanger automatically succeeds. The transformation lasts for the duration or until the target drops to 0 Hit Points or dies.\n\nThe new form can be any Beast whose challenge rating is equal to or less than the target's level or challenge rating. The target's game statistics are replaced by the statistics of the chosen Beast, but the target retains its personality, Hit Point maximum, and Hit Points. The target gains a number of Temporary Hit Points equal to the Hit Points of the new form. The target is limited in the actions it can perform by the nature of its new form, and it can't speak or cast spells. The target's gear melds into the new form.",
    },
    "True Polymorph": {
        "desc": "Choose one creature or nonmagical object you can see within range. The creature is transformed into a different creature or into an object; or the object is transformed into a creature. The transformation lasts for the duration or until the target drops to 0 Hit Points or dies. If you concentrate on this spell for the full duration, the spell lasts until dispelled.\n\nCreature into Creature: The new form can be any kind of creature whose challenge rating is equal to or less than the target's. The target's statistics are replaced by the statistics of the new form, but it retains its personality, Hit Point maximum, and Hit Points. The target gains Temporary Hit Points equal to the Hit Points of the new form.",
    },
    "Animal Shapes": {
        "desc": "You choose any number of willing creatures that you can see within range. Each target transforms into a Large or smaller Beast with a challenge rating of 4 or lower. On subsequent turns, you can use your action to transform the targets into new forms. The transformation lasts for the duration for each target, or until the target drops to 0 Hit Points or dies. You can choose a different form for each target. A target's statistics are replaced by the statistics of the chosen Beast, but the target retains its personality, Hit Point maximum, and Hit Points. It gains Temporary Hit Points equal to the Hit Points of the new form.",
    },
    "Shapechange": {
        "desc": "You assume the form of a different creature for the duration. The new form can be of any creature with a challenge rating equal to your level or lower. The creature can't be a Construct or Undead. Your statistics are replaced by the statistics of the chosen creature, though you retain your personality, Hit Point maximum, and Hit Points. You gain Temporary Hit Points equal to the Hit Points of the new form. You also retain your class features and can cast spells. If the new form can make multiple attacks, you can use that ability.",
    },
    "Cloud of Daggers": {
        "desc": "You fill the air with spinning daggers in a Cube 5 feet on each side, centered on a point you choose within range. A creature takes 4d4 Slashing damage when it enters the area for the first time on a turn or starts its turn there. You can also move the Cube up to 10 feet as a Bonus Action on your turns.",
        "higher": "When you cast this spell using a spell slot of 3rd level or higher, the damage increases by 2d4 for each slot level above 2nd.",
    },
    "Ray of Sickness": {
        "desc": "A ray of sickening greenish energy lashes out toward a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 2d8 Poison damage and has the Poisoned condition until the end of your next turn.",
        "higher": "When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st.",
    },
    "Grease": {
        "desc": "Nonflammable grease covers the ground in a 10-foot square centered on a point within range and turns it into Difficult Terrain for the duration. When the grease appears, each creature standing in its area must succeed on a Dexterity saving throw or have the Prone condition. A creature that enters the area or ends its turn there must also succeed on a Dexterity saving throw or have the Prone condition.",
    },
    "Wish": {
        "desc": "Wish is the mightiest spell a mortal creature can cast. By simply speaking aloud, you can alter the very foundations of reality in accord with your desires.\n\nThe most basic use of this spell is to duplicate any other spell of 8th level or lower. If you use it for any other effect, you describe the wish to the DM. The DM has great latitude in ruling what occurs; the greater the wish, the greater the likelihood that something goes wrong. The stress of casting this spell to produce any effect other than duplicating another spell weakens you, and there is a 33% chance you are never able to cast wish again.",
    },
    "Aura of Vitality": {
        "desc": "Healing energy radiates from you in a 30-foot-radius Aura. Until the spell ends, whenever you or a creature in the Aura regains Hit Points from a spell, that creature regains an additional 2d6 Hit Points.",
    },
    "Divine Favor": {
        "desc": "Your prayer empowers you with divine radiance. Until the spell ends, your weapon attacks deal an extra 1d4 Radiant damage on a hit.",
    },
    "Hail of Thorns": {
        "desc": "As part of casting this spell, you make a ranged weapon attack. If you hit, the target and each creature within 5 feet of the target must succeed on a Dexterity saving throw or take 1d10 Piercing damage.",
        "higher": "When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d10 for each slot level above 1st.",
    },
    "Magic Weapon": {
        "desc": "You touch a nonmagical weapon. Until the spell ends, that weapon becomes a +1 magic weapon.",
        "higher": "When you cast this spell using a 4th-level spell slot, the bonus increases to +2. When you use a 6th-level spell slot, the bonus increases to +3.",
    },
    "Lightning Arrow": {
        "desc": "As part of casting this spell, you make a ranged weapon attack. If you hit, the target takes Lightning damage instead of the weapon's normal damage type, and the target takes an extra 4d8 Lightning damage. Hit or miss, each creature within 10 feet of the target must succeed on a Dexterity saving throw or take 2d8 Lightning damage.",
        "higher": "When you cast this spell using a spell slot of 4th level or higher, the extra Lightning damage on a hit increases by 1d8 for each slot level above 3rd.",
    },
    "Ensnaring Strike": {
        "desc": "As part of casting this spell, you make a weapon attack. If you hit, a writhing mass of thorny vines appears at the point of impact, and the target must succeed on a Strength saving throw or have the Restrained condition until the spell ends. A Large or larger creature has Advantage on this saving throw. The Restrained target takes 1d6 Piercing damage at the start of each of its turns. A creature Restrained by the vines or an adjacent creature can use an action to make a Strength check against your spell save DC, freeing the Restrained creature on a success.",
        "higher": "When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d6 for each slot level above 1st.",
    },
    "Searing Smite": {
        "desc": "As you hit the target, it takes an extra 1d6 Fire damage from the attack. At the start of each of its turns, the target must make a Constitution saving throw. On a failed save, it takes 1d6 Fire damage. On a successful save, the ongoing effect ends.",
        "higher": "When you cast this spell using a spell slot of 2nd level or higher, all the damage increases by 1d6 for each slot level above 1st.",
    },
    "Thunderous Smite": {
        "desc": "Your weapon rings with thunder. The attack deals an extra 2d6 Thunder damage. Additionally, if the target is a creature, it must succeed on a Strength saving throw or be pushed 10 feet away from you and have the Prone condition.",
    },
    "Wrathful Smite": {
        "desc": "Your attack deals an extra 1d6 Psychic damage. Additionally, if the target is a creature, it must succeed on a Wisdom saving throw or have the Frightened condition until the spell ends. At the end of each of its turns, the Frightened creature repeats the save, ending the effect on itself on a success.",
    },
    "Blinding Smite": {
        "desc": "Your weapon flares with bright light. The attack deals an extra 3d8 Radiant damage. Additionally, the target must succeed on a Constitution saving throw or have the Blinded condition until the spell ends. A creature Blinded by this spell makes a Constitution saving throw at the end of each of its turns, ending the effect on itself on a success.",
    },
    "Staggering Smite": {
        "desc": "Your weapon strikes with overwhelming force. The attack deals an extra 4d6 Psychic damage. Additionally, if the target is a creature, it must succeed on a Wisdom saving throw or have the Stunned condition until the end of your next turn.",
    },
    "Banishing Smite": {
        "desc": "Your weapon crackles with force. The attack deals an extra 5d10 Force damage. Additionally, if this attack reduces the target to 50 Hit Points or fewer, the target must succeed on a Charisma saving throw or be banished to a harmless demiplane, where it has the Incapacitated condition. At the end of your next turn, the target reappears in the space it left or the nearest unoccupied space.",
    },
    "Spiritual Weapon": {
        "desc": "You create a floating, spectral weapon within range that lasts for the duration. When you cast the spell, you can make a melee spell attack against a creature within 5 feet of the weapon. On a hit, the target takes Force damage equal to 1d8 + your spellcasting ability modifier. As a Bonus Action on your turn, you can move the weapon up to 20 feet and repeat the attack.",
        "higher": "When you cast this spell using a spell slot of 3rd level or higher, the damage increases by 1d8 for every two slot levels above 2nd.",
    },
    "Forcecage": {
        "desc": "An immobile, invisible, cube-shaped prison composed of magical force springs into existence around an area you choose within range. The prison can be a cage or a solid box, as you choose.\n\nA cage can be up to 20 feet on a side and is made from 1/2-inch diameter bars spaced 1/2 inch apart. A solid box can be up to 10 feet on a side. A creature inside the cage can't leave it by nonmagical means. If the creature tries to use teleportation or interplanar travel, it must first make a Charisma saving throw. On a success, the creature is teleported; on a failure, it can't leave the cage.",
    },
    "Barkskin": {
        "desc": "You touch a willing creature. Until the spell ends, the target's skin has a rough, bark-like appearance, and the target has an AC of 17 if its AC is lower than that.",
    },
}


def phase_c():
    """Update spell descriptions for redesigned and revised spells."""
    print("\n" + "=" * 70)
    print("PHASE C: Description Updates")
    print("=" * 70)
    rewritten = 0
    edited = 0

    # Process full rewrites
    for name, data in DESCRIPTION_REWRITES.items():
        path = find_spell_file(name)
        if not path:
            print(f"  WARN: {name} not found for rewrite!")
            continue
        content = read_file(path)
        fm_lines, body = split_frontmatter(content)
        body = update_description(body, data["desc"], data.get("higher"))
        body = update_tools_link(body, name, "2024")
        new_content = rebuild_file(fm_lines, body)
        if new_content == content:
            continue
        write_file(path, new_content)
        print(f"  REWRITE: {name}")
        rewritten += 1

    # Process targeted edits
    for name, data in DESCRIPTION_EDITS.items():
        if name in DESCRIPTION_REWRITES:
            continue  # already handled
        path = find_spell_file(name)
        if not path:
            print(f"  WARN: {name} not found for edit!")
            continue
        content = read_file(path)
        fm_lines, body = split_frontmatter(content)
        body = update_description(body, data["desc"], data.get("higher"))
        body = update_tools_link(body, name, "2024")
        new_content = rebuild_file(fm_lines, body)
        if new_content == content:
            continue
        write_file(path, new_content)
        print(f"  EDIT: {name}")
        edited += 1

    print(f"\n  Phase C complete: {rewritten} rewritten, {edited} edited")
    return rewritten, edited


# ══════════════════════════════════════════════════════════════════════════════
# PHASE D: New 2024 Spells
# ══════════════════════════════════════════════════════════════════════════════

NEW_SPELLS_2024 = [
    {
        "name": "Arcane Vigor",
        "level": 2,
        "school": "Abjuration",
        "time": "1 bonus action",
        "range": "Self",
        "comp": "V, S",
        "dur": "Instantaneous",
        "classes": ["Sorcerer", "Wizard"],
        "conc": False,
        "desc": "You tap into your life force to heal yourself. You regain Hit Points equal to twice the spell slot level used to cast this spell.",
    },
    {
        "name": "Divine Smite",
        "level": 1,
        "school": "Evocation",
        "time": "1 bonus action, which you take immediately after hitting a target with a melee weapon or an Unarmed Strike",
        "range": "Self",
        "comp": "V",
        "dur": "Instantaneous",
        "classes": ["Paladin"],
        "conc": False,
        "desc": "The target takes an extra 2d8 Radiant damage from the attack. The damage increases by 1d8 if the target is a Fiend or an Undead.",
        "higher": "When you cast this spell using a spell slot of 2nd level or higher, the extra damage increases by 1d8 for each slot level above 1st.",
    },
    {
        "name": "Elementalism",
        "level": 0,
        "school": "Transmutation",
        "time": "1 action",
        "range": "30 feet",
        "comp": "V, S",
        "dur": "Instantaneous",
        "classes": ["Druid", "Sorcerer", "Wizard"],
        "conc": False,
        "desc": "You exert control over the elements, creating one of the following effects within range: a harmless sensory effect related to air, earth, fire, or water (such as a shower of sparks, a puff of wind, a spray of light mist, or a gentle rumbling of stone); you instantaneously light or snuff out a candle, torch, or small campfire; you chill or warm up to 1 pound of nonliving material for up to 1 hour; or you cause earth, fire, water, or mist to shape itself into a crude form you designate for 1 minute.",
    },
    {
        "name": "Fount of Moonlight",
        "level": 4,
        "school": "Evocation",
        "time": "1 action",
        "range": "Self",
        "comp": "V, S",
        "dur": "Concentration, up to 10 minutes",
        "classes": ["Bard", "Druid"],
        "conc": True,
        "desc": "A cool light wreathing your body sheds Bright Light in a 20-foot radius and Dim Light for an additional 20 feet for the duration. Until the spell ends, you have Resistance to Radiant damage, and your melee attacks deal an extra 2d6 Radiant damage on a hit.\n\nIn addition, immediately after you take damage from a creature you can see within 60 feet of yourself, you can use your Reaction to force the creature to make a Constitution saving throw. On a failed save, the creature has the Blinded condition until the end of your next turn.",
    },
    {
        "name": "Jallarzi's Storm of Radiance",
        "level": 5,
        "school": "Evocation",
        "time": "1 action",
        "range": "120 feet",
        "comp": "V, S, M (a pinch of phosphorus)",
        "dur": "Concentration, up to 1 minute",
        "classes": ["Warlock", "Wizard"],
        "conc": True,
        "desc": "You unleash a storm of flashing light and raging thunder in a 10-foot-radius, 40-foot-high Cylinder centered on a point you can see within range. While in this area, creatures have the Blinded and Deafened conditions. When a creature enters the spell's area for the first time on a turn or starts its turn there, it must make a Constitution saving throw, taking 2d10 Radiant damage and 2d10 Thunder damage on a failed save, or half as much damage on a successful one.",
        "higher": "When you cast this spell using a spell slot of 6th level or higher, the Radiant damage and the Thunder damage each increase by 1d10 for each slot level above 5th.",
    },
    {
        "name": "Power Word Fortify",
        "level": 7,
        "school": "Enchantment",
        "time": "1 action",
        "range": "60 feet",
        "comp": "V",
        "dur": "Instantaneous",
        "classes": ["Bard", "Cleric"],
        "conc": False,
        "desc": "You speak a word of power that fortifies up to six creatures you can see within range. The spell bestows 120 Temporary Hit Points, which you divide among the targets as you choose.",
    },
    {
        "name": "Sorcerous Burst",
        "level": 0,
        "school": "Evocation",
        "time": "1 action",
        "range": "120 feet",
        "comp": "V, S",
        "dur": "Instantaneous",
        "classes": ["Sorcerer"],
        "conc": False,
        "desc": "You cast sorcerous energy at one creature or object within range. Make a ranged spell attack against the target. On a hit, the target takes 1d8 damage of a type you choose: Acid, Cold, Fire, Lightning, Poison, or Thunder.\n\nIf you roll an 8 on any of the d8s for this spell, you can roll an additional d8, and add it to the damage. You can do so only once per turn.\n\nThis spell's damage increases by 1d8 when you reach 5th level (2d8), 11th level (3d8), and 17th level (4d8).",
    },
    {
        "name": "Starry Wisp",
        "level": 0,
        "school": "Evocation",
        "time": "1 action",
        "range": "60 feet",
        "comp": "V, S",
        "dur": "Instantaneous",
        "classes": ["Bard", "Druid"],
        "conc": False,
        "desc": "You launch a mote of light at one creature or object within range. Make a ranged spell attack against the target. On a hit, the target takes 1d8 Radiant damage, and until the end of your next turn, it emits Dim Light in a 10-foot radius and can't benefit from the Invisible condition.\n\nThis spell's damage increases by 1d8 when you reach 5th level (2d8), 11th level (3d8), and 17th level (4d8).",
    },
    {
        "name": "Summon Dragon",
        "level": 5,
        "school": "Conjuration",
        "time": "1 action",
        "range": "60 feet",
        "comp": "V, S, M (an object with the image of a dragon engraved on it, worth at least 500 gp)",
        "dur": "Concentration, up to 1 hour",
        "classes": ["Druid", "Wizard"],
        "conc": True,
        "desc": "You call forth a draconic spirit. It manifests in an unoccupied space that you can see within range. When you cast the spell, choose a family of dragon: Chromatic, Gem, or Metallic. The creature resembles a dragon of the chosen family, which determines certain traits in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.",
        "higher": "When you cast this spell using a spell slot of 6th level or higher, use the higher level wherever the spell's level appears in the stat block.",
    },
    {
        "name": "Tasha's Bubbling Cauldron",
        "level": 6,
        "school": "Conjuration",
        "time": "1 action",
        "range": "5 feet",
        "comp": "V, S, M (a gilded ladle worth 500+ gp)",
        "dur": "10 minutes",
        "classes": ["Warlock", "Wizard"],
        "conc": False,
        "desc": "You conjure a clattering cauldron filled with bubbling liquid. It appears in an unoccupied space on the ground within range and lasts for the duration.\n\nWhen you cast the spell, choose up to three potions from among the common and uncommon potions listed in the Player's Handbook. These potions can be drawn from the cauldron as an action. A creature can draw each potion only once. The potions retain their potency for the duration or until used.",
    },
    {
        "name": "Yolande's Regal Presence",
        "level": 5,
        "school": "Enchantment",
        "time": "1 action",
        "range": "Self",
        "comp": "V, S, M (a miniature tiara)",
        "dur": "Concentration, up to 1 minute",
        "classes": ["Bard", "Wizard"],
        "conc": True,
        "desc": "You surround yourself with unearthly majesty in a 10-foot Emanation. Whenever the Emanation enters the space of a creature you can see and whenever a creature you can see enters the Emanation or ends its turn there, you can force that creature to make a Wisdom saving throw. On a failed save, the target takes 4d6 Psychic damage and has the Prone condition, and you can push the target up to 10 feet away. On a successful save, the target takes half as much damage only. A creature makes this save only once per turn.",
    },
]


def phase_d():
    """Create .md files for 11 brand-new 2024 spells."""
    print("\n" + "=" * 70)
    print("PHASE D: New 2024 Spells")
    print("=" * 70)
    created = 0

    for spell in NEW_SPELLS_2024:
        filepath, content = generate_new_spell(spell)
        if os.path.exists(filepath):
            print(f"  SKIP (exists): {spell['name']}")
            continue
        write_file(filepath, content)
        print(f"  CREATED: {spell['name']} ({spell['school']}/{LEVEL_DIRS[spell['level']]})")
        created += 1

    print(f"\n  Phase D complete: {created} new spells created")
    return created


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"Spell vault: {VAULT_SPELLS}")
    print()

    renamed, moved = phase_a()
    updated = phase_b()
    rewritten, edited = phase_c()
    created = phase_d()

    # Count total spells
    total = 0
    for root, _dirs, files in os.walk(VAULT_SPELLS):
        total += sum(1 for f in files if f.endswith(".md"))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Files renamed:    {renamed}")
    print(f"  Files moved:      {moved}")
    print(f"  Frontmatter updated: {updated}")
    print(f"  Descriptions rewritten: {rewritten}")
    print(f"  Descriptions edited: {edited}")
    print(f"  New spells created: {created}")
    print(f"  Total spell files: {total}")
    print()
    print("Done! Run link_vault.py to re-link the vault.")


if __name__ == "__main__":
    main()
