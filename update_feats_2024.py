#!/usr/bin/env python3
"""Update the Tenelis feat vault to reflect 2024 PHB changes.

Phase A: Restructure feats into category subdirectories + delete removed feats
Phase B: Frontmatter updates (add category, level; update source, prerequisite)
Phase C: Description rewrites (all 39 continuing feats)
Phase D: New 2024 feats (36 brand-new files)
"""

import os
import shutil
import urllib.parse

VAULT_FEATS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Tenelis", "07 - Reference", "Feats",
)

# ── Category Mappings ─────────────────────────────────────────────────────────

ORIGIN_FEATS = [
    "Alert", "Healer", "Lucky", "Magic Initiate", "Savage Attacker",
    "Skilled", "Tavern Brawler", "Tough",
]

GENERAL_FEATS = [
    "Actor", "Athlete", "Charger", "Crossbow Expert", "Defensive Duelist",
    "Dual Wielder", "Dungeon Delver", "Durable", "Elemental Adept",
    "Grappler", "Great Weapon Master", "Heavily Armored", "Heavy Armor Master",
    "Inspiring Leader", "Keen Mind", "Lightly Armored", "Mage Slayer",
    "Medium Armor Master", "Moderately Armored", "Mounted Combatant",
    "Observant", "Polearm Master", "Resilient", "Ritual Caster", "Sentinel",
    "Sharpshooter", "Shield Master", "Skulker", "Spell Sniper", "War Caster",
    "Weapon Master",
]

REMOVED_FEATS = ["Linguist", "Martial Adept", "Mobile"]

# Category -> level mapping
CATEGORY_LEVEL = {
    "Origin": 1,
    "General": 4,
    "Fighting Style": 4,
    "Epic Boon": 19,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

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
            if isinstance(value, int):
                new_val = str(value)
            else:
                new_val = f'"{value}"'
            new_line = f"{field}: {new_val}"
            if fm_lines[i] != new_line:
                fm_lines[i] = new_line
                return True
            return False
    return False


def add_fm_field(fm_lines, field, value, after=None):
    """Add a new frontmatter field. Insert after `after` field if given, else append."""
    if isinstance(value, int):
        new_val = str(value)
    else:
        new_val = f'"{value}"'
    new_line = f"{field}: {new_val}"

    # Check if field already exists
    for line in fm_lines:
        if line.startswith(f"{field}:"):
            return False  # already exists

    if after:
        for i, line in enumerate(fm_lines):
            if line.startswith(f"{after}:"):
                fm_lines.insert(i + 1, new_line)
                return True

    # Append before source if possible, else at end
    for i, line in enumerate(fm_lines):
        if line.startswith("source:"):
            fm_lines.insert(i, new_line)
            return True

    fm_lines.append(new_line)
    return True


def get_fm_field(fm_lines, field):
    """Get a frontmatter field value as raw string."""
    for line in fm_lines:
        if line.startswith(f"{field}:"):
            return line[len(field) + 1:].strip()
    return None


def update_description(body, new_desc):
    """Replace the description in the body (between # Title and --- footer)."""
    lines = body.split("\n")

    title_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title_idx = i
            break

    if title_idx is None:
        return body

    footer_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i] == "---":
            footer_idx = i
            break

    if footer_idx is None:
        return body

    new_lines = lines[:title_idx + 1]
    new_lines.append("")
    new_lines.append(new_desc)
    new_lines.append("")
    new_lines.extend(lines[footer_idx:])

    return "\n".join(new_lines)


def update_tools_link(body, feat_name, source="2024"):
    """Update the 5e.tools link in the footer."""
    import re
    encoded = urllib.parse.quote(feat_name.lower(), safe="'-")
    new_url = f"https://5e.tools/feats.html#{encoded}_{source.lower()}"
    return re.sub(
        r"🔗 \[Full Details on 5e\.tools\]\([^)]+\)",
        f"🔗 [Full Details on 5e.tools]({new_url})",
        body,
    )


def generate_new_feat(feat):
    """Generate a brand-new feat .md file. Returns (path, content)."""
    category = feat["category"]
    target_dir = os.path.join(VAULT_FEATS, category)
    filepath = os.path.join(target_dir, f"{feat['name']}.md")

    encoded_name = urllib.parse.quote(feat["name"].lower(), safe="'-")
    tools_url = f"https://5e.tools/feats.html#{encoded_name}_2024"

    lines = [
        "---",
        "tags: [feat, reference]",
        f'category: "{category}"',
        f"level: {CATEGORY_LEVEL[category]}",
        f'prerequisite: "{feat.get("prerequisite", "None")}"',
        'source: "2024"',
        "---",
        f"# {feat['name']}",
        "",
        feat["desc"],
        "",
        "---",
        f"\U0001f517 [Full Details on 5e.tools]({tools_url})",
        "",
    ]

    return filepath, "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE A: Restructure into Category Subdirectories
# ══════════════════════════════════════════════════════════════════════════════

def phase_a():
    """Move feats into category subdirectories, delete removed feats."""
    print("=" * 70)
    print("PHASE A: Restructure into Category Subdirectories")
    print("=" * 70)
    moved = 0
    deleted = 0

    # Create subdirectories
    for subdir in ["Origin", "General", "Fighting Style", "Epic Boon"]:
        os.makedirs(os.path.join(VAULT_FEATS, subdir), exist_ok=True)

    # Move Origin feats
    for name in ORIGIN_FEATS:
        src = os.path.join(VAULT_FEATS, f"{name}.md")
        dst = os.path.join(VAULT_FEATS, "Origin", f"{name}.md")
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.move(src, dst)
            print(f"  MOVED: {name} -> Origin/")
            moved += 1
        elif os.path.exists(dst):
            print(f"  SKIP (already moved): {name}")
        else:
            print(f"  WARN: {name} not found!")

    # Move General feats
    for name in GENERAL_FEATS:
        src = os.path.join(VAULT_FEATS, f"{name}.md")
        dst = os.path.join(VAULT_FEATS, "General", f"{name}.md")
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.move(src, dst)
            print(f"  MOVED: {name} -> General/")
            moved += 1
        elif os.path.exists(dst):
            print(f"  SKIP (already moved): {name}")
        else:
            print(f"  WARN: {name} not found!")

    # Delete removed feats
    for name in REMOVED_FEATS:
        path = os.path.join(VAULT_FEATS, f"{name}.md")
        if os.path.exists(path):
            os.remove(path)
            print(f"  DELETED: {name}")
            deleted += 1
        else:
            print(f"  SKIP (already deleted): {name}")

    print(f"\n  Phase A complete: {moved} moved, {deleted} deleted")
    return moved, deleted


# ══════════════════════════════════════════════════════════════════════════════
# PHASE B: Frontmatter Updates
# ══════════════════════════════════════════════════════════════════════════════

# Prerequisite updates for 2024 versions
PREREQUISITE_UPDATES = {
    # Origin feats — no prerequisites
    "Alert": "None",
    "Healer": "None",
    "Lucky": "None",
    "Magic Initiate": "None",
    "Savage Attacker": "None",
    "Skilled": "None",
    "Tavern Brawler": "None",
    "Tough": "None",
    # General feats — some have prerequisites
    "Actor": "Charisma 13+",
    "Athlete": "Strength, Dexterity, or Constitution 13+",
    "Charger": "Strength or Dexterity 13+",
    "Crossbow Expert": "Dexterity 13+",
    "Defensive Duelist": "Dexterity 13+",
    "Dual Wielder": "Strength or Dexterity 13+",
    "Dungeon Delver": "Intelligence or Wisdom 13+",
    "Durable": "Constitution 13+",
    "Elemental Adept": "Spellcasting or Pact Magic feature",
    "Grappler": "Strength or Dexterity 13+",
    "Great Weapon Master": "Strength 13+",
    "Heavily Armored": "Medium Armor proficiency",
    "Heavy Armor Master": "Heavy Armor proficiency",
    "Inspiring Leader": "Charisma 13+",
    "Keen Mind": "Intelligence 13+",
    "Lightly Armored": "None",
    "Mage Slayer": "None",
    "Medium Armor Master": "Medium Armor proficiency",
    "Moderately Armored": "Light Armor proficiency",
    "Mounted Combatant": "None",
    "Observant": "Intelligence or Wisdom 13+",
    "Polearm Master": "Strength or Dexterity 13+",
    "Resilient": "None",
    "Ritual Caster": "Intelligence, Wisdom, or Charisma 13+",
    "Sentinel": "Strength or Dexterity 13+",
    "Sharpshooter": "Dexterity 13+",
    "Shield Master": "Shield proficiency",
    "Skulker": "Dexterity 13+",
    "Spell Sniper": "Spellcasting or Pact Magic feature",
    "War Caster": "Spellcasting or Pact Magic feature",
    "Weapon Master": "Strength or Dexterity 13+",
}


def phase_b():
    """Update frontmatter on all feat files: add category, level; update source."""
    print("\n" + "=" * 70)
    print("PHASE B: Frontmatter Updates")
    print("=" * 70)
    updated = 0

    for root, _dirs, files in os.walk(VAULT_FEATS):
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            name = fname[:-3]
            path = os.path.join(root, fname)

            # Determine category from parent directory
            parent = os.path.basename(root)
            if parent in ("Origin", "General", "Fighting Style", "Epic Boon"):
                category = parent
            else:
                continue  # skip files not yet in a category subdir

            content = read_file(path)
            fm_lines, body = split_frontmatter(content)
            if not fm_lines:
                continue

            changed = False
            level = CATEGORY_LEVEL[category]

            # Add category field (after tags)
            if add_fm_field(fm_lines, "category", category, after="tags"):
                changed = True

            # Add level field (after category)
            if add_fm_field(fm_lines, "level", level, after="category"):
                changed = True

            # Update prerequisite if changed
            if name in PREREQUISITE_UPDATES:
                if update_fm_field(fm_lines, "prerequisite", PREREQUISITE_UPDATES[name]):
                    changed = True

            # Update source to "2024"
            if update_fm_field(fm_lines, "source", "2024"):
                changed = True

            if changed:
                new_content = rebuild_file(fm_lines, body)
                write_file(path, new_content)
                updated += 1
                print(f"  UPDATED: {name}")

    print(f"\n  Phase B complete: {updated} files updated")
    return updated


# ══════════════════════════════════════════════════════════════════════════════
# PHASE C: Description Rewrites (all 39 continuing feats)
# ══════════════════════════════════════════════════════════════════════════════

DESCRIPTION_REWRITES = {
    # ── Origin Feats ──────────────────────────────────────────────────────────
    "Alert": (
        "*Origin Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Initiative Proficiency.** When you roll Initiative, you can add your Proficiency Bonus to the roll.\n\n"
        "**Initiative Swap.** Immediately after you roll Initiative, you can swap your Initiative with one willing ally in the same combat. You can't make this swap if you or the ally has the Incapacitated condition."
    ),
    "Healer": (
        "*Origin Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Battle Medic.** If you have a Healer's Kit, you can expend one use of it and tend to a creature within 5 feet of yourself as a Utilize action. That creature can expend one of its Hit Point Dice, and you then roll that die. The creature regains a number of Hit Points equal to the roll plus your Proficiency Bonus.\n\n"
        "**Healing Rerolls.** Whenever you roll a die to determine the number of Hit Points you restore with a spell or with this feat's Battle Medic benefit, you can reroll the die if it rolls a 1, and you must use the new roll."
    ),
    "Lucky": (
        "*Origin Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Luck Points.** You have a number of Luck Points equal to your Proficiency Bonus and can spend the points on the benefits below. You regain your expended Luck Points when you finish a Long Rest.\n\n"
        "**Advantage.** When you roll a d20 for a D20 Test, you can spend 1 Luck Point to give yourself Advantage on the roll.\n\n"
        "**Disadvantage.** When a creature rolls a d20 for an attack roll against you, you can spend 1 Luck Point to impose Disadvantage on that roll."
    ),
    "Magic Initiate": (
        "*Origin Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Two Cantrips.** You learn two cantrips of your choice from the Cleric, Druid, or Wizard spell list. Intelligence, Wisdom, or Charisma is your spellcasting ability for this feat's spells (choose when you select this feat).\n\n"
        "**Level 1 Spell.** Choose a level 1 spell from the same list you selected for the cantrips. You always have that spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast the spell using any spell slots you have.\n\n"
        "**Spell Change.** Whenever you gain a new level, you can replace one of the spells you chose for this feat with a different spell of the same level from the chosen spell list."
    ),
    "Savage Attacker": (
        "*Origin Feat*\n\n"
        "You've trained to deal particularly damaging strikes. Once per turn when you hit a target with a weapon, you can roll the weapon's damage dice twice and use either roll against the target."
    ),
    "Skilled": (
        "*Origin Feat*\n\n"
        "You gain proficiency in any combination of three skills or tools of your choice."
    ),
    "Tavern Brawler": (
        "*Origin Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Enhanced Unarmed Strike.** When you hit with your Unarmed Strike and deal damage, you can deal Bludgeoning damage equal to 1d4 plus your Strength modifier instead of the normal damage of an Unarmed Strike.\n\n"
        "**Damage Rerolls.** Whenever you roll a damage die for your Unarmed Strike, you can reroll the die if it rolls a 1, and you must use the new roll.\n\n"
        "**Shove.** When you hit a creature with an Unarmed Strike as part of the Attack action on your turn, you can deal damage to the target and also push it 5 feet away from you. You can use this benefit only once per turn.\n\n"
        "**Furniture as Weapons.** You can wield furniture as a Weapon, using the statistics of a Club for Small furniture or a Greatclub for Medium or larger furniture."
    ),
    "Tough": (
        "*Origin Feat*\n\n"
        "Your Hit Point maximum increases by an amount equal to twice your character level when you gain this feat. Whenever you gain a level thereafter, your Hit Point maximum increases by an additional 2 Hit Points."
    ),

    # ── General Feats ─────────────────────────────────────────────────────────
    "Actor": (
        "*General Feat (Prerequisite: Charisma 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Charisma score by 1, to a maximum of 20.\n\n"
        "**Impersonation.** While you're disguised as a fictional person or a real person other than yourself, you have Advantage on Charisma (Deception) checks to convince others that you are that person.\n\n"
        "**Mimicry.** You can mimic the sounds of other creatures, including speech. A creature that hears the sounds can tell they are imitations with a successful Wisdom (Insight) check against your Charisma (Deception) check."
    ),
    "Athlete": (
        "*General Feat (Prerequisite: Strength, Dexterity, or Constitution 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength, Dexterity, or Constitution score by 1, to a maximum of 20.\n\n"
        "**Climb Speed.** You gain a Climb Speed equal to your Speed.\n\n"
        "**Hop Up.** When you have the Prone condition, you can right yourself with only 5 feet of movement.\n\n"
        "**Jumping.** Your jump distances are determined by your Strength or Dexterity score (your choice) instead of only Strength."
    ),
    "Charger": (
        "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Improved Dash.** When you take the Dash action, your Speed increases by 10 feet for that action.\n\n"
        "**Charge Attack.** If you move at least 10 feet in a straight line toward a target immediately before hitting it with a melee attack as part of the Attack action, choose one of the following effects: gain a +1d8 bonus to the attack's damage roll, or push the target up to 10 feet away if it is Large or smaller. You can use this benefit only once on each of your turns."
    ),
    "Crossbow Expert": (
        "*General Feat (Prerequisite: Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Dexterity score by 1, to a maximum of 20.\n\n"
        "**Ignore Loading.** You ignore the Loading property of crossbows.\n\n"
        "**Firing in Melee.** Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with crossbows.\n\n"
        "**Dual Wielding.** When you make the extra attack of the Light weapon property, you can add your ability modifier to the damage of that attack if the extra attack is made with a crossbow that has the Light property."
    ),
    "Defensive Duelist": (
        "*General Feat (Prerequisite: Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Dexterity score by 1, to a maximum of 20.\n\n"
        "**Parry.** If you're holding a Finesse weapon and another creature hits you with a melee attack, you can take a Reaction to add your Proficiency Bonus to your Armor Class, potentially causing the attack to miss you. You gain this bonus to your AC against melee attacks until the start of your next turn."
    ),
    "Dual Wielder": (
        "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Enhanced Dual Wielding.** When you take the Attack action on your turn and attack with a weapon that has the Light property, you can make one extra attack as a Bonus Action later on the same turn with a different weapon, which must be a Melee weapon that lacks the Two-Handed property. You don't add your ability modifier to the extra attack's damage unless that modifier is negative.\n\n"
        "**Quick Draw.** You can draw or stow two weapons that lack the Two-Handed property when you would normally be able to draw or stow only one."
    ),
    "Dungeon Delver": (
        "*General Feat (Prerequisite: Intelligence or Wisdom 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Intelligence or Wisdom score by 1, to a maximum of 20.\n\n"
        "**Trap Finder.** You have Advantage on saving throws made to avoid or resist traps, and you have Resistance to the damage dealt by traps.\n\n"
        "**Perceptive.** You have Advantage on Wisdom (Perception) checks made to detect the presence of secret doors.\n\n"
        "**Dungeon Sense.** You can use a Bonus Action to sense the presence of traps within 30 feet of yourself for the rest of the current turn. When you sense a trap in this way, you don't learn the specific nature or location of the trap."
    ),
    "Durable": (
        "*General Feat (Prerequisite: Constitution 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Constitution score by 1, to a maximum of 20.\n\n"
        "**Defy Death.** You have Advantage on Death Saving Throws.\n\n"
        "**Speedy Recovery.** As a Bonus Action, you can expend one of your Hit Point Dice, roll the die, and regain a number of Hit Points equal to the roll."
    ),
    "Elemental Adept": (
        "*General Feat (Prerequisite: Spellcasting or Pact Magic feature)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
        "**Energy Mastery.** Choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. Spells you cast ignore Resistance to damage of the chosen type. In addition, when you roll damage for a spell you cast that deals damage of that type, you can treat any 1 on a damage die as a 2.\n\n"
        "**Repeatable.** You can take this feat more than once, choosing a different damage type each time."
    ),
    "Grappler": (
        "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Punch and Grab.** When you hit a creature with an Unarmed Strike as part of the Attack action on your turn, you can use both the Damage and the Grapple option. You can use this benefit only once per turn.\n\n"
        "**Attack Advantage.** You have Advantage on attack rolls against a creature Grappled by you.\n\n"
        "**Fast Wrestler.** Your Speed isn't halved when you move a creature Grappled by you if the creature is your size or smaller."
    ),
    "Great Weapon Master": (
        "*General Feat (Prerequisite: Strength 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength score by 1, to a maximum of 20.\n\n"
        "**Cleave.** Immediately after you score a Critical Hit with a Melee weapon or reduce a creature to 0 Hit Points with one, you can make one attack with the same weapon as a Bonus Action.\n\n"
        "**Heavy Weapon Mastery.** When you hit a creature with a Heavy weapon as part of the Attack action on your turn, you can cause the weapon to deal extra damage to the target. The extra damage equals your Proficiency Bonus."
    ),
    "Heavily Armored": (
        "*General Feat (Prerequisite: Medium Armor proficiency)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Constitution or Strength score by 1, to a maximum of 20.\n\n"
        "**Armor Training.** You gain proficiency with Heavy armor."
    ),
    "Heavy Armor Master": (
        "*General Feat (Prerequisite: Heavy Armor proficiency)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Constitution or Strength score by 1, to a maximum of 20.\n\n"
        "**Damage Reduction.** When you're hit by an attack while you're wearing Heavy armor, any Bludgeoning, Piercing, or Slashing damage dealt to you by that attack is reduced by an amount equal to your Proficiency Bonus."
    ),
    "Inspiring Leader": (
        "*General Feat (Prerequisite: Charisma 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Charisma score by 1, to a maximum of 20.\n\n"
        "**Encouraging Performance.** At the end of a Short or Long Rest, you can give an inspiring performance: a speech, a song, or a dance. When you do so, choose up to six friendly creatures (which can include yourself) within 30 feet of yourself who witness the performance. The chosen creatures each gain Temporary Hit Points equal to your character level plus your Charisma modifier."
    ),
    "Keen Mind": (
        "*General Feat (Prerequisite: Intelligence 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Intelligence score by 1, to a maximum of 20.\n\n"
        "**Lore Knowledge.** Choose one of the following skills: Arcana, History, Investigation, Nature, or Religion. If you lack proficiency in the chosen skill, you gain proficiency in it, and if you already have proficiency in it, you gain Expertise in it.\n\n"
        "**Quick Study.** You can take the Study action as a Bonus Action."
    ),
    "Lightly Armored": (
        "*General Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Armor Training.** You gain proficiency with Light armor and Shields."
    ),
    "Mage Slayer": (
        "*General Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Concentration Breaker.** When you damage a creature that is concentrating, it has Disadvantage on the saving throw it makes to maintain Concentration.\n\n"
        "**Guarded Mind.** If you fail an Intelligence, Wisdom, or Charisma saving throw, you can cause yourself to succeed instead. Once you use this benefit, you can't use it again until you finish a Short or Long Rest."
    ),
    "Medium Armor Master": (
        "*General Feat (Prerequisite: Medium Armor proficiency)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Dexterous Wearer.** While you're wearing Medium armor, you can add 3, rather than 2, to your AC if you have a Dexterity of 16 or higher. In addition, wearing Medium armor doesn't impose Disadvantage on your Dexterity (Stealth) checks."
    ),
    "Moderately Armored": (
        "*General Feat (Prerequisite: Light Armor proficiency)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Armor Training.** You gain proficiency with Medium armor and Shields."
    ),
    "Mounted Combatant": (
        "*General Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength, Dexterity, or Wisdom score by 1, to a maximum of 20.\n\n"
        "**Mounted Strike.** While mounted, you have Advantage on attack rolls against any unmounted creature whose size is smaller than your mount.\n\n"
        "**Leap Aside.** If your mount is subjected to an effect that allows it to make a Dexterity saving throw, you can use your Reaction to grant your mount a bonus to the save equal to your Proficiency Bonus.\n\n"
        "**Veer.** While mounted, you can force any attack directed at your mount to target you instead."
    ),
    "Observant": (
        "*General Feat (Prerequisite: Intelligence or Wisdom 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Intelligence or Wisdom score by 1, to a maximum of 20.\n\n"
        "**Keen Observer.** Choose one of the following skills: Insight, Investigation, or Perception. If you lack proficiency in the chosen skill, you gain proficiency in it, and if you already have proficiency in it, you gain Expertise in it.\n\n"
        "**Quick Search.** You can take the Search action as a Bonus Action."
    ),
    "Polearm Master": (
        "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength score by 1, to a maximum of 20.\n\n"
        "**Bonus Attack.** When you take the Attack action and attack with a Quarterstaff, a Spear, or a weapon that has the Heavy and Reach properties, you can make one extra attack as a Bonus Action with the opposite end of the weapon. The weapon deals 1d4 Bludgeoning damage on a hit.\n\n"
        "**Reactive Strike.** While you're holding a weapon that has the Heavy and Reach properties, you can take a Reaction to make one melee attack against a creature that enters the reach you have with that weapon."
    ),
    "Resilient": (
        "*General Feat*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 20.\n\n"
        "**Saving Throw Proficiency.** You gain proficiency in saving throws using the ability you chose."
    ),
    "Ritual Caster": (
        "*General Feat (Prerequisite: Intelligence, Wisdom, or Charisma 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
        "**Ritual Spells.** Choose two level 1 spells that have the Ritual tag from the Cleric, Druid, or Wizard spell list. You always have those two spells prepared, and you can cast them with any spell slots you have. The spells' spellcasting ability is the ability increased by this feat. Whenever you gain a new level, you can replace one of the ritual spells with another eligible spell of the same level from the same spell list.\n\n"
        "**Quick Ritual.** With this feat, you can cast a Ritual spell in its normal casting time rather than adding 10 minutes to it."
    ),
    "Sentinel": (
        "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Guardian.** Immediately after a creature within 5 feet of you takes the Disengage action or hits a target other than you with an attack, you can make an Opportunity Attack against that creature.\n\n"
        "**Halt.** When you hit a creature with an Opportunity Attack, the creature's Speed becomes 0 for the rest of the current turn."
    ),
    "Sharpshooter": (
        "*General Feat (Prerequisite: Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Dexterity score by 1, to a maximum of 20.\n\n"
        "**Bypass Cover.** Your ranged attacks with weapons ignore Half Cover and Three-Quarters Cover.\n\n"
        "**Firing in Melee.** Being within 5 feet of an enemy doesn't impose Disadvantage on your ranged attack rolls with weapons.\n\n"
        "**Long-Range Shooting.** Attacking at long range doesn't impose Disadvantage on your ranged attack rolls with weapons."
    ),
    "Shield Master": (
        "*General Feat (Prerequisite: Shield proficiency)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength score by 1, to a maximum of 20.\n\n"
        "**Shield Bash.** If you attack a creature within 5 feet of you as part of the Attack action and hit with a Melee weapon, you can immediately make a Shove using your Shield against that creature as a Bonus Action. You can use this benefit only once on each of your turns.\n\n"
        "**Interpose Shield.** If you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you can take a Reaction to take no damage if you succeed on the saving throw, interposing your Shield between yourself and the source of the effect."
    ),
    "Skulker": (
        "*General Feat (Prerequisite: Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Dexterity score by 1, to a maximum of 20.\n\n"
        "**Blindsight.** You have Blindsight with a range of 10 feet.\n\n"
        "**Fog of War.** You exploit the distractions of battle, gaining Advantage on any Dexterity (Stealth) check you make as part of the Hide action during combat.\n\n"
        "**Sniper.** If you make an attack roll while hidden and the roll misses, making the attack roll doesn't reveal your location."
    ),
    "Spell Sniper": (
        "*General Feat (Prerequisite: Spellcasting or Pact Magic feature)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
        "**Bypass Cover.** Your attack rolls for spells ignore Half Cover and Three-Quarters Cover.\n\n"
        "**Casting in Melee.** Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with spells.\n\n"
        "**Increased Range.** When you cast a spell that has a range of at least 10 feet and requires you to make an attack roll, you can increase the spell's range by 60 feet."
    ),
    "War Caster": (
        "*General Feat (Prerequisite: Spellcasting or Pact Magic feature)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
        "**Concentration.** You have Advantage on Constitution saving throws that you make to maintain Concentration.\n\n"
        "**Reactive Spell.** When a creature provokes an Opportunity Attack from you by leaving your reach, you can take a Reaction to cast a spell at the creature rather than making an Opportunity Attack. The spell must have a casting time of one action and must target only that creature.\n\n"
        "**Somatic Components.** You can perform the Somatic components of spells even when you have weapons or a Shield in one or both hands."
    ),
    "Weapon Master": (
        "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
        "You gain the following benefits.\n\n"
        "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
        "**Mastery Property.** Your training with weapons allows you to use the mastery property of two kinds of Simple or Martial weapons of your choice. Whenever you finish a Long Rest, you can change the kinds of weapons you chose."
    ),
}


def phase_c():
    """Rewrite descriptions for all 39 continuing feats."""
    print("\n" + "=" * 70)
    print("PHASE C: Description Rewrites")
    print("=" * 70)
    rewritten = 0

    for root, _dirs, files in os.walk(VAULT_FEATS):
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            name = fname[:-3]
            if name not in DESCRIPTION_REWRITES:
                continue

            path = os.path.join(root, fname)
            content = read_file(path)
            fm_lines, body = split_frontmatter(content)

            body = update_description(body, DESCRIPTION_REWRITES[name])
            body = update_tools_link(body, name, "2024")

            new_content = rebuild_file(fm_lines, body)
            if new_content != content:
                write_file(path, new_content)
                print(f"  REWRITE: {name}")
                rewritten += 1

    print(f"\n  Phase C complete: {rewritten} feats rewritten")
    return rewritten


# ══════════════════════════════════════════════════════════════════════════════
# PHASE D: New 2024 Feats (36 brand-new files)
# ══════════════════════════════════════════════════════════════════════════════

NEW_FEATS_2024 = [
    # ── Origin (2 new) ────────────────────────────────────────────────────────
    {
        "name": "Crafter",
        "category": "Origin",
        "desc": (
            "*Origin Feat*\n\n"
            "You gain the following benefits.\n\n"
            "**Tool Proficiency.** You gain proficiency with three different Artisan's Tools of your choice.\n\n"
            "**Discount.** Whenever you buy a nonmagical item, you receive a 20 percent discount on it.\n\n"
            "**Faster Crafting.** When you craft an item using a tool with which you have proficiency, the required crafting time is reduced by 20 percent."
        ),
    },
    {
        "name": "Musician",
        "category": "Origin",
        "desc": (
            "*Origin Feat*\n\n"
            "You gain the following benefits.\n\n"
            "**Instrument Training.** You gain proficiency with three Musical Instruments of your choice.\n\n"
            "**Inspiring Song.** As you finish a Short or Long Rest, you can play a song on a Musical Instrument with which you have proficiency and give Inspiration to allies who hear the song. The number of allies you can affect in this way equals your Proficiency Bonus."
        ),
    },

    # ── General (12 new) ──────────────────────────────────────────────────────
    {
        "name": "Chef",
        "category": "General",
        "prerequisite": "Constitution or Wisdom 13+",
        "desc": (
            "*General Feat (Prerequisite: Constitution or Wisdom 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Constitution or Wisdom score by 1, to a maximum of 20.\n\n"
            "**Cook's Utensils.** You gain proficiency with Cook's Utensils if you don't already have it.\n\n"
            "**Replenishing Meal.** As part of a Short Rest, you can cook special food if you have Cook's Utensils and ingredients on hand. You can prepare enough for a number of creatures equal to 4 + your Proficiency Bonus. At the end of the Short Rest, any creature who eats the food regains an extra 1d8 Hit Points.\n\n"
            "**Bolstering Treats.** With 1 hour of work or when you finish a Long Rest, you can cook a number of treats equal to your Proficiency Bonus if you have Cook's Utensils on hand. These special treats last 8 hours after being made. A creature can eat one of these treats as a Bonus Action, gaining Temporary Hit Points equal to your Proficiency Bonus."
        ),
    },
    {
        "name": "Crusher",
        "category": "General",
        "prerequisite": "Strength or Constitution 13+",
        "desc": (
            "*General Feat (Prerequisite: Strength or Constitution 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Strength or Constitution score by 1, to a maximum of 20.\n\n"
            "**Push.** Once per turn, when you hit a creature with an attack that deals Bludgeoning damage, you can move it 5 feet to an unoccupied space if the target is no more than one size larger than you.\n\n"
            "**Enhanced Critical.** When you score a Critical Hit that deals Bludgeoning damage to a creature, attack rolls against that creature have Advantage until the start of your next turn."
        ),
    },
    {
        "name": "Fey Touched",
        "category": "General",
        "prerequisite": "Intelligence, Wisdom, or Charisma 13+",
        "desc": (
            "*General Feat (Prerequisite: Intelligence, Wisdom, or Charisma 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
            "**Fey Magic.** You learn the Misty Step spell and one level 1 spell of your choice. The level 1 spell must be from the Divination or Enchantment school of magic. You always have these spells prepared. You can cast each of these spells without expending a spell slot. Once you cast either of these spells in this way, you can't cast that spell in this way again until you finish a Long Rest. You can also cast these spells using spell slots you have of the appropriate level. The spells' spellcasting ability is the ability increased by this feat."
        ),
    },
    {
        "name": "Fighting Initiate",
        "category": "General",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*General Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
            "**Fighting Style.** You learn one Fighting Style feat of your choice. Whenever you reach a level that grants the Ability Score Increase feature, you can replace this feat's fighting style with another one."
        ),
    },
    {
        "name": "Piercer",
        "category": "General",
        "prerequisite": "Strength or Dexterity 13+",
        "desc": (
            "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
            "**Puncture.** Once per turn, when you hit a creature with an attack that deals Piercing damage, you can reroll one of the attack's damage dice, and you must use the new roll.\n\n"
            "**Enhanced Critical.** When you score a Critical Hit that deals Piercing damage to a creature, you can roll one additional damage die when determining the extra Piercing damage the target takes."
        ),
    },
    {
        "name": "Poisoner",
        "category": "General",
        "prerequisite": "Dexterity or Intelligence 13+",
        "desc": (
            "*General Feat (Prerequisite: Dexterity or Intelligence 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Dexterity or Intelligence score by 1, to a maximum of 20.\n\n"
            "**Potent Poison.** When you make a damage roll that deals Poison damage, it ignores Resistance to Poison damage.\n\n"
            "**Brew Poison.** You gain proficiency with the Poisoner's Kit. With 1 hour of work using a Poisoner's Kit and expending 50 GP worth of materials, you can create a number of poison doses equal to your Proficiency Bonus. As a Bonus Action, you can apply a poison dose to a weapon or piece of ammunition. Once applied, the poison retains its potency for 1 minute or until you hit with the weapon or ammunition. When a creature takes damage from the poisoned weapon or ammunition, that creature must succeed on a Constitution saving throw (DC 8 + the ability modifier increased by this feat + your Proficiency Bonus) or take 2d8 Poison damage and have the Poisoned condition until the end of your next turn."
        ),
    },
    {
        "name": "Shadow Touched",
        "category": "General",
        "prerequisite": "Intelligence, Wisdom, or Charisma 13+",
        "desc": (
            "*General Feat (Prerequisite: Intelligence, Wisdom, or Charisma 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
            "**Shadow Magic.** You learn the Invisibility spell and one level 1 spell of your choice. The level 1 spell must be from the Illusion or Necromancy school of magic. You always have these spells prepared. You can cast each of these spells without expending a spell slot. Once you cast either of these spells in this way, you can't cast that spell in this way again until you finish a Long Rest. You can also cast these spells using spell slots you have of the appropriate level. The spells' spellcasting ability is the ability increased by this feat."
        ),
    },
    {
        "name": "Skill Expert",
        "category": "General",
        "prerequisite": "None",
        "desc": (
            "*General Feat*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 20.\n\n"
            "**Skill Proficiency.** You gain proficiency in one skill of your choice.\n\n"
            "**Expertise.** Choose one skill in which you have proficiency. You gain Expertise in that skill."
        ),
    },
    {
        "name": "Slasher",
        "category": "General",
        "prerequisite": "Strength or Dexterity 13+",
        "desc": (
            "*General Feat (Prerequisite: Strength or Dexterity 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 20.\n\n"
            "**Hamstring.** Once per turn, when you hit a creature with an attack that deals Slashing damage, you can reduce the Speed of the target by 10 feet until the start of your next turn.\n\n"
            "**Enhanced Critical.** When you score a Critical Hit that deals Slashing damage to a creature, the target has Disadvantage on all attack rolls until the start of your next turn."
        ),
    },
    {
        "name": "Speedy",
        "category": "General",
        "prerequisite": "Dexterity or Constitution 13+",
        "desc": (
            "*General Feat (Prerequisite: Dexterity or Constitution 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Dexterity or Constitution score by 1, to a maximum of 20.\n\n"
            "**Speed Increase.** Your Speed increases by 10 feet.\n\n"
            "**Dash Over Difficult Terrain.** When you take the Dash action on your turn, Difficult Terrain doesn't cost you extra movement for the rest of that turn.\n\n"
            "**Agile Movement.** Opportunity Attacks have Disadvantage against you."
        ),
    },
    {
        "name": "Telekinetic",
        "category": "General",
        "prerequisite": "Intelligence, Wisdom, or Charisma 13+",
        "desc": (
            "*General Feat (Prerequisite: Intelligence, Wisdom, or Charisma 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
            "**Minor Telekinesis.** You learn the Mage Hand cantrip. You can cast it without Verbal or Somatic components, and you can make the spectral hand invisible. If you already know this spell, its range increases by 30 feet when you cast it. Its spellcasting ability is the ability increased by this feat.\n\n"
            "**Telekinetic Shove.** As a Bonus Action, you can try to telekinetically shove one creature you can see within 30 feet of you. When you do so, the target must succeed on a Strength saving throw (DC 8 + the ability modifier increased by this feat + your Proficiency Bonus) or be moved 5 feet toward you or away from you."
        ),
    },
    {
        "name": "Telepathic",
        "category": "General",
        "prerequisite": "Intelligence, Wisdom, or Charisma 13+",
        "desc": (
            "*General Feat (Prerequisite: Intelligence, Wisdom, or Charisma 13+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n\n"
            "**Telepathic Communication.** You can speak telepathically to any creature you can see within 60 feet of you. Your telepathic utterances are in a language you know, and the creature understands you only if it knows that language. Your communication doesn't give the creature the ability to respond to you telepathically.\n\n"
            "**Detect Thoughts.** You can cast the Detect Thoughts spell, requiring no spell slot or components, and you must finish a Long Rest before you can cast it this way again. Your spellcasting ability for the spell is the ability increased by this feat. If you have spell slots of level 2 or higher, you can cast this spell with them."
        ),
    },

    # ── Fighting Style (10 new) ───────────────────────────────────────────────
    {
        "name": "Archery",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "You gain a +2 bonus to attack rolls you make with Ranged weapons."
        ),
    },
    {
        "name": "Blind Fighting",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "You have Blindsight with a range of 10 feet."
        ),
    },
    {
        "name": "Defense",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "While you're wearing Light, Medium, or Heavy armor, you gain a +1 bonus to Armor Class."
        ),
    },
    {
        "name": "Dueling",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "When you're holding a Melee weapon in one hand and no other weapons, you gain a +2 bonus to damage rolls with that weapon."
        ),
    },
    {
        "name": "Great Weapon Fighting",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "When you roll damage for an attack you make with a Melee weapon that you are holding with two hands, you can treat any 1 or 2 on a damage die as a 3. The weapon must have the Two-Handed or Versatile property to gain this benefit."
        ),
    },
    {
        "name": "Interception",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "When a creature you can see hits another creature within 5 feet of you with an attack roll, you can take a Reaction to reduce the damage dealt to the target by 1d10 + your Proficiency Bonus. You must be holding a Shield or a Simple or Martial weapon to use this Reaction."
        ),
    },
    {
        "name": "Protection",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "When a creature you can see attacks a target other than you that is within 5 feet of you, you can take a Reaction to interpose your Shield and impose Disadvantage on the attack roll. You must be holding a Shield to use this Reaction."
        ),
    },
    {
        "name": "Thrown Weapon Fighting",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "When you hit with a ranged attack roll using a weapon that has the Thrown property, you gain a +2 bonus to the damage roll. In addition, you can draw a weapon that has the Thrown property as part of the attack you make with it."
        ),
    },
    {
        "name": "Two-Weapon Fighting",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "When you make an extra attack as a result of using a weapon that has the Light property, you can add your ability modifier to the damage of that extra attack if you aren't already adding it to the damage."
        ),
    },
    {
        "name": "Unarmed Fighting",
        "category": "Fighting Style",
        "prerequisite": "Proficiency with a Martial Weapon",
        "desc": (
            "*Fighting Style Feat (Prerequisite: Proficiency with a Martial Weapon)*\n\n"
            "When you hit with your Unarmed Strike and deal damage, you can deal Bludgeoning damage equal to 1d6 + your Strength modifier instead of the normal damage of an Unarmed Strike. If you aren't holding any weapons or a Shield when you make the attack roll, the d6 becomes a d8.\n\n"
            "At the start of each of your turns, you can deal 1d4 Bludgeoning damage to one creature Grappled by you."
        ),
    },

    # ── Epic Boon (12 new) ────────────────────────────────────────────────────
    {
        "name": "Boon of Combat Prowess",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Peerless Aim.** When you miss with an attack roll, you can hit instead. Once you use this benefit, you can't use it again until the start of your next turn."
        ),
    },
    {
        "name": "Boon of Dimensional Travel",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Blink Steps.** Immediately after you take the Attack action or the Magic action, you can teleport up to 30 feet to an unoccupied space you can see."
        ),
    },
    {
        "name": "Boon of Energy Resistance",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Energy Resistances.** You gain Resistance to two of the following damage types of your choice: Acid, Cold, Fire, Lightning, Necrotic, Poison, Psychic, Radiant, or Thunder. Whenever you finish a Long Rest, you can change your choices.\n\n"
            "**Energy Redirection.** When you take damage of one of the types chosen for the Energy Resistances benefit, you can take a Reaction to direct damage of the same type toward another creature you can see within 60 feet of yourself that isn't behind Total Cover. If you do, that creature must succeed on a Dexterity saving throw (DC 8 + your Proficiency Bonus + the ability modifier of the ability increased by this feat) or take damage equal to 2d12 plus your Constitution modifier."
        ),
    },
    {
        "name": "Boon of Fate",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Fate's Favor.** When you or another creature within 60 feet of you succeeds on or fails a D20 Test, you can roll 2d4 and apply the number rolled as a bonus or penalty to the d20 roll. Once you use this benefit, you can't use it again until you roll Initiative or finish a Short or Long Rest."
        ),
    },
    {
        "name": "Boon of Fortitude",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Fortified Health.** Your Hit Point maximum increases by 40. In addition, whenever you regain Hit Points, you can regain additional Hit Points equal to your Constitution modifier. You can regain these additional Hit Points no more than once per turn."
        ),
    },
    {
        "name": "Boon of Irresistible Offense",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Strength or Dexterity score by 1, to a maximum of 30.\n\n"
            "**Overcome Defenses.** The Bludgeoning, Piercing, and Slashing damage you deal always ignores Resistance.\n\n"
            "**Overwhelming Strike.** When you roll a 20 on the d20 for an attack roll, you can deal extra damage to the target equal to the ability modifier increased by this feat. The extra damage's type is the same as the attack's type."
        ),
    },
    {
        "name": "Boon of Recovery",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Last Stand.** When you would be reduced to 0 Hit Points, you can drop to a number of Hit Points equal to your Constitution modifier (minimum of 1 Hit Point) instead. Once you use this benefit, you can't use it again until you finish a Long Rest.\n\n"
            "**Speedy Recovery.** As a Bonus Action, you can expend one of your Hit Point Dice, roll it, and regain a number of Hit Points equal to the number rolled plus your Constitution modifier (minimum of 1 Hit Point). Once you use this benefit, you can't use it again until the start of your next turn."
        ),
    },
    {
        "name": "Boon of Skill",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**All-Around Adept.** You gain proficiency in all skills.\n\n"
            "**Expertise.** Choose five skills in which you have proficiency. You gain Expertise in those skills."
        ),
    },
    {
        "name": "Boon of Speed",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Speed Increase.** Your Speed increases by 30 feet.\n\n"
            "**Peerless Agility.** Opportunity Attacks have Disadvantage against you."
        ),
    },
    {
        "name": "Boon of Spell Recall",
        "category": "Epic Boon",
        "prerequisite": "Level 19+, Spellcasting or Pact Magic feature",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+, Spellcasting or Pact Magic feature)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 30.\n\n"
            "**Free Casting.** Whenever you cast a spell with a spell slot of level 1 through 4, roll 1d4. If the number you roll equals the level of the spell slot, the slot isn't expended."
        ),
    },
    {
        "name": "Boon of the Night Spirit",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Darkvision.** You have Darkvision with a range of 300 feet.\n\n"
            "**Shadow Step.** While you're within Dim Light or Darkness, you can take a Bonus Action to teleport up to 60 feet to an unoccupied space you can see that is also in Dim Light or Darkness.\n\n"
            "**Shadow Meld.** While you're within Dim Light or Darkness, you can take the Hide action as a Bonus Action even if you're in plain sight, using shadows to conceal yourself."
        ),
    },
    {
        "name": "Boon of Truesight",
        "category": "Epic Boon",
        "prerequisite": "Level 19+",
        "desc": (
            "*Epic Boon Feat (Prerequisite: Level 19+)*\n\n"
            "You gain the following benefits.\n\n"
            "**Ability Score Increase.** Increase one ability score of your choice by 1, to a maximum of 30.\n\n"
            "**Truesight.** You have Truesight with a range of 60 feet."
        ),
    },
]


def phase_d():
    """Create .md files for 36 brand-new 2024 feats."""
    print("\n" + "=" * 70)
    print("PHASE D: New 2024 Feats")
    print("=" * 70)
    created = 0

    for feat in NEW_FEATS_2024:
        filepath, content = generate_new_feat(feat)
        if os.path.exists(filepath):
            print(f"  SKIP (exists): {feat['name']}")
            continue
        write_file(filepath, content)
        print(f"  CREATED: {feat['name']} ({feat['category']})")
        created += 1

    print(f"\n  Phase D complete: {created} new feats created")
    return created


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"Feat vault: {VAULT_FEATS}")
    print()

    moved, deleted = phase_a()
    updated = phase_b()
    rewritten = phase_c()
    created = phase_d()

    # Count total feats
    total = 0
    for root, _dirs, files in os.walk(VAULT_FEATS):
        total += sum(1 for f in files if f.endswith(".md"))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Files moved:       {moved}")
    print(f"  Files deleted:     {deleted}")
    print(f"  Frontmatter updated: {updated}")
    print(f"  Descriptions rewritten: {rewritten}")
    print(f"  New feats created: {created}")
    print(f"  Total feat files:  {total}")
    print()
    print("Done! Run link_vault.py to re-link the vault.")


if __name__ == "__main__":
    main()
