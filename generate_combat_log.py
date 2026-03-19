"""
Generate a consolidated combat log from all session recaps.

Extracts Combat Encounters tables and combat-related events from
session recaps into a single Combat Log archive file.
"""

import re

from vault_utils import (VAULT_ROOT, SESSIONS_DIR, DM_DIR,
    parse_session_number, strip_wikilinks, parse_table_row)

OUTPUT = DM_DIR / "Combat Log.md"


def extract_combat_encounters(content, session_num):
    """Extract combat encounters from a session recap."""
    encounters = []

    table_match = re.search(
        r'## Combat Encounters\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n##|\Z)',
        content, re.DOTALL
    )
    if not table_match:
        return encounters

    for line in table_match.group(1).strip().split('\n'):
        cols = parse_table_row(line)
        if len(cols) >= 3:
            enemy = cols[0].strip()
            result = cols[1].strip()
            notable = cols[2].strip() if len(cols) > 2 else ""

            if enemy and enemy != "None" and enemy != "-":
                encounters.append({
                    'session': session_num,
                    'enemy': enemy,
                    'enemy_clean': strip_wikilinks(enemy),
                    'result': result,
                    'notable': notable,
                    'notable_clean': strip_wikilinks(notable),
                })

    return encounters


def extract_combat_events(content, session_num):
    """Extract ### Combat subsection events."""
    events = []
    combat_match = re.search(r'### Combat\n(.*?)(?=\n### |\n## )', content, re.DOTALL)
    if combat_match:
        for line in combat_match.group(1).strip().split('\n'):
            match = re.match(r'^\d+\.\s+(.+)$', line.strip())
            if match:
                events.append({
                    'session': session_num,
                    'event': match.group(1),
                    'event_clean': strip_wikilinks(match.group(1)),
                })
            elif line.strip().startswith('- '):
                text = line.strip()[2:]
                if text and text != "No combat this session":
                    events.append({
                        'session': session_num,
                        'event': text,
                        'event_clean': strip_wikilinks(text),
                    })

    return events


def run():
    session_files = sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)
    if not session_files:
        print("No session recaps found.")
        return

    all_encounters = []
    all_events = []
    sessions_with_combat = 0
    sessions_without_combat = 0

    for session_file in session_files:
        content = session_file.read_text(encoding='utf-8')
        session_num = parse_session_number(session_file)

        encounters = extract_combat_encounters(content, session_num)
        events = extract_combat_events(content, session_num)

        all_encounters.extend(encounters)
        all_events.extend(events)

        if encounters or events:
            sessions_with_combat += 1
        else:
            sessions_without_combat += 1

    # Calculate stats
    wins = sum(1 for e in all_encounters if e['result'].upper() in ('W', 'WIN', 'VICTORY', 'DECEASED'))
    losses = sum(1 for e in all_encounters if e['result'].upper() in ('L', 'LOSS', 'DEFEAT'))
    total = len(all_encounters)

    # Track unique enemies
    unique_enemies = set()
    for e in all_encounters:
        unique_enemies.add(e['enemy_clean'])

    # Build output
    output = """---
aliases: [Combat Log]
tags: [dm, combat]
---

# Combat Log

A complete record of all combat encounters across the campaign.

## Combat Statistics

| Stat | Value |
|------|-------|
"""
    output += f"| Total encounters | {total} |\n"
    output += f"| Wins | {wins} |\n"
    output += f"| Losses | {losses} |\n"
    output += f"| Sessions with combat | {sessions_with_combat} |\n"
    output += f"| Sessions without combat | {sessions_without_combat} |\n"
    output += f"| Unique enemy types | {len(unique_enemies)} |\n"

    output += "\n---\n\n## All Encounters\n\n"
    output += "| Session | Enemy | Result | Notable Moments |\n"
    output += "|---------|-------|--------|----------------|\n"

    for e in all_encounters:
        output += f"| Session {e['session']} | {e['enemy']} | {e['result']} | {e['notable']} |\n"

    if not all_encounters:
        output += "| - | No encounters recorded | - | - |\n"

    output += "\n## Combat Details by Session\n\n"

    # Group events by session
    events_by_session = {}
    for e in all_events:
        events_by_session.setdefault(e['session'], []).append(e)

    encounters_by_session = {}
    for e in all_encounters:
        encounters_by_session.setdefault(e['session'], []).append(e)

    all_combat_sessions = sorted(set(list(events_by_session.keys()) + list(encounters_by_session.keys())))

    for session_num in all_combat_sessions:
        output += f"### Session {session_num}\n\n"

        if session_num in encounters_by_session:
            for enc in encounters_by_session[session_num]:
                output += f"**vs {enc['enemy']}** - Result: {enc['result']}\n\n"
                if enc['notable']:
                    output += f"- {enc['notable']}\n"

        if session_num in events_by_session:
            output += "\n**Combat Events:**\n\n"
            for evt in events_by_session[session_num]:
                output += f"- {evt['event']}\n"

        output += "\n---\n\n"

    # Enemy roster
    output += "## Enemy Roster\n\n"
    output += "All unique enemies encountered:\n\n"
    output += "| Enemy | Sessions | Encounters |\n"
    output += "|-------|----------|------------|\n"

    enemy_counts = {}
    enemy_sessions = {}
    for e in all_encounters:
        name = e['enemy_clean']
        enemy_counts[name] = enemy_counts.get(name, 0) + 1
        enemy_sessions.setdefault(name, set()).add(e['session'])

    for enemy in sorted(enemy_counts.keys()):
        sessions_str = ", ".join(str(s) for s in sorted(enemy_sessions[enemy]))
        output += f"| {enemy} | {sessions_str} | {enemy_counts[enemy]} |\n"

    if not enemy_counts:
        output += "| No enemies encountered yet | - | - |\n"

    OUTPUT.write_text(output, encoding='utf-8')
    print(f"Generated: {OUTPUT}")
    print(f"  {total} encounters across {sessions_with_combat} sessions")
    print(f"  {len(unique_enemies)} unique enemy types")


if __name__ == "__main__":
    run()
