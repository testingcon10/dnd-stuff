---
aliases: ["Home", "Dashboard"]
tags: [dashboard]
---

# Tenelis Campaign

> [!abstract] Welcome
> Campaign dashboard for the **Tenelis** D&D 5e campaign. Use the links below to navigate the vault.

---

## Party

```dataview
TABLE character_name AS "Character", player AS "Player", race AS "Race", class AS "Class", level AS "Level"
FROM "01 - Party"
WHERE character_name != ""
SORT file.name ASC
```

> [!tip] Character Sheets
> [[Character Sheet 1]] · [[Character Sheet 2]] · [[Character Sheet 3]] · [[Character Sheet 4]] · [[Character Sheet 5]]

---

## Sessions

```dataview
TABLE session_number AS "Session #", session_date AS "Date", players_present AS "Players Present"
FROM "02 - Sessions"
SORT session_number DESC
```

> *Create new session recaps using the **Template - Session Recap** template (Ctrl+T).*

---

## Active Quests

```dataview
TABLE WITHOUT ID file.link AS "Quest", quest_giver AS "Quest Giver", location AS "Location", reward AS "Reward"
FROM "03 - Quests"
WHERE status = "active"
SORT file.name ASC
```

---

## NPCs

```dataview
TABLE race AS "Race", location AS "Location", status AS "Status", attitude AS "Attitude"
FROM "04 - NPCs"
SORT file.name ASC
```

---

## Loot & Gold

> [!treasure] Loot Tracking
> [[Loot Log]] — Master inventory and gold tracking for the party.

---

## World

> [!map] World Building
> **[[06 - World/World Map|World Map]]** · **[[06 - World/Locations/|Locations]]** · **[[06 - World/Factions/|Factions]]** · **[[06 - World/Lore/|Lore]]**
>
> *Add world-building notes as the campaign unfolds.*

---

## Quick Reference

> [!book] Player Reference (5e)
>
> **Classes:** [[Barbarian]] · [[Bard]] · [[Cleric]] · [[Druid]] · [[Fighter]] · [[Monk]] · [[Paladin]] · [[Ranger]] · [[Rogue]] · [[Sorcerer]] · [[Warlock]] · [[Wizard]]
>
> **Races:** [[Dwarf]] · [[Elf]] · [[Halfling]] · [[Human]] · [[Dragonborn]] · [[Gnome]] · [[Half-Elf]] · [[Half-Orc]] · [[Tiefling]]
>
> **Conditions:** [[Blinded]] · [[Charmed]] · [[Deafened]] · [[Exhaustion]] · [[Frightened]] · [[Grappled]] · [[Incapacitated]] · [[Invisible]] · [[Paralyzed]] · [[Petrified]] · [[Poisoned]] · [[Prone]] · [[Restrained]] · [[Stunned]] · [[Unconscious]]
>
> **Backgrounds:** [[Acolyte]] · [[Artisan]] · [[Charlatan]] · [[Criminal]] · [[Entertainer]] · [[Farmer]] · [[Guard]] · [[Guide]] · [[Hermit]] · [[Merchant]] · [[Noble]] · [[Sage]] · [[Sailor]] · [[Scribe]] · [[Soldier]] · [[Wayfarer]]
>
> **Rules:** [[Actions in Combat]] · [[Ability Scores]] · [[Skills]] · [[Resting]] · [[Death & Dying]] · [[Cover]] · [[Damage Types]] · [[Weapon Properties]] · [[Weapons Table]] · [[Armor Table]] · [[Tools]] · [[Languages]] · [[Glossary]]

> [!example] Popular Spells
>
> **Cantrips:** [[Eldritch Blast]] · [[Fire Bolt]] · [[Light]] · [[Mage Hand]] · [[Minor Illusion]] · [[Prestidigitation]] · [[Sacred Flame]] · [[Thaumaturgy]]
>
> **1st Level:** [[Bless]] · [[Cure Wounds]] · [[Detect Magic]] · [[Faerie Fire]] · [[Guiding Bolt]] · [[Healing Word]] · [[Hunter's Mark]] · [[Mage Armor]] · [[Magic Missile]] · [[Shield]]
>
> **2nd Level:** [[Aid]] · [[Darkness]] · [[Hold Person]] · [[Lesser Restoration]] · [[Misty Step]] · [[Pass Without Trace]] · [[Shatter]] · [[Silence]] · [[Spiritual Weapon]]
>
> **3rd Level:** [[Counterspell]] · [[Dispel Magic]] · [[Fireball]] · [[Fly]] · [[Haste]] · [[Hypnotic Pattern]] · [[Lightning Bolt]] · [[Revivify]] · [[Spirit Guardians]] · [[Tongues]]
>
> **4th Level:** [[Banishment]] · [[Death Ward]] · [[Dimension Door]] · [[Greater Invisibility]] · [[Polymorph]] · [[Wall of Fire]]
>
> **5th Level:** [[Greater Restoration]] · [[Mass Cure Wounds]] · [[Raise Dead]] · [[Teleportation Circle]] · [[Wall of Force]]

> [!gear] Magic Items
> [[Potion of Healing]] · [[Bag of Holding]] · [[Cloak of Protection]] · [[Boots of Elvenkind]] · [[Gauntlets of Ogre Power]] · [[Goggles of Night]] · [[Ring of Protection]] · [[Weapon +1]] · [[Flame Tongue]] · [[Armor +1]] · [[Ring of Spell Storing]] · [[Cape of the Mountebank]] · [[Amulet of Health]] · [[Armor +2]] · [[Staff of Power]] · [[Cloak of Displacement]] · [[Belt of Giant Strength (Hill)]] · [[Vorpal Sword]]

> [!star] Popular [[Feats]]
> [[Alert]] · [[Crossbow Expert]] · [[Defensive Duelist]] · [[Great Weapon Master]] · [[Inspiring Leader]] · [[Lucky]] · [[Mage Slayer]] · [[Mobile]] · [[Observant]] · [[Polearm Master]] · [[Resilient]] · [[Sentinel]] · [[Sharpshooter]] · [[Tough]] · [[War Caster]]

---

> [!info] Templates
> Use **Ctrl+T** (or Cmd+T on Mac) to insert a template when creating new notes.
> Available templates: Character Sheet, Session Recap, Quest, NPC, Spell, Item, Feat, Location, Map
