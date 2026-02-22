#!/usr/bin/env python3
"""Populate Obsidian character sheets from Foundry VTT actor exports."""

import json
import math
import os
import re

# ── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.join(SCRIPT_DIR, "Tenelis")
PARTY_DIR = os.path.join(VAULT_ROOT, "01 - Party")
SOURCE_DIR = r"C:\Users\cfpor\Desktop\DndObsidian"

# JSON filename → (sheet number, player name, aliases)
CHARACTER_MAP = {
    "fvtt-Actor-netanyahu-d.-kirkuenly-nnEKWJyPLRLubatG.json": (1, "Conor", ["Net"]),
    "fvtt-Actor-booker-locke-tony-4nGqbVHT5RpdW1YI.json": (2, "Tony", []),
    "fvtt-Actor-old-shell-erik-49MF2ytKMV478LKx.json": (3, "Erik", []),
    "fvtt-Actor-cassius-bellona-jake-twrJLhtjw4LG5hSK.json": (4, "Jake", []),
    "fvtt-Actor-ryan-nigamus-aDgKZYENNFo45Jdo.json": (5, "Nigamus", []),
}

ABILITY_ORDER = ["str", "dex", "con", "int", "wis", "cha"]
ABILITY_LABELS = {"str": "STR", "dex": "DEX", "con": "CON",
                  "int": "INT", "wis": "WIS", "cha": "CHA"}

# Skill key → (display name, default ability)
SKILL_MAP = {
    "acr": ("Acrobatics", "dex"),
    "ani": ("Animal Handling", "wis"),
    "arc": ("Arcana", "int"),
    "ath": ("Athletics", "str"),
    "dec": ("Deception", "cha"),
    "his": ("History", "int"),
    "ins": ("Insight", "wis"),
    "itm": ("Intimidation", "cha"),
    "inv": ("Investigation", "int"),
    "med": ("Medicine", "wis"),
    "nat": ("Nature", "int"),
    "prc": ("Perception", "wis"),
    "prf": ("Performance", "cha"),
    "per": ("Persuasion", "cha"),
    "rel": ("Religion", "int"),
    "slt": ("Sleight of Hand", "dex"),
    "ste": ("Stealth", "dex"),
    "sur": ("Survival", "wis"),
}
SKILL_ORDER = list(SKILL_MAP.keys())

HIT_DICE = {
    "Barbarian": "d12", "Fighter": "d10", "Paladin": "d10", "Ranger": "d10",
    "Bard": "d8", "Cleric": "d8", "Druid": "d8", "Monk": "d8",
    "Rogue": "d8", "Warlock": "d8", "Artificer": "d8",
    "Sorcerer": "d6", "Wizard": "d6",
}

SPELLCASTING_ABILITY_NAMES = {
    "str": "Strength", "dex": "Dexterity", "con": "Constitution",
    "int": "Intelligence", "wis": "Wisdom", "cha": "Charisma",
}

# Correct max spell slots by caster progression at level 3
SPELL_SLOTS = {
    "full":  {3: [4, 2, 0, 0, 0, 0, 0, 0, 0]},
    "half":  {3: [3, 0, 0, 0, 0, 0, 0, 0, 0]},
    "third": {3: [2, 0, 0, 0, 0, 0, 0, 0, 0]},
}
CASTER_TYPE = {
    "Bard": "full", "Cleric": "full", "Druid": "full",
    "Sorcerer": "full", "Wizard": "full",
    "Paladin": "half", "Ranger": "half",
    "Fighter": "third", "Rogue": "third",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def modifier(score):
    return math.floor((score - 10) / 2)


def fmt_mod(mod):
    return f"+{mod}" if mod >= 0 else str(mod)


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = (text.replace("&amp;", "&").replace("&lt;", "<")
                .replace("&gt;", ">").replace("&quot;", '"')
                .replace("&#39;", "'"))
    return re.sub(r"\s+", " ", text).strip()


def safe_get(obj, *keys, default=None):
    """Drill into nested dicts safely."""
    for k in keys:
        if isinstance(obj, dict):
            obj = obj.get(k, default)
        else:
            return default
    return obj if obj is not None else default


def fmt_rarity(rarity):
    """Format Foundry rarity strings (e.g. 'veryRare' → 'Very Rare')."""
    if not rarity or rarity == "common":
        return ""
    # Insert space before capital letters for camelCase
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", rarity)
    return spaced.title()


# ── Parsing ──────────────────────────────────────────────────────────────────

def parse_character(json_path, sheet_num, player_name, aliases):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    system = data["system"]
    items = data.get("items", [])

    # ── Name ─────────────────────────────────────────────────────────────
    actor_name = data["name"]
    char_name = actor_name.split(" - ")[0].strip() if " - " in actor_name else actor_name

    # ── Abilities ────────────────────────────────────────────────────────
    prof_bonus = 2  # all level 3
    abilities = {}
    for abl in ABILITY_ORDER:
        score = system["abilities"][abl]["value"]
        prof = system["abilities"][abl].get("proficient", 0)
        mod = modifier(score)
        abilities[abl] = {"score": score, "modifier": mod, "proficient": prof}

    # ── Items: class / subclass / race / background ──────────────────────
    class_name = subclass_name = race_name = background_name = ""
    class_level = 1
    for item in items:
        t, n = item.get("type", ""), item.get("name", "")
        if t == "class":
            class_name = n
            class_level = safe_get(item, "system", "levels", default=1)
        elif t == "subclass":
            subclass_name = n
        elif t == "race":
            race_name = n
        elif t == "background":
            background_name = n

    # ── Attributes ───────────────────────────────────────────────────────
    attrs = system.get("attributes", {})
    speed = safe_get(attrs, "movement", "walk", default=30)
    hp = safe_get(attrs, "hp", "value", default=0)
    spellcasting_abl = safe_get(attrs, "spellcasting", default="") or ""
    has_spells = bool(spellcasting_abl)

    # ── AC ────────────────────────────────────────────────────────────────
    ac_calc = safe_get(attrs, "ac", "calc", default="default")
    ac_flat = safe_get(attrs, "ac", "flat", default=None)

    if ac_calc == "natural" and ac_flat is not None:
        ac = ac_flat
    elif ac_calc == "unarmoredBarb":
        ac = 10 + abilities["dex"]["modifier"] + abilities["con"]["modifier"]
    else:
        base_ac = 10 + abilities["dex"]["modifier"]
        shield_bonus = 0
        for item in items:
            if item.get("type") != "equipment":
                continue
            isys = item.get("system", {})
            equipped = isys.get("equipped", False)
            if isinstance(equipped, dict):
                equipped = equipped.get("value", False)
            if not equipped:
                continue
            type_obj = isys.get("type", {})
            atype = type_obj.get("value", "") if isinstance(type_obj, dict) else (type_obj or "")
            armor_val = safe_get(isys, "armor", "value", default=0) or 0
            magic_bonus = safe_get(isys, "armor", "magicalBonus", default=0) or 0
            if atype == "light":
                base_ac = armor_val + magic_bonus + abilities["dex"]["modifier"]
            elif atype == "medium":
                base_ac = armor_val + magic_bonus + min(abilities["dex"]["modifier"], 2)
            elif atype == "heavy":
                base_ac = armor_val + magic_bonus
            elif atype == "shield":
                shield_bonus = armor_val + magic_bonus
        ac = base_ac + shield_bonus

    # ── Derived combat stats ─────────────────────────────────────────────
    initiative = abilities["dex"]["modifier"]
    hit_die = HIT_DICE.get(class_name, "d8")
    hit_dice = f"{class_level}{hit_die}"

    # ── Skills ───────────────────────────────────────────────────────────
    skills = {}
    for key in SKILL_ORDER:
        sd = system["skills"][key]
        val = sd.get("value", 0)
        abl = sd.get("ability", SKILL_MAP[key][1])
        abl_mod = abilities[abl]["modifier"]
        if val == 0:
            total = abl_mod
        elif val == 0.5:
            total = abl_mod + math.floor(prof_bonus / 2)  # Jack of All Trades
        elif val == 1:
            total = abl_mod + prof_bonus
        elif val == 2:
            total = abl_mod + 2 * prof_bonus
        else:
            total = abl_mod
        skills[key] = {"value": val, "ability": abl, "total": total}

    passive_perception = 10 + skills["prc"]["total"]

    # ── Spell slots ──────────────────────────────────────────────────────
    spell_slots = [0] * 9
    if has_spells and class_name in CASTER_TYPE:
        ct = CASTER_TYPE[class_name]
        spell_slots = SPELL_SLOTS.get(ct, {}).get(class_level, [0] * 9)

    # ── Spell save / attack ──────────────────────────────────────────────
    spell_save_dc = spell_atk = 0
    if has_spells:
        sc_mod = abilities[spellcasting_abl]["modifier"]
        spell_save_dc = 8 + prof_bonus + sc_mod
        spell_atk = prof_bonus + sc_mod

    # ── Weapons (attacks table) ──────────────────────────────────────────
    weapons = []
    seen_weapons = set()
    for item in items:
        if item.get("type") != "weapon":
            continue
        name = item.get("name", "")
        if name == "Unarmed Strike" or name in seen_weapons:
            continue
        seen_weapons.add(name)
        isys = item.get("system", {})

        # Damage
        base_dmg = safe_get(isys, "damage", "base", default={})
        d_num = base_dmg.get("number")
        d_den = base_dmg.get("denomination")
        d_bonus = base_dmg.get("bonus", "") or ""
        d_types = base_dmg.get("types", [])
        d_type = d_types[0] if d_types else ""

        if d_num and d_den:
            dmg = f"{d_num}d{d_den}"
        else:
            dmg = "1"

        # Properties
        props = isys.get("properties", [])
        if isinstance(props, dict):
            props = [k for k, v in props.items() if v]

        is_finesse = "fin" in props
        is_ammo = "amm" in props

        # Attack ability
        if is_finesse:
            atk_abl_mod = max(abilities["str"]["modifier"], abilities["dex"]["modifier"])
        elif is_ammo:
            atk_abl_mod = abilities["dex"]["modifier"]
        else:
            atk_abl_mod = abilities["str"]["modifier"]

        atk_bonus = atk_abl_mod + prof_bonus
        # Weapon magic bonus from name ("+1", "+2", etc.)
        m = re.search(r"\+(\d+)", name)
        if m:
            atk_bonus += int(m.group(1))

        # Damage with ability modifier
        if atk_abl_mod > 0:
            dmg += f" + {atk_abl_mod}"
        elif atk_abl_mod < 0:
            dmg += f" - {abs(atk_abl_mod)}"
        if d_bonus:
            dmg += f" + {d_bonus}"
        if d_type:
            dmg += f" {d_type}"

        # Range
        r_val = safe_get(isys, "range", "value", default=None)
        r_long = safe_get(isys, "range", "long", default=None)
        if r_val and r_long and r_long > 0:
            range_str = f"{r_val}/{r_long} ft."
        elif r_val:
            range_str = f"{r_val} ft."
        elif r_long:
            range_str = f"{r_long} ft."
        else:
            range_str = "5 ft."

        # Notes
        rarity = isys.get("rarity", "")
        notes = fmt_rarity(rarity)

        weapons.append({
            "name": name, "atk_bonus": fmt_mod(atk_bonus),
            "damage": dmg, "range": range_str, "notes": notes,
        })

    # ── Spells (grouped by level, deduplicated, skip item-granted) ─────
    spells_by_level = {}
    for item in items:
        if item.get("type") != "spell":
            continue
        # Skip spells granted by magic items (Staff of Healing, etc.)
        cached_for = safe_get(item, "flags", "dnd5e", "cachedFor", default="")
        if cached_for and cached_for.startswith(".Item."):
            continue
        sname = item.get("name", "")
        slevel = safe_get(item, "system", "level", default=0)
        spells_by_level.setdefault(slevel, set()).add(sname)
    for lvl in spells_by_level:
        spells_by_level[lvl] = sorted(spells_by_level[lvl])

    # ── Features & Traits ────────────────────────────────────────────────
    features = sorted(item["name"] for item in items if item.get("type") == "feat")

    # ── Equipment ────────────────────────────────────────────────────────
    equipment = []
    equip_types = {"equipment", "container", "tool", "consumable", "loot"}
    for item in items:
        if item.get("type") not in equip_types:
            continue
        isys = item.get("system", {})
        qty = isys.get("quantity", 1)
        w = isys.get("weight", 0)
        weight = w.get("value", 0) if isinstance(w, dict) else (w or 0)
        weight = weight or 0
        if weight == int(weight) and weight > 0:
            weight_str = f"{int(weight)} lb."
        elif weight > 0:
            weight_str = f"{weight} lb."
        else:
            weight_str = "—"

        notes_parts = []
        rarity = isys.get("rarity", "")
        if rarity and rarity != "common":
            notes_parts.append(fmt_rarity(rarity))
        equipped = isys.get("equipped", False)
        if isinstance(equipped, dict):
            equipped = equipped.get("value", False)
        type_obj = isys.get("type", {})
        atype = type_obj.get("value", "") if isinstance(type_obj, dict) else ""
        if equipped and atype in ("light", "medium", "heavy", "shield"):
            notes_parts.append("Equipped")

        equipment.append({
            "name": item["name"], "qty": qty,
            "weight": weight_str, "notes": ", ".join(notes_parts),
        })
    equipment.sort(key=lambda x: x["name"])

    # ── Currency ─────────────────────────────────────────────────────────
    cur = system.get("currency", {})

    # ── Details ──────────────────────────────────────────────────────────
    details = system.get("details", {})
    alignment = details.get("alignment", "")
    trait = strip_html(details.get("trait", ""))
    ideal = strip_html(details.get("ideal", ""))
    bond = strip_html(details.get("bond", ""))
    flaw = strip_html(details.get("flaw", ""))

    return {
        "sheet_num": sheet_num, "player": player_name,
        "character_name": char_name, "aliases": aliases,
        "race": race_name, "class": class_name,
        "subclass": subclass_name, "level": class_level,
        "background": background_name, "alignment": alignment,
        "abilities": abilities, "prof_bonus": prof_bonus,
        "ac": ac, "initiative": initiative, "speed": speed,
        "hp": hp, "hit_dice": hit_dice,
        "skills": skills, "passive_perception": passive_perception,
        "weapons": weapons,
        "has_spells": has_spells, "spellcasting_abl": spellcasting_abl,
        "spell_save_dc": spell_save_dc, "spell_atk": spell_atk,
        "spell_slots": spell_slots, "spells_by_level": spells_by_level,
        "features": features, "equipment": equipment,
        "cp": cur.get("cp", 0), "sp": cur.get("sp", 0),
        "ep": cur.get("ep", 0), "gp": cur.get("gp", 0),
        "pp": cur.get("pp", 0),
        "trait": trait, "ideal": ideal, "bond": bond, "flaw": flaw,
    }


# ── Sheet generation ─────────────────────────────────────────────────────────

def generate_sheet(c):
    lines = []

    # ── YAML frontmatter ─────────────────────────────────────────────────
    lines.append("---")
    if c["aliases"]:
        lines.append("aliases:")
        for a in c["aliases"]:
            lines.append(f"  - {a}")
    else:
        lines.append("aliases: []")
    lines.append("tags: [character]")
    lines.append(f"player: {c['player']}")
    lines.append(f"character_name: {c['character_name']}")
    lines.append(f"race: {c['race']}")
    lines.append(f"class: {c['class']}")
    lines.append(f"subclass: {c['subclass']}")
    lines.append(f"level: {c['level']}")
    lines.append(f"background: {c['background']}")
    lines.append(f"alignment: {c['alignment']}")
    lines.append("---")
    lines.append("")

    # ── Infobox callout ──────────────────────────────────────────────────
    lines.append("> [!infobox]")
    lines.append("> # `=this.character_name`")
    lines.append("> **Race:** `=this.race`")
    lines.append("> **Class:** `=this.class` (`=this.subclass`)")
    lines.append("> **Level:** `=this.level`")
    lines.append("> **Background:** `=this.background`")
    lines.append("> **Alignment:** `=this.alignment`")
    lines.append("> **Player:** `=this.player`")
    lines.append("")

    # ── Ability Scores ───────────────────────────────────────────────────
    lines.append("## [[Ability Scores]]")
    lines.append("")
    lines.append("| Ability | Score | Modifier | Save Prof? | Save Mod |")
    lines.append("|---------|-------|----------|------------|----------|")
    for abl in ABILITY_ORDER:
        a = c["abilities"][abl]
        label = ABILITY_LABELS[abl]
        prof_check = "\u2611" if a["proficient"] else "\u2610"
        save = a["modifier"] + (c["prof_bonus"] if a["proficient"] else 0)
        lines.append(
            f"| **{label}** | {a['score']} | {fmt_mod(a['modifier'])} "
            f"| {prof_check} | {fmt_mod(save)} |"
        )
    lines.append("")

    # ── Combat stats ─────────────────────────────────────────────────────
    lines.append(f"**Proficiency Bonus:** +{c['prof_bonus']}")
    lines.append(f"**Armor Class:** {c['ac']}")
    lines.append(f"**Initiative:** {fmt_mod(c['initiative'])}")
    lines.append(f"**Speed:** {c['speed']} ft.")
    lines.append(f"**Hit Point Maximum:** {c['hp']}")
    lines.append(f"**Current Hit Points:** {c['hp']}")
    lines.append("**Temporary Hit Points:** 0")
    lines.append(f"**Hit Dice:** {c['hit_dice']}")
    lines.append("")

    # ── Skills ───────────────────────────────────────────────────────────
    lines.append("## Skills")
    lines.append("")
    lines.append("| Skill | Ability | Prof? | Mod |")
    lines.append("|-------|---------|-------|-----|")
    for key in SKILL_ORDER:
        name = SKILL_MAP[key][0]
        s = c["skills"][key]
        abl_label = s["ability"].upper()
        if s["value"] == 2:
            prof = "\u2611\u2611"
        elif s["value"] >= 1:
            prof = "\u2611"
        elif s["value"] == 0.5:
            prof = "\u00bd"
        else:
            prof = "\u2610"
        lines.append(f"| [[{name}]] | {abl_label} | {prof} | {fmt_mod(s['total'])} |")
    lines.append("")
    lines.append(f"**Passive Perception:** {c['passive_perception']}")
    lines.append("")

    # ── Attacks ──────────────────────────────────────────────────────────
    lines.append("## Attacks & Spellcasting")
    lines.append("")
    lines.append("| Name | Atk Bonus | Damage/Type | Range/Reach | Notes |")
    lines.append("|------|-----------|-------------|-------------|-------|")
    if c["weapons"]:
        for w in c["weapons"]:
            lines.append(
                f"| {w['name']} | {w['atk_bonus']} | {w['damage']} "
                f"| {w['range']} | {w['notes']} |"
            )
    else:
        lines.append("|      |           |             |             |       |")
    lines.append("")

    # ── Spellcasting ─────────────────────────────────────────────────────
    if c["has_spells"]:
        lines.append("## Spellcasting")
        lines.append("")
        abl_name = SPELLCASTING_ABILITY_NAMES.get(c["spellcasting_abl"], "")
        lines.append(f"**Spellcasting Ability:** {abl_name}")
        lines.append(f"**Spell Save DC:** {c['spell_save_dc']}")
        lines.append(f"**Spell Attack Bonus:** {fmt_mod(c['spell_atk'])}")
        lines.append("")

        lines.append("| Slot Level | Total | Expended |")
        lines.append("|------------|-------|----------|")
        ordinals = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]
        for i, label in enumerate(ordinals):
            lines.append(f"| {label}        | {c['spell_slots'][i]}     |          |")
        lines.append("")

        lines.append("### Spells Known / Prepared")
        lines.append("")
        level_names = {
            0: "Cantrips", 1: "1st Level", 2: "2nd Level", 3: "3rd Level",
            4: "4th Level", 5: "5th Level", 6: "6th Level",
            7: "7th Level", 8: "8th Level", 9: "9th Level",
        }
        for lvl in range(10):
            spells = c["spells_by_level"].get(lvl, [])
            label = level_names[lvl]
            if spells:
                spell_links = ", ".join(f"[[{s}]]" for s in spells)
                lines.append(f"**{label}:** {spell_links}")
            else:
                lines.append(f"**{label}:**")
            lines.append("")

    # ── Features & Traits ────────────────────────────────────────────────
    lines.append("## Features & Traits")
    lines.append("")
    for feat in c["features"]:
        lines.append(f"- {feat}")
    lines.append("")

    # ── Equipment ────────────────────────────────────────────────────────
    lines.append("## Equipment")
    lines.append("")
    lines.append("| Item | Qty | Weight | Notes |")
    lines.append("|------|-----|--------|-------|")
    for eq in c["equipment"]:
        lines.append(f"| {eq['name']} | {eq['qty']} | {eq['weight']} | {eq['notes']} |")
    lines.append("")

    # ── Currency ─────────────────────────────────────────────────────────
    lines.append("### Currency")
    lines.append("")
    lines.append("| CP | SP | EP | GP | PP |")
    lines.append("|----|----|----|----|----|")
    lines.append(f"| {c['cp']} | {c['sp']} | {c['ep']} | {c['gp']} | {c['pp']} |")
    lines.append("")

    # ── Personality ──────────────────────────────────────────────────────
    lines.append("## Personality")
    lines.append("")
    lines.append(f"**Personality Traits:** {c['trait']}")
    lines.append("")
    lines.append(f"**Ideals:** {c['ideal']}")
    lines.append("")
    lines.append(f"**Bonds:** {c['bond']}")
    lines.append("")
    lines.append(f"**Flaws:** {c['flaw']}")
    lines.append("")

    # ── Backstory & Notes ────────────────────────────────────────────────
    lines.append("## Backstory")
    lines.append("")
    lines.append("")
    lines.append("## Notes")
    lines.append("")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Populating character sheets from Foundry VTT exports...")
    print(f"  Source: {SOURCE_DIR}")
    print(f"  Target: {PARTY_DIR}")
    print()

    for json_file, (sheet_num, player, aliases) in CHARACTER_MAP.items():
        path = os.path.join(SOURCE_DIR, json_file)
        if not os.path.exists(path):
            print(f"  WARNING: {json_file} not found, skipping")
            continue

        char = parse_character(path, sheet_num, player, aliases)
        content = generate_sheet(char)
        out_path = os.path.join(PARTY_DIR, f"{char['character_name']}.md")

        # Remove old numbered sheet if it exists
        old_path = os.path.join(PARTY_DIR, f"Character Sheet {sheet_num}.md")
        if os.path.exists(old_path) and old_path != out_path:
            os.remove(old_path)
            print(f"  Removed: Character Sheet {sheet_num}.md")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  Created: {char['character_name']}.md")
        print(f"    {char['race']} {char['class']} ({char['subclass']}) Lv{char['level']}")
        print(f"    HP {char['hp']} | AC {char['ac']} | "
              f"STR {char['abilities']['str']['score']} "
              f"DEX {char['abilities']['dex']['score']} "
              f"CON {char['abilities']['con']['score']} "
              f"INT {char['abilities']['int']['score']} "
              f"WIS {char['abilities']['wis']['score']} "
              f"CHA {char['abilities']['cha']['score']}")
        if char["has_spells"]:
            n_spells = sum(len(v) for v in char["spells_by_level"].values())
            print(f"    Spells: {n_spells} known | DC {char['spell_save_dc']}")
        print(f"    Weapons: {len(char['weapons'])} | Equipment: {len(char['equipment'])}")
        print()

    print("Done! Character sheets populated.")


if __name__ == "__main__":
    main()
