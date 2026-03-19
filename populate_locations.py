"""
Populate location files with session event data.

Scans session recaps for location mentions, then updates location files
with session log entries and key NPCs found at each location.
"""

import re
from pathlib import Path
from collections import defaultdict

VAULT_ROOT = Path(__file__).parent / "Tenelis"
SESSIONS_DIR = VAULT_ROOT / "02 - Sessions"
LOCATIONS_DIR = VAULT_ROOT / "06 - World" / "Locations"


def parse_session_number(filepath):
    match = re.search(r'Session\s+(\d+)', filepath.name)
    return int(match.group(1)) if match else 0


def extract_wikilinks(text):
    return set(re.findall(r'\[\[([^\]|#]+?)(?:\|[^\]]+?)?\]\]', text))


def get_location_files():
    """Get all location file stems and paths."""
    locations = {}
    for f in LOCATIONS_DIR.rglob("*.md"):
        content = f.read_text(encoding='utf-8')
        # Get name from stem
        locations[f.stem] = f
        # Also check aliases
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            for alias in re.finditer(r'^\s+-\s+"?([^"\n]+)"?\s*$', fm_match.group(1), re.MULTILINE):
                alias_name = alias.group(1).strip()
                if alias_name:
                    locations[alias_name] = f
    return locations


def extract_npc_table(content):
    """Extract NPCs Encountered table from session recap."""
    table_match = re.search(
        r'## NPCs Encountered\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n##|\Z)',
        content, re.DOTALL
    )
    if not table_match:
        return []
    npcs = []
    for line in table_match.group(1).strip().split('\n'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) >= 4 and cols[0].strip():
            npc_name = re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', r'\1', cols[0]).strip()
            location = re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', r'\1', cols[1]).strip()
            disposition = cols[2].strip()
            notes = cols[3].strip()
            npcs.append({
                'name': npc_name,
                'location': location,
                'disposition': disposition,
                'notes': notes,
            })
    return npcs


def extract_session_events(content, location_names):
    """Find events mentioning specific locations in a session recap."""
    events = defaultdict(list)

    # Check Key Events section
    key_events_match = re.search(r'## Key Events\n(.*?)(?=\n## )', content, re.DOTALL)
    if key_events_match:
        section = key_events_match.group(1)
        for line in section.split('\n'):
            line = line.strip()
            match = re.match(r'^\d+\.\s+(.+)$', line)
            if match:
                event_text = match.group(1)
                links = extract_wikilinks(event_text)
                for link in links:
                    if link in location_names:
                        events[link].append(event_text)

    # Check Summary
    summary_match = re.search(r'## Summary\n\n(.+?)(?=\n## )', content, re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()
        links = extract_wikilinks(summary)
        for link in links:
            if link in location_names and link not in events:
                # Extract sentence containing the location
                for sentence in re.split(r'(?<=[.!?])\s+', summary):
                    if link in sentence or f'[[{link}' in sentence:
                        events[link].append(sentence.strip())
                        break

    return events


def update_session_log(filepath, session_num, events_text):
    """Add a session log entry to a location file if not already present."""
    content = filepath.read_text(encoding='utf-8')

    # Check if this session is already logged
    if f'Session {session_num}' in content:
        return False

    # Find the Session Log table
    log_match = re.search(r'## Session Log\n\n(\|.*?\|\n\|[-\s|]+\|\n)(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not log_match:
        return False

    header = log_match.group(1)
    existing = log_match.group(2).strip()

    # Build summary
    summary = ". ".join(events_text[:2])
    if len(summary) > 200:
        summary = summary[:197] + "..."

    new_row = f"| Session {session_num} | {summary} |"

    if existing and existing != '|         |        |':
        new_table = f"{header}{existing}\n{new_row}"
    else:
        new_table = f"{header}{new_row}"

    # Replace old table
    old_section = log_match.group(0)
    new_section = f"## Session Log\n\n{new_table}"
    updated = content.replace(old_section, new_section)

    filepath.write_text(updated, encoding='utf-8')
    return True


def update_key_npcs(filepath, npcs_at_location, session_num):
    """Add NPCs to a location's Key NPCs table."""
    content = filepath.read_text(encoding='utf-8')

    for npc in npcs_at_location:
        # Check if NPC already in the table
        npc_escaped = re.escape(npc['name'])
        if re.search(npc_escaped, content):
            continue

        # Find Key NPCs table
        npc_match = re.search(
            r'(## Key NPCs\n\n\|.*?\|\n\|[-\s|]+\|\n)(.*?)(?=\n##|\Z)',
            content, re.DOTALL
        )
        if not npc_match:
            continue

        header = npc_match.group(1)
        existing = npc_match.group(2).strip()

        new_row = f"| [[{npc['name']}]] | {npc['disposition']} | {npc['notes']} |"

        if existing and existing != '|     |      |       |':
            new_table = f"{header}{existing}\n{new_row}"
        else:
            new_table = f"{header}{new_row}"

        old_section = npc_match.group(0)
        new_section = f"## Key NPCs\n\n{new_table}"
        content = content.replace(old_section, new_section)
        filepath.write_text(content, encoding='utf-8')


def run():
    location_files = get_location_files()
    location_names = set(location_files.keys())

    session_files = sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)
    if not session_files:
        print("No session recaps found.")
        return

    updates = 0
    npc_adds = 0

    for session_file in session_files:
        content = session_file.read_text(encoding='utf-8')
        session_num = parse_session_number(session_file)

        # Extract events per location
        events = extract_session_events(content, location_names)

        # Extract NPCs per location
        session_npcs = extract_npc_table(content)

        for location_name, event_texts in events.items():
            filepath = location_files.get(location_name)
            if filepath and update_session_log(filepath, session_num, event_texts):
                updates += 1
                print(f"  [Session {session_num}] Updated: {location_name}")

        # Update NPCs at locations
        for npc in session_npcs:
            loc_name = npc['location']
            filepath = location_files.get(loc_name)
            if filepath:
                update_key_npcs(filepath, [npc], session_num)

    print(f"\nDone: {updates} session log entries added")


if __name__ == "__main__":
    run()
