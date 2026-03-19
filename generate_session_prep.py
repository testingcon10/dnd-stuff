"""
Generate a DM session prep file for the next session.

Reads the most recent session recap and extracts:
- Previously On summary
- Open threads
- Active quest status
- Recent NPC encounters
- Party status (HP, resources)
"""

import re
from pathlib import Path

VAULT_ROOT = Path(__file__).parent / "Tenelis"
SESSIONS_DIR = VAULT_ROOT / "02 - Sessions"
QUESTS_DIR = VAULT_ROOT / "03 - Quests"
NPC_DIR = VAULT_ROOT / "04 - NPCs"
DM_DIR = VAULT_ROOT / "08 - DM"


def parse_session_number(filepath):
    """Extract session number from filename."""
    match = re.search(r'Session\s+(\d+)', filepath.name)
    return int(match.group(1)) if match else 0


def get_latest_sessions(n=2):
    """Get the N most recent session recap files."""
    files = sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)
    return files[-n:] if len(files) >= n else files


def extract_section(content, heading, level=2):
    """Extract content under a markdown heading."""
    prefix = '#' * level
    pattern = rf'^{prefix}\s+{re.escape(heading)}\s*\n(.*?)(?=\n{prefix}\s+|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_subsection(content, heading, level=3):
    """Extract content under a ### heading."""
    return extract_section(content, heading, level)


def get_active_quests():
    """Get all active quest summaries."""
    quests = []
    for f in QUESTS_DIR.glob("*.md"):
        content = f.read_text(encoding='utf-8')
        # Check status
        status_match = re.search(r'^status:\s*(.+)$', content, re.MULTILINE)
        if status_match and status_match.group(1).strip() == 'active':
            # Get unchecked objectives
            objectives = re.findall(r'- \[ \] (.+)', content)
            quests.append({
                'name': f.stem,
                'objectives': objectives,
            })
    return quests


def get_recent_npcs(content):
    """Extract NPC encounter table from session recap."""
    table_match = re.search(
        r'## NPCs Encountered\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    if not table_match:
        return []

    npcs = []
    for line in table_match.group(1).strip().split('\n'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) >= 4 and cols[0].strip():
            npcs.append({
                'name': re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', r'\1', cols[0]),
                'location': re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', r'\1', cols[1]),
                'disposition': cols[2],
                'notes': cols[3],
            })
    return npcs


def get_open_threads(content):
    """Extract open threads from session recap."""
    section = extract_section(content, "Open Threads")
    if not section:
        return []
    threads = []
    for line in section.split('\n'):
        match = re.match(r'- \[[ x]\] (.+)', line.strip())
        if match:
            threads.append(match.group(1))
    return threads


def run():
    DM_DIR.mkdir(parents=True, exist_ok=True)

    sessions = get_latest_sessions(2)
    if not sessions:
        print("No session recaps found.")
        return

    latest = sessions[-1]
    latest_content = latest.read_text(encoding='utf-8')
    latest_num = parse_session_number(latest)
    next_num = latest_num + 1

    # Extract summary from latest session
    summary = extract_section(latest_content, "Summary")
    open_threads = get_open_threads(latest_content)
    recent_npcs = get_recent_npcs(latest_content)
    active_quests = get_active_quests()

    # Extract key events
    story_events = extract_subsection(latest_content, "Story")

    # Build the prep file
    output = f"""---
aliases: []
tags: [dm, session-prep]
session_number: {next_num}
prep_date:
---

# Session {next_num} Prep

## Previously On (Session {latest_num})

{summary}

## Open Threads

"""

    if open_threads:
        for thread in open_threads:
            output += f"- [ ] {thread}\n"
    else:
        output += "- [ ] No open threads recorded\n"

    output += f"""
## Active Quests

"""

    if active_quests:
        for quest in active_quests:
            output += f"### [[{quest['name']}]]\n\n"
            if quest['objectives']:
                output += "**Next objectives:**\n"
                for obj in quest['objectives'][:3]:
                    output += f"- [ ] {obj}\n"
            output += "\n"
    else:
        output += "No active quests.\n"

    output += f"""## Recent NPC Status

| NPC | Last Location | Disposition | Last Seen |
|-----|---------------|-------------|-----------|
"""

    if recent_npcs:
        for npc in recent_npcs:
            output += f"| [[{npc['name']}]] | {npc['location']} | {npc['disposition']} | Session {latest_num} |\n"

    output += f"""
## Planned Encounters

| Encounter | Location | Difficulty | Enemies | Notes |
|-----------|----------|------------|---------|-------|
|           |          |            |         |       |

## NPC Appearances

| NPC | Location | Purpose | Key Info to Reveal |
|-----|----------|---------|--------------------|
|     |          |         |                    |

## Plot Hooks to Drop

- [ ]

## Loot & Rewards

| Item | Rarity | Where Found | Intended For |
|------|--------|-------------|--------------|
|      |        |             |              |

**Gold:**

## DM Notes

%% Private notes, contingency plans, branching storylines %%

"""

    output_file = DM_DIR / f"Session {next_num} Prep.md"
    output_file.write_text(output, encoding='utf-8')
    print(f"Generated: {output_file}")
    print(f"  Based on Session {latest_num} recap")
    print(f"  {len(open_threads)} open threads carried forward")
    print(f"  {len(active_quests)} active quests with objectives")
    print(f"  {len(recent_npcs)} recent NPCs listed")


if __name__ == "__main__":
    run()
