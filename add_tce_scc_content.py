#!/usr/bin/env python3
"""
Generate Tasha's Cauldron of Everything (TCE) and Strixhaven (SCC) content
that is missing from the vault's reference section.

Creates:
  - 5 Strixhaven spells
  - 4 TCE feats
  - 2 Strixhaven feats
  - 10 Strixhaven items

Total: 21 new .md files (skips any that already exist).
"""

import os
import urllib.parse

VAULT_ROOT = os.path.join("Tenelis", "07 - Reference")
VAULT_SPELLS = os.path.join(VAULT_ROOT, "Spells")
VAULT_FEATS = os.path.join(VAULT_ROOT, "Feats")
VAULT_ITEMS = os.path.join(VAULT_ROOT, "Items")

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

# ---------------------------------------------------------------------------
# Spell data
# ---------------------------------------------------------------------------
SPELLS = [
    {
        "name": "Silvery Barbs",
        "level": 1,
        "school": "Enchantment",
        "time": "1 reaction, which you take when a creature you can see within 60 feet of you succeeds on an attack roll, an ability check, or a saving throw",
        "range": "60 feet",
        "comp": "V",
        "dur": "Instantaneous",
        "classes": ["Bard", "Sorcerer", "Wizard"],
        "ritual": False,
        "conc": False,
        "source": "SCC",
        "desc": (
            "You magically distract the triggering creature and turn its "
            "moment of success into failure. The creature must reroll the d20 "
            "and use the lower roll.\n\n"
            "You can then choose a different creature you can see within range "
            "(you can choose yourself). The chosen creature has advantage on "
            "the next attack roll, ability check, or saving throw it makes "
            "within 1 minute. A creature can be empowered by only one use of "
            "this spell at a time."
        ),
    },
    {
        "name": "Borrowed Knowledge",
        "level": 2,
        "school": "Divination",
        "time": "1 action",
        "range": "Self",
        "comp": "V, S, M (a book worth at least 25 gp)",
        "dur": "1 hour",
        "classes": ["Bard", "Cleric", "Warlock", "Wizard"],
        "ritual": False,
        "conc": False,
        "source": "SCC",
        "desc": (
            "You draw on knowledge from spirits of the past. Choose one skill "
            "in which you lack proficiency. For the spell's duration, you have "
            "proficiency in the chosen skill. The spell ends early if you cast "
            "it again."
        ),
    },
    {
        "name": "Kinetic Jaunt",
        "level": 2,
        "school": "Transmutation",
        "time": "1 bonus action",
        "range": "Self",
        "comp": "S",
        "dur": "Concentration, up to 1 minute",
        "classes": ["Artificer", "Bard", "Sorcerer", "Wizard"],
        "ritual": False,
        "conc": True,
        "source": "SCC",
        "desc": (
            "You magically empower your movement with dance-like steps, "
            "giving yourself the following benefits for the duration:\n\n"
            "- Your walking speed increases by 10 feet.\n"
            "- You don't provoke opportunity attacks.\n"
            "- You can move through the space of another creature. The other "
            "creature's space is not difficult terrain for you, but you can't "
            "willingly end your move in its space."
        ),
    },
    {
        "name": "Vortex Warp",
        "level": 2,
        "school": "Conjuration",
        "time": "1 action",
        "range": "90 feet",
        "comp": "V, S",
        "dur": "Instantaneous",
        "classes": ["Artificer", "Sorcerer", "Wizard"],
        "ritual": False,
        "conc": False,
        "source": "SCC",
        "desc": (
            "You magically twist space around another creature you can see "
            "within range. The target must succeed on a Constitution saving "
            "throw (the target can choose to fail), or the target is "
            "teleported to an unoccupied space of your choice that you can "
            "see within range. The chosen space must be on a surface or in "
            "a liquid that can support the target without the target having "
            "to squeeze."
        ),
        "higher": (
            "When you cast this spell using a spell slot of 3rd level or "
            "higher, the range of the spell increases by 30 feet for each "
            "slot level above 2nd."
        ),
    },
    {
        "name": "Wither and Bloom",
        "level": 2,
        "school": "Necromancy",
        "time": "1 action",
        "range": "60 feet",
        "comp": "V, S, M (a withered vine twisted into a loop)",
        "dur": "Instantaneous",
        "classes": ["Druid", "Sorcerer", "Wizard"],
        "ritual": False,
        "conc": False,
        "source": "SCC",
        "desc": (
            "You invoke both death and life upon a 10-foot-radius sphere "
            "centered on a point within range. Each creature of your choice "
            "in that area must make a Constitution saving throw, taking 2d6 "
            "necrotic damage on a failed save, or half as much damage on a "
            "successful one. Nonmagical vegetation in that area withers.\n\n"
            "In addition, one creature of your choice in that area can spend "
            "and roll one of its unspent Hit Dice and regain a number of hit "
            "points equal to the roll plus your spellcasting ability modifier."
        ),
        "higher": (
            "When you cast this spell using a spell slot of 3rd level or "
            "higher, the damage increases by 1d6 for each slot level above "
            "2nd, and an additional creature in the area can spend and roll "
            "one of its Hit Dice for each slot level above 2nd."
        ),
    },
]

# ---------------------------------------------------------------------------
# Feat data
# ---------------------------------------------------------------------------
FEATS = [
    # TCE feats
    {
        "name": "Eldritch Adept",
        "category": "General",
        "prerequisite": "Spellcasting or Pact Magic feature",
        "source": "TCE",
        "desc": (
            "*General Feat (Prerequisite: Spellcasting or Pact Magic feature)*\n\n"
            "Studying occult lore, you have unlocked eldritch power within "
            "yourself: you learn one Eldritch Invocation option of your choice "
            "from the warlock class. If the invocation has a prerequisite of "
            "any kind, you can choose that invocation only if you're a warlock "
            "who meets the prerequisite.\n\n"
            "Whenever you gain a level, you can replace the invocation with "
            "another one from the warlock class."
        ),
    },
    {
        "name": "Metamagic Adept",
        "category": "General",
        "prerequisite": "Spellcasting or Pact Magic feature",
        "source": "TCE",
        "desc": (
            "*General Feat (Prerequisite: Spellcasting or Pact Magic feature)*\n\n"
            "You've learned how to exert your will on your spells to alter how "
            "they function:\n\n"
            "- You learn two Metamagic options of your choice from the sorcerer "
            "class. You can use only one Metamagic option on a spell when you "
            "cast it, unless the option says otherwise. Whenever you reach a "
            "level that grants the Ability Score Improvement feature, you can "
            "replace one of these Metamagic options with another one from the "
            "sorcerer class.\n"
            "- You gain 2 sorcery points to spend on Metamagic (these points "
            "are added to any sorcery points you have from another source but "
            "can be used only on Metamagic). You regain all spent sorcery "
            "points when you finish a long rest."
        ),
    },
    {
        "name": "Artificer Initiate",
        "category": "General",
        "prerequisite": "None",
        "source": "TCE",
        "desc": (
            "*General Feat*\n\n"
            "You've learned some of an artificer's inventiveness:\n\n"
            "- You learn one cantrip of your choice from the artificer spell "
            "list, and you learn one 1st-level spell of your choice from that "
            "list. Intelligence is your spellcasting ability for these spells.\n"
            "- You can cast this feat's 1st-level spell without a spell slot, "
            "and you must finish a long rest before you can cast it in this "
            "way again. You can also cast the spell using any spell slots you "
            "have.\n"
            "- You gain proficiency with one type of artisan's tools of your "
            "choice, and you can use that type of tool as a spellcasting focus "
            "for any spell you cast that uses Intelligence as its spellcasting "
            "ability."
        ),
    },
    {
        "name": "Gunner",
        "category": "General",
        "prerequisite": "None",
        "source": "TCE",
        "desc": (
            "*General Feat*\n\n"
            "You have a quick hand and keen eye when employing firearms, "
            "granting you the following benefits:\n\n"
            "**Ability Score Increase.** Increase your Dexterity score by 1, "
            "to a maximum of 20.\n\n"
            "**Firearms Proficiency.** You gain proficiency with firearms.\n\n"
            "**Quick Draw.** Being within 5 feet of a hostile creature doesn't "
            "impose disadvantage on your ranged attack rolls."
        ),
    },
    # Strixhaven feats
    {
        "name": "Strixhaven Initiate",
        "category": "General",
        "prerequisite": "None",
        "source": "SCC",
        "desc": (
            "*General Feat*\n\n"
            "You have studied some magical theory and have learned a few "
            "spells associated with Strixhaven University.\n\n"
            "Choose one of Strixhaven's colleges: Lorehold, Prismari, "
            "Quandrix, Silverquill, or Witherbloom. You learn two cantrips "
            "and one 1st-level spell based on the college you choose, as "
            "specified in the Strixhaven Spells table.\n\n"
            "You can cast the chosen 1st-level spell without a spell slot, "
            "and you must finish a long rest before you can cast it in this "
            "way again. You can also cast the spell using any spell slots "
            "you have.\n\n"
            "Your spellcasting ability for these spells is Intelligence, "
            "Wisdom, or Charisma (choose when you select this feat).\n\n"
            "| College | Cantrips | 1st-Level Spell |\n"
            "|---------|----------|-----------------|\n"
            "| Lorehold | [[Light]], [[Sacred Flame]] | [[Comprehend Languages]] |\n"
            "| Prismari | [[Fire Bolt]], [[Prestidigitation]] | [[Chromatic Orb]] |\n"
            "| Quandrix | [[Druidcraft]], [[Guidance]] | [[Guiding Bolt]] |\n"
            "| Silverquill | [[Sacred Flame]], [[Thaumaturgy]] | [[Silvery Barbs]] |\n"
            "| Witherbloom | [[Chill Touch]], [[Spare the Dying]] | [[Cure Wounds]] |"
        ),
    },
    {
        "name": "Strixhaven Mascot",
        "category": "General",
        "prerequisite": "Strixhaven Initiate",
        "source": "SCC",
        "desc": (
            "*General Feat (Prerequisite: Strixhaven Initiate)*\n\n"
            "You have learned how to summon a Strixhaven mascot to assist "
            "you, granting you these benefits:\n\n"
            "**Mascot.** You can cast the [[Find Familiar]] spell as a ritual. "
            "Your familiar can take one of the forms listed in the spell or "
            "one of the following special forms: art elemental mascot "
            "(Prismari), fractal mascot (Quandrix), inkling mascot "
            "(Silverquill), pest mascot (Witherbloom), or spirit statue "
            "mascot (Lorehold).\n\n"
            "**Mascot Shield.** If you see the familiar take damage while "
            "it is within 60 feet of you, you can use your reaction to grant "
            "it resistance against that damage's type."
        ),
    },
]

# ---------------------------------------------------------------------------
# Item data
# ---------------------------------------------------------------------------
ITEMS = [
    {
        "title": "Bottle of Boundless Coffee",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Common",
        "attunement": False,
        "source": "SCC",
        "description": (
            "This bottle comes with a stopper and appears to be empty. "
            "However, while the stopper is removed, you can use an action to "
            "pour a serving of delicious, piping hot coffee from the bottle. "
            "The bottle never runs out of coffee, which is always hot. "
            "A creature that drinks coffee from the bottle has advantage on "
            "saving throws against the exhaustion condition for the next "
            "hour. The coffee loses its magical properties if it isn't "
            "consumed within 1 hour of being poured."
        ),
    },
    {
        "title": "Cuddly Strixhaven Mascot",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Common",
        "attunement": False,
        "source": "SCC",
        "description": (
            "Strixhaven mascots are sold in the university bookstore and "
            "common throughout the campus. They are perfectly ordinary plush "
            "toys that are often used as decorations or travel companions."
        ),
    },
    {
        "title": "Masque Charm",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Common",
        "attunement": False,
        "source": "SCC",
        "description": (
            "A masque charm is a small silver pin. While you are wearing it, "
            "you can use an action to cast the [[Disguise Self]] spell "
            "(DC 13 to discern the disguise). Once the spell is cast, it "
            "can't be cast from the charm again until the next dawn. When "
            "the spell ends, the charm crumbles to dust."
        ),
    },
    {
        "title": "Strixhaven Pennant",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Common",
        "attunement": False,
        "source": "SCC",
        "description": (
            "This pennant bears the symbol of Strixhaven or one of its "
            "colleges: Lorehold, Prismari, Quandrix, Silverquill, or "
            "Witherbloom. While you wave the pennant, you and your allies "
            "within 10 feet of you can add a d4 to an ability check made "
            "to influence or impress others with a display of group spirit "
            "(such as a Charisma (Performance) check). Once this property "
            "is used, it can't be used again until the next dawn."
        ),
    },
    {
        "title": "Lorehold Primer",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Uncommon",
        "attunement": True,
        "source": "SCC",
        "description": (
            "*Requires Attunement by a Spellcaster*\n\n"
            "The Lorehold Primer is a magic textbook created at Strixhaven's "
            "Lorehold College. The primer has 3 charges, and it regains 1d3 "
            "expended charges daily at dawn. If you make an Intelligence "
            "(History) or Intelligence (Religion) check while holding the "
            "primer, you can expend 1 charge to give yourself a 1d4 bonus to "
            "the check, immediately after you roll the d20.\n\n"
            "In addition, if you study the primer during a long rest, you "
            "choose one 1st-level spell from the cleric or wizard spell list. "
            "Before you finish your next long rest, you can cast the chosen "
            "spell once without expending a spell slot. Intelligence is your "
            "spellcasting ability for this spell."
        ),
    },
    {
        "title": "Prismari Primer",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Uncommon",
        "attunement": True,
        "source": "SCC",
        "description": (
            "*Requires Attunement by a Spellcaster*\n\n"
            "The Prismari Primer is a magic textbook created at Strixhaven's "
            "Prismari College. The primer has 3 charges, and it regains 1d3 "
            "expended charges daily at dawn. If you make a Dexterity "
            "(Acrobatics) or Charisma (Performance) check while holding the "
            "primer, you can expend 1 charge to give yourself a 1d4 bonus to "
            "the check, immediately after you roll the d20.\n\n"
            "In addition, if you study the primer during a long rest, you "
            "choose one 1st-level spell from the bard or sorcerer spell list. "
            "Before you finish your next long rest, you can cast the chosen "
            "spell once without expending a spell slot. Charisma is your "
            "spellcasting ability for this spell."
        ),
    },
    {
        "title": "Quandrix Primer",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Uncommon",
        "attunement": True,
        "source": "SCC",
        "description": (
            "*Requires Attunement by a Spellcaster*\n\n"
            "The Quandrix Primer is a magic textbook created at Strixhaven's "
            "Quandrix College. The primer has 3 charges, and it regains 1d3 "
            "expended charges daily at dawn. If you make an Intelligence "
            "(Arcana) or Intelligence (Nature) check while holding the "
            "primer, you can expend 1 charge to give yourself a 1d4 bonus to "
            "the check, immediately after you roll the d20.\n\n"
            "In addition, if you study the primer during a long rest, you "
            "choose one 1st-level spell from the druid or wizard spell list. "
            "Before you finish your next long rest, you can cast the chosen "
            "spell once without expending a spell slot. Intelligence is your "
            "spellcasting ability for this spell."
        ),
    },
    {
        "title": "Silverquill Primer",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Uncommon",
        "attunement": True,
        "source": "SCC",
        "description": (
            "*Requires Attunement by a Spellcaster*\n\n"
            "The Silverquill Primer is a magic textbook created at "
            "Strixhaven's Silverquill College. The primer has 3 charges, and "
            "it regains 1d3 expended charges daily at dawn. If you make a "
            "Charisma (Intimidation) or Charisma (Persuasion) check while "
            "holding the primer, you can expend 1 charge to give yourself a "
            "1d4 bonus to the check, immediately after you roll the d20.\n\n"
            "In addition, if you study the primer during a long rest, you "
            "choose one 1st-level spell from the bard or cleric spell list. "
            "Before you finish your next long rest, you can cast the chosen "
            "spell once without expending a spell slot. Charisma is your "
            "spellcasting ability for this spell."
        ),
    },
    {
        "title": "Witherbloom Primer",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Uncommon",
        "attunement": True,
        "source": "SCC",
        "description": (
            "*Requires Attunement by a Spellcaster*\n\n"
            "The Witherbloom Primer is a magic textbook created at "
            "Strixhaven's Witherbloom College. The primer has 3 charges, and "
            "it regains 1d3 expended charges daily at dawn. If you make an "
            "Intelligence (Nature) or Wisdom (Survival) check while holding "
            "the primer, you can expend 1 charge to give yourself a 1d4 bonus "
            "to the check, immediately after you roll the d20.\n\n"
            "In addition, if you study the primer during a long rest, you "
            "choose one 1st-level spell from the druid or wizard spell list. "
            "Before you finish your next long rest, you can cast the chosen "
            "spell once without expending a spell slot. Wisdom is your "
            "spellcasting ability for this spell."
        ),
    },
    {
        "title": "Murgaxor's Orb",
        "folder": "Wondrous Items",
        "item_type": "Wondrous Item",
        "rarity": "Legendary",
        "attunement": True,
        "source": "SCC",
        "description": (
            "*Requires Attunement*\n\n"
            "This orb of dark, smoky glass is about the size of a human fist "
            "and weighs 5 pounds. It is warm to the touch and pulses with a "
            "faint inner light. The orb has the following properties while "
            "you are attuned to it:\n\n"
            "**Life Drain.** When you make a melee spell attack or a melee "
            "weapon attack, you can choose to deal an extra 2d6 necrotic "
            "damage to the target. You regain hit points equal to the necrotic "
            "damage dealt. Once you use this property, you can't do so again "
            "until the next dawn.\n\n"
            "**Dark Pulse.** You can use an action to cause the orb to emit a "
            "pulse of darkness in a 30-foot-radius sphere centered on the "
            "orb. Each creature in that area must make a DC 18 Constitution "
            "saving throw, taking 4d10 necrotic damage on a failed save, or "
            "half as much damage on a successful one. Undead and constructs "
            "are unaffected. Once you use this property, you can't do so "
            "again until the next dawn."
        ),
    },
]


# ---------------------------------------------------------------------------
# Generation functions
# ---------------------------------------------------------------------------
def generate_spell_file(spell):
    """Generate a single spell .md file and write it to the correct directory."""
    school = spell["school"]
    level = spell["level"]
    level_dir = LEVEL_DIRS[level]
    target_dir = os.path.join(VAULT_SPELLS, school, level_dir)
    os.makedirs(target_dir, exist_ok=True)

    filepath = os.path.join(target_dir, f"{spell['name']}.md")
    if os.path.exists(filepath):
        print(f"  SKIP (exists): {filepath}")
        return False

    classes_yaml = "[" + ", ".join(f'"{c}"' for c in spell["classes"]) + "]"
    encoded_name = urllib.parse.quote(spell["name"].lower(), safe="'-")
    source_lower = spell["source"].lower()
    tools_url = f"https://5e.tools/spells.html#{encoded_name}_{source_lower}"

    lines = [
        "---",
        "tags: [spell, reference]",
        f"spell_level: {level}",
        f'school: "{school}"',
        f'casting_time: "{spell["time"]}"',
        f'range: "{spell["range"]}"',
        f'components: "{spell["comp"]}"',
        f'duration: "{spell["dur"]}"',
        f"classes: {classes_yaml}",
        f"ritual: {'true' if spell['ritual'] else 'false'}",
        f"concentration: {'true' if spell['conc'] else 'false'}",
        f'source: "{spell["source"]}"',
        "---",
        f"# {spell['name']}",
        "",
        spell["desc"],
    ]

    if spell.get("higher"):
        lines.extend(["", "## At Higher Levels", spell["higher"]])

    lines.extend(["", "---", f"\U0001f517 [Full Details on 5e.tools]({tools_url})", ""])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  CREATED: {filepath}")
    return True


def generate_feat_file(feat):
    """Generate a single feat .md file and write it to the correct directory."""
    category = feat["category"]
    target_dir = os.path.join(VAULT_FEATS, category)
    os.makedirs(target_dir, exist_ok=True)

    filepath = os.path.join(target_dir, f"{feat['name']}.md")
    if os.path.exists(filepath):
        print(f"  SKIP (exists): {filepath}")
        return False

    encoded_name = urllib.parse.quote(feat["name"].lower(), safe="'-")
    source_lower = feat["source"].lower()
    tools_url = f"https://5e.tools/feats.html#{encoded_name}_{source_lower}"

    lines = [
        "---",
        "tags: [feat, reference]",
        f'category: "{category}"',
        "level: 4",
        f'prerequisite: "{feat.get("prerequisite", "None")}"',
        f'source: "{feat["source"]}"',
        "---",
        f"# {feat['name']}",
        "",
        feat["desc"],
        "",
        "---",
        f"\U0001f517 [Full Details on 5e.tools]({tools_url})",
        "",
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  CREATED: {filepath}")
    return True


def generate_item_file(item):
    """Generate a single item .md file and write it to the correct directory."""
    folder = item["folder"]
    target_dir = os.path.join(VAULT_ITEMS, folder)
    os.makedirs(target_dir, exist_ok=True)

    filepath = os.path.join(target_dir, f"{item['title']}.md")
    if os.path.exists(filepath):
        print(f"  SKIP (exists): {filepath}")
        return False

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

    name_lower = item["title"].lower()
    source_lower = item["source"].lower()
    encoded = urllib.parse.quote(name_lower, safe="")
    # Match 5e.tools convention: lowercase percent-encoding
    import re
    encoded = re.sub(r"%[0-9A-Fa-f]{2}", lambda m: m.group(0).lower(), encoded)
    url_slug = f"{encoded}_{source_lower}"
    tools_url = f"https://5e.tools/items.html#{url_slug}"

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
        f"\U0001f517 [Full Details on 5e.tools]({tools_url})",
        "",
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  CREATED: {filepath}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    created = 0
    skipped = 0

    print("=== Strixhaven Spells ===")
    for spell in SPELLS:
        if generate_spell_file(spell):
            created += 1
        else:
            skipped += 1

    print("\n=== TCE & Strixhaven Feats ===")
    for feat in FEATS:
        if generate_feat_file(feat):
            created += 1
        else:
            skipped += 1

    print("\n=== Strixhaven Items ===")
    for item in ITEMS:
        if generate_item_file(item):
            created += 1
        else:
            skipped += 1

    print(f"\nDone: {created} created, {skipped} skipped.")


if __name__ == "__main__":
    main()
