#!/usr/bin/env python3
"""
Generate reference content .md files for the Tenelis Obsidian vault.

Creates Backgrounds (16), Rules topics (12), and a Glossary for D&D 5e (2024).

Usage:
    python generate_reference_content.py           # Generate all missing .md files
    python generate_reference_content.py --dry-run # Show what would be created
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.join(SCRIPT_DIR, "Tenelis")
REFERENCE_ROOT = os.path.join(VAULT_ROOT, "07 - Reference")
BACKGROUNDS_DIR = os.path.join(REFERENCE_ROOT, "Backgrounds")
RULES_DIR = os.path.join(REFERENCE_ROOT, "Rules")

# ── Helper ────────────────────────────────────────────────────────────────────

def write_file(filepath, content, dry_run=False):
    """Write a file, creating directories as needed. Returns True if created."""
    if os.path.exists(filepath):
        return False
    if dry_run:
        rel = os.path.relpath(filepath, VAULT_ROOT)
        print(f"  + {rel}")
        return True
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ══════════════════════════════════════════════════════════════════════════════
#  BACKGROUNDS
# ══════════════════════════════════════════════════════════════════════════════

BACKGROUNDS = [
    {
        "name": "Acolyte",
        "description": "You spent your early days in a religious community. Study and prayer were the pillars of your existence, granting you insight into the nature of the divine and the workings of faith.",
        "ability_scores": "Intelligence, Wisdom, Charisma",
        "origin_feat": "[[Magic Initiate]] (Cleric)",
        "skill_proficiencies": "Insight, Religion",
        "tool_proficiency": "Calligrapher's Supplies",
        "equipment": "Calligrapher's Supplies, Book (prayers), Holy Symbol, Parchment (10), Robe, 8 GP",
    },
    {
        "name": "Artisan",
        "description": "You began your career as an apprentice to a skilled artisan, learning the tools of a particular trade. Your hands-on experience gives you a practical understanding of materials and craftsmanship.",
        "ability_scores": "Strength, Dexterity, Intelligence",
        "origin_feat": "[[Crafter]]",
        "skill_proficiencies": "Investigation, Persuasion",
        "tool_proficiency": "Artisan's Tools (one of your choice)",
        "equipment": "Artisan's Tools (one of your choice), Letter of Introduction, Pouch, Traveler's Clothes, 32 GP",
    },
    {
        "name": "Charlatan",
        "description": "You learned early on that people are gullible and easily manipulated. You have a knack for reading others, creating false identities, and running confidence schemes.",
        "ability_scores": "Dexterity, Constitution, Charisma",
        "origin_feat": "[[Skilled]]",
        "skill_proficiencies": "Deception, Sleight of Hand",
        "tool_proficiency": "Forgery Kit",
        "equipment": "Forgery Kit, Costume, Fine Clothes, Pouch, 15 GP",
    },
    {
        "name": "Criminal",
        "description": "You have a history of breaking the law. You might have been a burglar, a bandit, a smuggler, or some other sort of ne'er-do-well. Your time in the underworld taught you things most honest folk never learn.",
        "ability_scores": "Dexterity, Constitution, Intelligence",
        "origin_feat": "[[Alert]]",
        "skill_proficiencies": "Sleight of Hand, Stealth",
        "tool_proficiency": "Thieves' Tools",
        "equipment": "Thieves' Tools, Crowbar, Pouch, Traveler's Clothes, 16 GP",
    },
    {
        "name": "Entertainer",
        "description": "You thrive in front of an audience. You know how to entrance them, entertain them, and inspire them. Your poetics can stir the hearts of those who hear you, awakening grief, joy, or anger.",
        "ability_scores": "Strength, Dexterity, Charisma",
        "origin_feat": "[[Musician]]",
        "skill_proficiencies": "Acrobatics, Performance",
        "tool_proficiency": "Musical Instrument (one of your choice)",
        "equipment": "Musical Instrument (one of your choice), Costume (2), Mirror, Perfume, Traveler's Clothes, 11 GP",
    },
    {
        "name": "Farmer",
        "description": "You grew up close to the land, tilling the soil, tending crops, and raising livestock. Hard work under the open sky gave you a sturdy constitution and a practical outlook on life.",
        "ability_scores": "Strength, Constitution, Wisdom",
        "origin_feat": "[[Tough]]",
        "skill_proficiencies": "Animal Handling, Nature",
        "tool_proficiency": "Carpenter's Tools",
        "equipment": "Carpenter's Tools, Healer's Kit, Iron Pot, Shovel, Traveler's Clothes, 30 GP",
    },
    {
        "name": "Guard",
        "description": "You served as a guard, watching over a settlement, a noble's estate, a trade caravan, or some other place of importance. Vigilance and discipline were the cornerstones of your duty.",
        "ability_scores": "Strength, Intelligence, Wisdom",
        "origin_feat": "[[Alert]]",
        "skill_proficiencies": "Athletics, Perception",
        "tool_proficiency": "Gaming Set (one of your choice)",
        "equipment": "Gaming Set (one of your choice), Hooded Lantern, Manacles, Quiver, Shortbow, Traveler's Clothes, 12 GP",
    },
    {
        "name": "Guide",
        "description": "You are an expert at navigating the wilds. You lead travelers safely through forests, mountains, deserts, and other treacherous terrain, using keen senses and hard-won knowledge of the land.",
        "ability_scores": "Dexterity, Constitution, Wisdom",
        "origin_feat": "[[Magic Initiate]] (Druid)",
        "skill_proficiencies": "Stealth, Survival",
        "tool_proficiency": "Cartographer's Tools",
        "equipment": "Cartographer's Tools, Bedroll, Quiver, Shortbow, Tent, Traveler's Clothes, 3 GP",
    },
    {
        "name": "Hermit",
        "description": "You spent an extended period living in seclusion — perhaps in a monastery, a forest, a desert cave, or some other isolated retreat. In that time of solitary contemplation, you found quiet and perhaps even illumination.",
        "ability_scores": "Constitution, Wisdom, Charisma",
        "origin_feat": "[[Healer]]",
        "skill_proficiencies": "Medicine, Religion",
        "tool_proficiency": "Herbalism Kit",
        "equipment": "Herbalism Kit, Bedroll, Book (philosophy), Lamp, Oil (3 flasks), Traveler's Clothes, 16 GP",
    },
    {
        "name": "Merchant",
        "description": "You were a professional trader, skilled in appraising goods and negotiating deals. The marketplace was your second home, and you learned how to read people as easily as a ledger.",
        "ability_scores": "Constitution, Intelligence, Charisma",
        "origin_feat": "[[Lucky]]",
        "skill_proficiencies": "Animal Handling, Persuasion",
        "tool_proficiency": "Navigator's Tools",
        "equipment": "Navigator's Tools, Pouch, Traveler's Clothes, 22 GP",
    },
    {
        "name": "Noble",
        "description": "You were born into a family of wealth and privilege. Whether you embraced or rebelled against your upbringing, it gave you confidence, education, and connections that most people lack.",
        "ability_scores": "Strength, Intelligence, Charisma",
        "origin_feat": "[[Skilled]]",
        "skill_proficiencies": "History, Persuasion",
        "tool_proficiency": "Gaming Set (one of your choice)",
        "equipment": "Gaming Set (one of your choice), Fine Clothes, Perfume, Signet Ring, 29 GP",
    },
    {
        "name": "Sage",
        "description": "You spent years learning the lore of the multiverse. You scoured manuscripts, studied scrolls, and listened to the greatest experts on the subjects that interest you.",
        "ability_scores": "Constitution, Intelligence, Wisdom",
        "origin_feat": "[[Magic Initiate]] (Wizard)",
        "skill_proficiencies": "Arcana, History",
        "tool_proficiency": "Calligrapher's Supplies",
        "equipment": "Calligrapher's Supplies, Book (lore), Parchment (8), Robe, 8 GP",
    },
    {
        "name": "Sailor",
        "description": "You sailed on a seagoing vessel for years, whether as a simple deckhand, a marine, a navigator, or even a pirate. Life at sea taught you to handle storms, read the weather, and hold your own in a fight.",
        "ability_scores": "Strength, Dexterity, Wisdom",
        "origin_feat": "[[Tavern Brawler]]",
        "skill_proficiencies": "Acrobatics, Perception",
        "tool_proficiency": "Navigator's Tools",
        "equipment": "Navigator's Tools, Dagger, Fishing Tackle, Rope, Traveler's Clothes, 20 GP",
    },
    {
        "name": "Scribe",
        "description": "You spent formative years recording information, copying documents, and assisting more learned scholars. Your eye for detail and ability to organize knowledge are second to none.",
        "ability_scores": "Dexterity, Intelligence, Wisdom",
        "origin_feat": "[[Skilled]]",
        "skill_proficiencies": "Investigation, Perception",
        "tool_proficiency": "Calligrapher's Supplies",
        "equipment": "Calligrapher's Supplies, Fine Clothes, Lamp, Oil (3 flasks), Parchment (12), 23 GP",
    },
    {
        "name": "Soldier",
        "description": "You began training for war at a young age. You might have been a member of a national army, a mercenary company, or a local militia. Battle and discipline are in your blood.",
        "ability_scores": "Strength, Dexterity, Constitution",
        "origin_feat": "[[Savage Attacker]]",
        "skill_proficiencies": "Athletics, Intimidation",
        "tool_proficiency": "Gaming Set (one of your choice)",
        "equipment": "Gaming Set (one of your choice), Healer's Kit, Quiver, Shortbow, Spear, Traveler's Clothes, 14 GP",
    },
    {
        "name": "Wayfarer",
        "description": "You grew up on the road, traveling with a band of nomads, a caravan of merchants, or a troupe of performers. Life on the move taught you self-reliance and how to find comfort wherever you lay your head.",
        "ability_scores": "Dexterity, Wisdom, Charisma",
        "origin_feat": "[[Lucky]]",
        "skill_proficiencies": "Insight, Stealth",
        "tool_proficiency": "Thieves' Tools",
        "equipment": "Thieves' Tools, Bedroll, Mess Kit, Traveler's Clothes, Waterskin, 16 GP",
    },
]


def render_background(bg):
    """Render a background dict to markdown content."""
    lines = [
        "---",
        "tags: [background, reference]",
        'source: "2024"',
        "---",
        f"# {bg['name']}",
        "",
        "*Background*",
        "",
        bg["description"],
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| **Ability Scores** | {bg['ability_scores']} |",
        f"| **Origin Feat** | {bg['origin_feat']} |",
        f"| **Skill Proficiencies** | {bg['skill_proficiencies']} |",
        f"| **Tool Proficiency** | {bg['tool_proficiency']} |",
        f"| **Equipment** | {bg['equipment']} |",
        "",
        "---",
        f"\U0001f517 [Full Details on 5e.tools](https://5e.tools/backgrounds.html#{bg['name'].lower()}_2024)",
    ]
    return "\n".join(lines) + "\n"


# ══════════════════════════════════════════════════════════════════════════════
#  RULES
# ══════════════════════════════════════════════════════════════════════════════

def render_actions_in_combat():
    return """---
tags: [rule, reference]
source: "2024"
---
# Actions in Combat

On your turn, you can take **one action**. The following actions are available to all creatures in combat.

## Attack

Make one melee or ranged attack. At higher levels, martial characters gain Extra Attack, allowing multiple attacks with this action.

## Dash

You gain extra movement equal to your Speed (after applying modifiers) for the current turn.

## Disengage

Your movement doesn't provoke [[Opportunity Attacks]] for the rest of the turn.

## Dodge

Until the start of your next turn, any attack roll made against you has Disadvantage if you can see the attacker, and you make Dexterity saving throws with Advantage.

## Help

You lend aid to another creature within 5 feet, giving them Advantage on the next ability check for the task you're helping with. Alternatively, you can aid an ally attacking a creature within 5 feet of you, giving them Advantage on their next attack roll against that creature (before the start of your next turn).

## Hide

You make a Dexterity (Stealth) check to become [[Invisible|hidden]] from other creatures. See the Hide action rules and the [[Invisible]] condition.

## Influence

You make a Charisma (Deception, Intimidation, or Persuasion) check to alter a creature's attitude. The DC equals the target's Wisdom score (not modifier).

## Magic

You cast a spell with a casting time of an action, use a magic item, or use a magical feature that requires a Magic action.

## Ready

You prepare to take an action in response to a trigger you define. When the trigger occurs, you can use your Reaction to take the readied action. If you ready a spell, you cast it on your turn (spending the spell slot) and hold its energy until the trigger.

## Search

You make a Wisdom (Perception) or Intelligence (Investigation) check to find something hidden or discern information.

## Study

You make an Intelligence (Arcana, History, Investigation, Nature, or Religion) check to recall or deduce information about a creature, object, or other subject.

## Utilize

You interact with a second object or use a nonmagical special feature, such as activating an item that requires an action.

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#actions_2024)
"""


def render_ability_scores():
    return """---
tags: [rule, reference]
source: "2024"
---
# Ability Scores

Every creature has six ability scores that describe their physical and mental characteristics.

## The Six Ability Scores

| Ability | Description |
|---------|-------------|
| **Strength** | Physical power. Affects melee attacks, carrying capacity, and Athletics checks. |
| **Dexterity** | Agility and reflexes. Affects AC, ranged attacks, initiative, and Acrobatics/Sleight of Hand/Stealth checks. |
| **Constitution** | Endurance and health. Affects Hit Points and Concentration saves. |
| **Intelligence** | Reasoning and memory. Affects Arcana, History, Investigation, Nature, and Religion checks. |
| **Wisdom** | Perception and intuition. Affects Animal Handling, Insight, Medicine, Perception, and Survival checks. |
| **Charisma** | Force of personality. Affects Deception, Intimidation, Performance, and Persuasion checks. |

## Ability Score Modifier Table

The modifier is what you add to d20 rolls, not the score itself.

| Score | Modifier | Score | Modifier |
|-------|----------|-------|----------|
| 1 | -5 | 16-17 | +3 |
| 2-3 | -4 | 18-19 | +4 |
| 4-5 | -3 | 20-21 | +5 |
| 6-7 | -2 | 22-23 | +6 |
| 8-9 | -1 | 24-25 | +7 |
| 10-11 | +0 | 26-27 | +8 |
| 12-13 | +1 | 28-29 | +9 |
| 14-15 | +2 | 30 | +10 |

**Formula:** Modifier = floor((Score - 10) / 2)

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#ability%20scores_2024)
"""


def render_skills():
    return """---
tags: [rule, reference]
source: "2024"
---
# Skills

Each ability score covers a broad range of capabilities. A skill represents a specific aspect of an ability score, and proficiency in a skill demonstrates a focus on that aspect.

## Skill List

| Skill | Ability | Description |
|-------|---------|-------------|
| **Acrobatics** | Dexterity | Balance, tumbling, aerial maneuvers |
| **Animal Handling** | Wisdom | Calm, control, or intuit an animal's intentions |
| **Arcana** | Intelligence | Recall lore about spells, magic items, planes of existence |
| **Athletics** | Strength | Climbing, jumping, swimming, grappling |
| **Deception** | Charisma | Convincingly hide the truth through words or actions |
| **History** | Intelligence | Recall lore about events, people, nations, wars |
| **Insight** | Wisdom | Read body language, detect lies, predict behavior |
| **Intimidation** | Charisma | Influence through threats, hostile actions, physical presence |
| **Investigation** | Intelligence | Search for clues, make deductions, find hidden details |
| **Medicine** | Wisdom | Stabilize a dying creature, diagnose illness |
| **Nature** | Intelligence | Recall lore about terrain, plants, animals, weather |
| **Perception** | Wisdom | Spot, hear, or detect the presence of something |
| **Performance** | Charisma | Delight an audience with music, dance, acting, or storytelling |
| **Persuasion** | Charisma | Influence through tact, social graces, or good nature |
| **Religion** | Intelligence | Recall lore about deities, rites, prayers, holy symbols |
| **Sleight of Hand** | Dexterity | Pickpocket, conceal an object, perform manual trickery |
| **Stealth** | Dexterity | Hide, move silently, avoid detection |
| **Survival** | Wisdom | Track, forage, navigate, avoid natural hazards |

## Proficiency

If you are proficient in a skill, you add your **Proficiency Bonus** to ability checks using that skill. Your Proficiency Bonus is determined by your level:

| Level | Bonus | Level | Bonus |
|-------|-------|-------|-------|
| 1-4 | +2 | 13-16 | +5 |
| 5-8 | +3 | 17-20 | +6 |
| 9-12 | +4 | | |

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#skills_2024)
"""


def render_resting():
    return """---
tags: [rule, reference]
source: "2024"
---
# Resting

Adventurers need rest to recover their strength. Two types of rest are available.

## Short Rest

A Short Rest is a period of downtime, **at least 1 hour** long, during which a character does nothing more strenuous than eating, drinking, reading, and tending to wounds.

- **Hit Dice:** A character can spend one or more Hit Dice at the end of a Short Rest to regain Hit Points. For each Hit Die spent, roll the die and add your Constitution modifier. You regain that many Hit Points.
- **Feature Recovery:** Some class features and abilities recharge on a Short Rest.

## Long Rest

A Long Rest is an extended period of downtime, **at least 8 hours** long, during which a character sleeps for at least 6 hours and performs no more than 2 hours of light activity (reading, talking, eating, standing watch).

A character regains:
- **All lost Hit Points**
- **Spent Hit Dice** equal to half their total (minimum 1)
- **All expended spell slots**
- **Features** that recharge on a Long Rest

**Restrictions:**
- A character can benefit from only **one Long Rest per 24 hours**.
- A character must have at least **1 Hit Point** at the start of the rest to gain its benefits.
- If the rest is interrupted by strenuous activity (1 hour of walking, fighting, casting spells, or similar), the characters must begin the rest again.

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#resting_2024)
"""


def render_death_and_dying():
    return """---
tags: [rule, reference]
source: "2024"
---
# Death & Dying

When you drop to 0 Hit Points, you either die outright or fall [[Unconscious]].

## Instant Death

If damage reduces you to 0 HP and there is damage remaining, you die if the remaining damage **equals or exceeds your Hit Point maximum**.

## Falling Unconscious

If you drop to 0 HP and aren't killed outright, you fall [[Unconscious]]. This condition ends if you regain any Hit Points.

## Death Saving Throws

At the **start of each of your turns** while you have 0 HP, you make a Death Saving Throw — a special saving throw (DC 10) not tied to any ability score.

- **Roll 10 or higher:** Success.
- **Roll 9 or lower:** Failure.
- **Roll a natural 20:** You regain 1 Hit Point (you are no longer dying).
- **Roll a natural 1:** Counts as **two failures**.

Track successes and failures separately. **Three successes** = you become Stable. **Three failures** = you die. The totals reset when you regain any HP or become Stable.

## Taking Damage at 0 HP

If you take any damage while at 0 HP, you suffer a Death Save failure. If the damage is from a **Critical Hit**, it counts as **two failures**. If the damage equals or exceeds your HP maximum, you suffer **Instant Death**.

## Stabilizing

A Stable creature doesn't make Death Saves but remains [[Unconscious]] at 0 HP. It regains 1 HP after **1d4 hours**.

A creature can be stabilized with a **DC 10 Wisdom (Medicine) check** or by any effect that restores HP (such as [[Healing Word]] or [[Cure Wounds]]).

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#death%20saving%20throws_2024)
"""


def render_cover():
    return """---
tags: [rule, reference]
source: "2024"
---
# Cover

Walls, trees, creatures, and other obstacles can provide cover during combat, making a target more difficult to harm.

## Half Cover (+2)

A target has **Half Cover** if an obstacle blocks at least half of its body. The obstacle might be a low wall, a large piece of furniture, a narrow tree trunk, or a creature (whether enemy or friend).

A target with Half Cover has a **+2 bonus to AC and Dexterity saving throws**.

## Three-Quarters Cover (+5)

A target has **Three-Quarters Cover** if about three-quarters of it is covered by an obstacle. The obstacle might be a portcullis, an arrow slit, or a thick tree trunk.

A target with Three-Quarters Cover has a **+5 bonus to AC and Dexterity saving throws**.

## Total Cover

A target has **Total Cover** if it is completely concealed by an obstacle. A target with Total Cover **can't be targeted directly** by an attack or a spell, although some spells can reach such a target by including it in an area of effect.

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#cover_2024)
"""


def render_damage_types():
    return """---
tags: [rule, reference]
source: "2024"
---
# Damage Types

Different attacks, spells, and other harmful effects deal different types of damage. Damage types have no rules of their own, but other rules — such as Resistance and Vulnerability — rely on the types.

| Damage Type | Description |
|-------------|-------------|
| **Acid** | Corrosive spray of a black dragon's breath or dissolving enzymes from an ooze |
| **Bludgeoning** | Blunt-force attacks — hammers, falling, constriction |
| **Cold** | Infernal chill of an ice devil's spear or the frigid blast of a white dragon's breath |
| **Fire** | Red dragons breathing flame and many spells conjuring fire |
| **Force** | Pure magical energy focused into a damaging form. [[Magic Missile]] and [[Eldritch Blast]] deal force damage |
| **Lightning** | A [[Lightning Bolt]] spell or a blue dragon's breath |
| **Necrotic** | Damage dealt by certain undead and spells like [[Blight]] that wither life |
| **Piercing** | Puncturing and impaling attacks — spears, monster bites, arrows |
| **Poison** | Venomous stings, toxic gas, or poisonous substances |
| **Psychic** | Mental damage — psionic abilities and certain spells |
| **Radiant** | Searing light of a [[Guiding Bolt]] or the righteous fury of an angel |
| **Slashing** | Swords, axes, and monster claws that cut through flesh |
| **Thunder** | A concussive burst of sound like the [[Shatter]] spell or a thunderous clap |

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#damage%20types_2024)
"""


def render_weapon_properties():
    return """---
tags: [rule, reference]
source: "2024"
---
# Weapon Properties

Many weapons have special properties related to their use, as shown in the [[Weapons Table]].

## Standard Properties

| Property | Description |
|----------|-------------|
| **Ammunition** | You can use this weapon to make a ranged attack only if you have ammunition to fire from it. Each attack expends one piece of ammunition. Drawing ammunition is part of the attack (you need a free hand to load a one-handed weapon). |
| **Finesse** | When making an attack, you use your choice of your Strength or Dexterity modifier for the attack and damage rolls. You must use the same modifier for both rolls. |
| **Heavy** | Creatures that are Small or Tiny have Disadvantage on attack rolls with this weapon. |
| **Light** | When you take the Attack action and attack with a Light weapon in one hand, you can make one extra attack as part of the same action with a different Light weapon in the other hand. You don't add your ability modifier to the damage of the extra attack unless that modifier is negative. |
| **Loading** | You can fire only one piece of ammunition from this weapon when you use an action, bonus action, or reaction to fire it, regardless of the number of attacks you can normally make. |
| **Reach** | This weapon adds 5 feet to your reach when you attack with it and when determining your reach for Opportunity Attacks with it. |
| **Thrown** | You can throw this weapon to make a ranged attack, using the same ability modifier for the attack and damage rolls that you would use for a melee attack. |
| **Two-Handed** | This weapon requires two hands when you attack with it. |
| **Versatile** | This weapon can be used with one or two hands. A damage value in parentheses appears with the property — the damage when the weapon is used with two hands. |

## Mastery Properties (2024)

Each weapon has a Mastery property. You can use a weapon's Mastery property only if you have a feature that lets you do so (typically a class feature).

| Property | Effect |
|----------|--------|
| **Cleave** | If you hit a creature, you can make an attack roll against a second creature within 5 feet of the first, using the same modifier. On a hit, the second creature takes the weapon's damage (no modifier added). |
| **Graze** | If your attack roll misses, the target takes damage equal to your ability modifier (minimum 0) of the weapon's damage type. |
| **Nick** | When you make the extra attack of the Light property, you can make it as part of the Attack action instead of as a Bonus Action. You can still make this extra attack only once per turn. |
| **Push** | If you hit a creature, you can push it up to 10 feet straight away from you if it is Large or smaller. |
| **Sap** | If you hit a creature, that creature has Disadvantage on its next attack roll before the start of your next turn. |
| **Slow** | If you hit a creature, its Speed is reduced by 10 feet until the start of your next turn. If hit more than once, the reduction doesn't exceed 10 feet. |
| **Topple** | If you hit a creature, you can force it to make a Constitution saving throw (DC = 8 + your PB + the modifier used for the attack roll). On a failure, the creature has the [[Prone]] condition. |
| **Vex** | If you hit a creature, you have Advantage on your next attack roll against that creature before the end of your next turn. |

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/variantrules.html#weapon%20mastery_2024)
"""


def render_weapons_table():
    return """---
tags: [rule, reference]
source: "2024"
---
# Weapons Table

## Simple Melee Weapons

| Weapon | Damage | Properties | Weight | Cost | Mastery |
|--------|--------|------------|--------|------|---------|
| [[Club]] | 1d4 bludgeoning | Light | 2 lb. | 1 SP | Slow |
| [[Dagger]] | 1d4 piercing | Finesse, Light, Thrown (20/60) | 1 lb. | 2 GP | Nick |
| [[Greatclub]] | 1d8 bludgeoning | Two-Handed | 10 lb. | 2 SP | Push |
| [[Handaxe]] | 1d6 slashing | Light, Thrown (20/60) | 2 lb. | 5 GP | Vex |
| [[Javelin]] | 1d6 piercing | Thrown (30/120) | 2 lb. | 5 SP | Slow |
| [[Light Hammer]] | 1d4 bludgeoning | Light, Thrown (20/60) | 2 lb. | 2 GP | Nick |
| [[Mace]] | 1d6 bludgeoning | — | 4 lb. | 5 GP | Sap |
| [[Quarterstaff]] | 1d6 bludgeoning | Versatile (1d8) | 4 lb. | 2 SP | Topple |
| [[Sickle]] | 1d4 slashing | Light | 2 lb. | 1 GP | Nick |
| [[Spear]] | 1d6 piercing | Thrown (20/60), Versatile (1d8) | 3 lb. | 1 GP | Sap |

## Simple Ranged Weapons

| Weapon | Damage | Properties | Weight | Cost | Mastery |
|--------|--------|------------|--------|------|---------|
| [[Dart]] | 1d4 piercing | Finesse, Thrown (20/60) | 1/4 lb. | 5 CP | Vex |
| [[Light Crossbow]] | 1d8 piercing | Ammunition (80/320), Loading, Two-Handed | 5 lb. | 25 GP | Slow |
| [[Shortbow]] | 1d6 piercing | Ammunition (80/320), Two-Handed | 2 lb. | 25 GP | Vex |
| [[Sling]] | 1d4 bludgeoning | Ammunition (30/120) | — | 1 SP | Slow |

## Martial Melee Weapons

| Weapon | Damage | Properties | Weight | Cost | Mastery |
|--------|--------|------------|--------|------|---------|
| [[Battleaxe]] | 1d8 slashing | Versatile (1d10) | 4 lb. | 10 GP | Topple |
| [[Flail]] | 1d8 bludgeoning | — | 2 lb. | 10 GP | Sap |
| [[Glaive]] | 1d10 slashing | Heavy, Reach, Two-Handed | 6 lb. | 20 GP | Graze |
| [[Greataxe]] | 1d12 slashing | Heavy, Two-Handed | 7 lb. | 30 GP | Cleave |
| [[Greatsword]] | 2d6 slashing | Heavy, Two-Handed | 6 lb. | 50 GP | Graze |
| [[Halberd]] | 1d10 slashing | Heavy, Reach, Two-Handed | 6 lb. | 20 GP | Cleave |
| [[Lance]] | 1d10 piercing | Heavy, Reach, Two-Handed (special: one-handed while mounted) | 6 lb. | 10 GP | Topple |
| [[Longsword]] | 1d8 slashing | Versatile (1d10) | 3 lb. | 15 GP | Sap |
| [[Maul]] | 2d6 bludgeoning | Heavy, Two-Handed | 10 lb. | 10 GP | Topple |
| [[Morningstar]] | 1d8 piercing | — | 4 lb. | 15 GP | Sap |
| [[Pike]] | 1d10 piercing | Heavy, Reach, Two-Handed | 18 lb. | 5 GP | Push |
| [[Rapier]] | 1d8 piercing | Finesse | 2 lb. | 25 GP | Vex |
| [[Scimitar]] | 1d6 slashing | Finesse, Light | 3 lb. | 25 GP | Nick |
| [[Shortsword]] | 1d6 piercing | Finesse, Light | 2 lb. | 10 GP | Vex |
| [[Trident]] | 1d8 piercing | Thrown (20/60), Versatile (1d10) | 4 lb. | 5 GP | Topple |
| [[War Pick]] | 1d8 piercing | Versatile (1d10) | 2 lb. | 5 GP | Sap |
| [[Warhammer]] | 1d8 bludgeoning | Versatile (1d10) | 2 lb. | 15 GP | Push |
| [[Whip]] | 1d4 slashing | Finesse, Reach | 3 lb. | 2 GP | Slow |

## Martial Ranged Weapons

| Weapon | Damage | Properties | Weight | Cost | Mastery |
|--------|--------|------------|--------|------|---------|
| [[Blowgun]] | 1 piercing | Ammunition (25/100), Loading | 1 lb. | 10 GP | Vex |
| [[Hand Crossbow]] | 1d6 piercing | Ammunition (30/120), Light, Loading | 3 lb. | 75 GP | Vex |
| [[Heavy Crossbow]] | 1d10 piercing | Ammunition (100/400), Heavy, Loading, Two-Handed | 18 lb. | 50 GP | Push |
| [[Longbow]] | 1d8 piercing | Ammunition (150/600), Heavy, Two-Handed | 2 lb. | 50 GP | Slow |
| [[Musket]] | 1d12 piercing | Ammunition (40/120), Loading, Two-Handed | 10 lb. | 500 GP | Slow |
| [[Pistol]] | 1d10 piercing | Ammunition (30/90), Loading | 3 lb. | 250 GP | Vex |
| [[Net]] | — | Thrown (5/15), special | 3 lb. | 1 GP | — |

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/items.html)
"""


def render_armor_table():
    return """---
tags: [rule, reference]
source: "2024"
---
# Armor Table

## Light Armor (requires no Strength)

| Armor | AC | Stealth | Weight | Cost |
|-------|----|---------|--------|------|
| [[Padded Armor\\|Padded]] | 11 + Dex modifier | Disadvantage | 8 lb. | 5 GP |
| [[Leather Armor\\|Leather]] | 11 + Dex modifier | — | 10 lb. | 10 GP |
| [[Studded Leather Armor\\|Studded Leather]] | 12 + Dex modifier | — | 13 lb. | 45 GP |

## Medium Armor (add Dex modifier, max +2)

| Armor | AC | Stealth | Weight | Cost |
|-------|----|---------|--------|------|
| [[Hide Armor\\|Hide]] | 12 + Dex modifier (max 2) | — | 12 lb. | 10 GP |
| [[Chain Shirt]] | 13 + Dex modifier (max 2) | — | 20 lb. | 50 GP |
| [[Scale Mail]] | 14 + Dex modifier (max 2) | Disadvantage | 45 lb. | 50 GP |
| [[Breastplate]] | 14 + Dex modifier (max 2) | — | 20 lb. | 400 GP |
| [[Half Plate Armor\\|Half Plate]] | 15 + Dex modifier (max 2) | Disadvantage | 40 lb. | 750 GP |

## Heavy Armor (Strength requirement, no Dex)

| Armor | AC | Strength | Stealth | Weight | Cost |
|-------|----|----------|---------|--------|------|
| [[Ring Mail]] | 14 | — | Disadvantage | 40 lb. | 30 GP |
| [[Chain Mail]] | 16 | Str 13 | Disadvantage | 55 lb. | 75 GP |
| [[Splint Armor\\|Splint]] | 17 | Str 15 | Disadvantage | 60 lb. | 200 GP |
| [[Plate Armor\\|Plate]] | 18 | Str 15 | Disadvantage | 65 lb. | 1,500 GP |

## Shield

| Shield | AC Bonus | Weight | Cost |
|--------|----------|--------|------|
| [[Shield]] | +2 | 6 lb. | 10 GP |

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/items.html)
"""


def render_tools():
    return """---
tags: [rule, reference]
source: "2024"
---
# Tools

Proficiency with a tool lets you add your Proficiency Bonus to any ability check you make using that tool. Tool use requires the appropriate tools in hand.

## Artisan's Tools

| Tool | Cost | Weight |
|------|------|--------|
| Alchemist's Supplies | 50 GP | 8 lb. |
| Brewer's Supplies | 20 GP | 9 lb. |
| Calligrapher's Supplies | 10 GP | 5 lb. |
| Carpenter's Tools | 8 GP | 6 lb. |
| Cartographer's Tools | 15 GP | 6 lb. |
| Cobbler's Tools | 5 GP | 5 lb. |
| Cook's Utensils | 1 GP | 8 lb. |
| Glassblower's Tools | 30 GP | 5 lb. |
| Jeweler's Tools | 25 GP | 2 lb. |
| Leatherworker's Tools | 5 GP | 5 lb. |
| Mason's Tools | 10 GP | 8 lb. |
| Painter's Supplies | 10 GP | 5 lb. |
| Potter's Tools | 10 GP | 3 lb. |
| Smith's Tools | 20 GP | 8 lb. |
| Tinker's Tools | 50 GP | 10 lb. |
| Weaver's Tools | 1 GP | 5 lb. |
| Woodcarver's Tools | 1 GP | 5 lb. |

## Gaming Sets

| Set | Cost | Weight |
|-----|------|--------|
| Dice Set | 1 SP | — |
| Dragonchess Set | 1 GP | 1/2 lb. |
| Playing Card Set | 5 SP | — |
| Three-Dragon Ante Set | 1 GP | — |

## Musical Instruments

| Instrument | Cost | Weight |
|------------|------|--------|
| Bagpipes | 30 GP | 6 lb. |
| Drum | 6 GP | 3 lb. |
| Dulcimer | 25 GP | 10 lb. |
| Flute | 2 GP | 1 lb. |
| Horn | 3 GP | 2 lb. |
| Lute | 35 GP | 2 lb. |
| Lyre | 30 GP | 2 lb. |
| Pan Flute | 12 GP | 2 lb. |
| Shawm | 2 GP | 1 lb. |
| Viol | 30 GP | 1 lb. |

## Other Tools

| Tool | Cost | Weight |
|------|------|--------|
| Disguise Kit | 25 GP | 3 lb. |
| Forgery Kit | 15 GP | 5 lb. |
| Herbalism Kit | 5 GP | 3 lb. |
| Navigator's Tools | 25 GP | 2 lb. |
| Poisoner's Kit | 50 GP | 2 lb. |
| Thieves' Tools | 25 GP | 1 lb. |

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/items.html)
"""


def render_languages():
    return """---
tags: [rule, reference]
source: "2024"
---
# Languages

Your race, background, and other features might give you proficiency in one or more languages, allowing you to speak and understand those languages.

## Standard Languages

These languages are widely spoken across the worlds of D&D.

| Language | Typical Speakers | Script |
|----------|-----------------|--------|
| Common | Humans, most civilized peoples | Common |
| Common Sign Language | Hearing-impaired or covert communicators | — |
| Dwarvish | Dwarves | Dwarvish |
| Elvish | Elves | Elvish |
| Giant | Ogres, Giants | Dwarvish |
| Gnomish | Gnomes | Dwarvish |
| Goblin | Goblinoids | Dwarvish |
| Halfling | Halflings | Common |
| Orc | Orcs | Dwarvish |

## Rare Languages

These languages are encountered less frequently, and typically only by those with specialized knowledge or backgrounds.

| Language | Typical Speakers | Script |
|----------|-----------------|--------|
| Abyssal | Demons | Infernal |
| Celestial | Celestials | Celestial |
| Deep Speech | Aberrations | — |
| Draconic | Dragons, Dragonborn | Draconic |
| Druidic | Druids (secret) | Elvish |
| Infernal | Devils | Infernal |
| Primordial | Elementals | Dwarvish |
| Sylvan | Fey creatures | Elvish |
| Thieves' Cant | Rogues (secret) | — |
| Undercommon | Underdark traders | Elvish |

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools/languages.html)
"""


RULES_RENDERERS = {
    "Actions in Combat": render_actions_in_combat,
    "Ability Scores": render_ability_scores,
    "Skills": render_skills,
    "Resting": render_resting,
    "Death & Dying": render_death_and_dying,
    "Cover": render_cover,
    "Damage Types": render_damage_types,
    "Weapon Properties": render_weapon_properties,
    "Weapons Table": render_weapons_table,
    "Armor Table": render_armor_table,
    "Tools": render_tools,
    "Languages": render_languages,
}


# ══════════════════════════════════════════════════════════════════════════════
#  GLOSSARY
# ══════════════════════════════════════════════════════════════════════════════

def render_glossary():
    return """---
tags: [glossary, reference]
source: "2024"
---
# Glossary

Quick-reference glossary of key D&D 5e terms.

---

**Advantage** — When you have Advantage on a d20 roll, roll two d20s and use the higher result. If you also have Disadvantage, they cancel out.

**Armor Class (AC)** — The number an attack roll must meet or exceed to hit a creature. See [[Armor Table]] for base AC values.

**Attunement** — Some magic items require you to bond with them before you can use their magical properties. A creature can be attuned to no more than **3 items** at a time.

**Bonus Action** — An additional action on your turn, granted by specific spells, features, or abilities. You can take only **one** Bonus Action per turn.

**Cantrip** — A spell that can be cast at will, without expending a spell slot. See [[Spells]].

**Challenge Rating (CR)** — A measure of how dangerous a monster is. A CR 1 creature is a fair challenge for a party of four 1st-level characters.

**Concentration** — Some spells require you to maintain Concentration to keep their effects active. Taking damage forces a Constitution saving throw (DC 10 or half the damage, whichever is higher). You can concentrate on only **one spell** at a time.

**Condition** — A status effect that modifies a creature's capabilities. See conditions like [[Blinded]], [[Frightened]], [[Prone]], [[Stunned]], and [[Unconscious]].

**Critical Hit** — When you roll a natural 20 on an attack roll, you hit regardless of the target's AC and roll all damage dice twice.

**Difficult Terrain** — Movement through difficult terrain costs **1 extra foot per foot moved** (effectively halving movement).

**Disadvantage** — When you have Disadvantage on a d20 roll, roll two d20s and use the lower result. If you also have Advantage, they cancel out.

**Exhaustion** — A debilitating condition with levels. See [[Exhaustion]].

**Hit Dice** — Dice used to determine your Hit Points. You also spend Hit Dice during a Short Rest to recover HP. See [[Resting]].

**Hit Points (HP)** — A measure of how much damage you can take before falling [[Unconscious]] or dying. See [[Death & Dying]].

**Initiative** — A Dexterity check made at the start of combat to determine turn order.

**Inspiration** — A reward (typically from the DM) that lets you gain Advantage on one d20 roll. In the 2024 rules, rolling a natural 20 on a d20 Test grants Heroic Inspiration.

**Opportunity Attack** — A melee attack you can make as a Reaction when a hostile creature you can see moves out of your reach. See [[Actions in Combat]].

**Proficiency Bonus** — A bonus added to rolls you're proficient in: attack rolls, saving throws, ability checks, and spell DCs. Starts at +2 and scales with level. See [[Skills]].

**Reaction** — A special response triggered by a specific event, such as an [[Opportunity Attacks|Opportunity Attack]]. You can take only **one** Reaction per round (resets at the start of your turn).

**Resistance** — If you have Resistance to a damage type, damage of that type is **halved**. See [[Damage Types]].

**Ritual** — A spell with the Ritual tag can be cast without expending a spell slot, but casting it takes **10 extra minutes**.

**Saving Throw** — A roll to resist spells, traps, poisons, and other effects. DC is set by the source. You add your ability modifier and Proficiency Bonus (if proficient).

**Spell Attack** — An attack roll made when casting certain spells. Uses your spellcasting ability modifier + Proficiency Bonus.

**Spell DC** — The Difficulty Class for saving throws against your spells. Equals **8 + Proficiency Bonus + spellcasting ability modifier**.

**Spell Slot** — A resource expended to cast a spell of 1st level or higher. Higher-level slots can cast lower-level spells (often at greater effect). Recovered on a Long Rest (or Short Rest for some classes). See [[Resting]].

**Vulnerability** — If you have Vulnerability to a damage type, damage of that type is **doubled**. See [[Damage Types]].

---
\U0001f517 [Full Details on 5e.tools](https://5e.tools)
"""


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    dry_run = "--dry-run" in sys.argv

    created = 0
    skipped = 0

    # ── Backgrounds ───────────────────────────────────────────────────────
    print("=== Backgrounds ===")
    for bg in BACKGROUNDS:
        filepath = os.path.join(BACKGROUNDS_DIR, f"{bg['name']}.md")
        content = render_background(bg)
        if write_file(filepath, content, dry_run):
            created += 1
        else:
            skipped += 1

    # ── Rules ─────────────────────────────────────────────────────────────
    print("\n=== Rules ===")
    for name, renderer in RULES_RENDERERS.items():
        filepath = os.path.join(RULES_DIR, f"{name}.md")
        content = renderer()
        if write_file(filepath, content, dry_run):
            created += 1
        else:
            skipped += 1

    # ── Glossary ──────────────────────────────────────────────────────────
    print("\n=== Glossary ===")
    filepath = os.path.join(REFERENCE_ROOT, "Glossary.md")
    content = render_glossary()
    if write_file(filepath, content, dry_run):
        created += 1
    else:
        skipped += 1

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  {'Would create' if dry_run else 'Created'}: {created}")
    print(f"  Skipped (exist): {skipped}")
    print(f"  Total: {created + skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
