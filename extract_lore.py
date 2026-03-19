"""
Extract lore from session recaps and update/create lore files in 06 - World/Lore/.

Parses ### Lore sections from session recaps, groups related lore entries,
and either creates new lore files or appends to existing ones.
"""

import re

from vault_utils import VAULT_ROOT, SESSIONS_DIR, LORE_DIR, parse_session_number, extract_wikilinks


def parse_lore_section(content, session_num):
    """Extract individual lore entries from a session recap's ### Lore section."""
    lore_match = re.search(
        r'### Lore\n(.*?)(?=\n###|\n## )',
        content,
        re.DOTALL
    )
    if not lore_match:
        return []

    lore_text = lore_match.group(1).strip()
    entries = []

    for line in lore_text.split('\n'):
        line = line.strip()
        match = re.match(r'^\d+\.\s+(.+)$', line)
        if match:
            entry_text = match.group(1)
            wikilinks = extract_wikilinks(entry_text)
            entries.append({
                'text': entry_text,
                'session': session_num,
                'entities': wikilinks,
            })

    return entries


def categorize_lore_entry(entry):
    """Determine which lore topic(s) an entry relates to based on entities."""
    text_lower = entry['text'].lower()
    entities_lower = [e.lower() for e in entry['entities']]

    categories = []

    # Check for known lore topics
    if 'mana virus' in text_lower:
        categories.append('Mana Virus')
    if 'three sisters' in text_lower or any(
        name in entities_lower for name in ['nahara', 'ayla', 'sophie']
    ):
        categories.append('The Three Sisters')
    if any(word in text_lower for word in ['catacomb', 'underground', 'tunnel', 'cave']):
        categories.append('Underground Networks')
    if 'avo red' in text_lower or 'knights of drayik' in text_lower:
        categories.append('Knights of Drayik')
    if any(word in text_lower for word in ['church', 'father ellen', 'church of the daughter']):
        categories.append('Church of the Daughter')
    if 'kenku' in entities_lower or 'kenku' in text_lower:
        if any(word in text_lower for word in ['family', 'father', 'sister', 'brother', 'son', 'daughter', 'lineage']):
            categories.append('Kenku Bloodlines')
        elif not categories:
            categories.append('Kenku')
    if any(faction in text_lower for faction in ['the golds', 'avian brotherhood', 'the feints', 'elven mafia', 'criminal', 'faction']):
        if 'Drayik Criminal Syndicate' not in categories:
            categories.append('Drayik Criminal Syndicate')
    if 'human trafficking' in text_lower:
        categories.append('Drayik Criminal Syndicate')

    # Skip entries explicitly marked as unimportant
    if not categories:
        skip_phrases = ['nothing of major note', 'nothing notable', 'no new information']
        if any(phrase in text_lower for phrase in skip_phrases):
            return []

    return categories


def load_existing_lore(filepath):
    """Read existing lore file and return its content."""
    if filepath.exists():
        return filepath.read_text(encoding='utf-8')
    return None


def get_existing_session_entries(content, session_num):
    """Check if a session's lore has already been extracted into this file."""
    pattern = rf'Session {session_num}\b'
    return bool(re.search(pattern, content))


def create_lore_file(topic, entries):
    """Create a new lore file with extracted entries."""
    safe_name = topic
    filepath = LORE_DIR / f"{safe_name}.md"

    # Build session-grouped entries
    session_sections = {}
    for entry in entries:
        session_sections.setdefault(entry['session'], []).append(entry['text'])

    content = f"""---
aliases:
  - {topic}
tags:
  - lore
---

# {topic}

## Overview

"""

    # Add entries grouped by session
    content += "## Session Discoveries\n\n"
    for session_num in sorted(session_sections.keys()):
        content += f"### Session {session_num}\n\n"
        for text in session_sections[session_num]:
            # Strip wikilink formatting for cleaner prose
            content += f"- {text}\n"
        content += "\n"

    content += "## Notes\n"

    filepath.write_text(content, encoding='utf-8')
    return filepath


def append_to_lore_file(filepath, entries, existing_content):
    """Append new session entries to an existing lore file."""
    new_sessions = {}
    for entry in entries:
        if not get_existing_session_entries(existing_content, entry['session']):
            new_sessions.setdefault(entry['session'], []).append(entry['text'])

    if not new_sessions:
        return False

    # Find the ## Notes section to insert before it
    notes_match = re.search(r'\n## Notes', existing_content)
    if notes_match:
        insert_pos = notes_match.start()
    else:
        insert_pos = len(existing_content)

    # Check if Session Discoveries section exists
    has_discoveries = '## Session Discoveries' in existing_content

    new_content = ""
    if not has_discoveries:
        new_content += "\n## Session Discoveries\n\n"

    for session_num in sorted(new_sessions.keys()):
        new_content += f"### Session {session_num}\n\n"
        for text in new_sessions[session_num]:
            new_content += f"- {text}\n"
        new_content += "\n"

    updated = existing_content[:insert_pos] + new_content + existing_content[insert_pos:]
    filepath.write_text(updated, encoding='utf-8')
    return True


def run():
    """Main extraction pipeline."""
    LORE_DIR.mkdir(parents=True, exist_ok=True)

    # Parse all session recaps
    all_entries = []
    session_files = sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)

    if not session_files:
        print("No session recaps found.")
        return

    for session_file in session_files:
        content = session_file.read_text(encoding='utf-8')
        session_num = parse_session_number(session_file)
        entries = parse_lore_section(content, session_num)
        all_entries.extend(entries)
        if entries:
            print(f"  Session {session_num}: {len(entries)} lore entries found")

    if not all_entries:
        print("No lore entries found in any session recap.")
        return

    # Categorize and group entries by lore topic
    topic_entries = {}
    for entry in all_entries:
        categories = categorize_lore_entry(entry)
        for cat in categories:
            topic_entries.setdefault(cat, []).append(entry)

    print(f"\nFound {len(all_entries)} total lore entries across {len(topic_entries)} topics:\n")

    created = []
    updated = []
    skipped = []

    for topic, entries in sorted(topic_entries.items()):
        filepath = LORE_DIR / f"{topic}.md"
        existing = load_existing_lore(filepath)

        if existing is None:
            create_lore_file(topic, entries)
            created.append(topic)
            print(f"  [CREATED] {topic}.md ({len(entries)} entries)")
        else:
            if append_to_lore_file(filepath, entries, existing):
                updated.append(topic)
                print(f"  [UPDATED] {topic}.md (new entries appended)")
            else:
                skipped.append(topic)
                print(f"  [SKIPPED] {topic}.md (entries already present)")

    print(f"\nDone: {len(created)} created, {len(updated)} updated, {len(skipped)} skipped")


if __name__ == "__main__":
    run()
