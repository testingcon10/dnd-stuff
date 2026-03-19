"""
Generate per-character journals from session recaps.

Extracts each PC's key moments, quotes, and developments from all
session recaps and updates the ## Journal section in each character sheet.
"""

import re
from pathlib import Path
from collections import defaultdict

VAULT_ROOT = Path(__file__).parent / "Tenelis"
SESSIONS_DIR = VAULT_ROOT / "02 - Sessions"
PARTY_DIR = VAULT_ROOT / "01 - Party"

PARTY = {
    "Netanyahu D. Kirkuenly": {
        "aliases": ["Net", "Netanyahu"],
        "player": "Conor",
    },
    "Booker Locke": {
        "aliases": ["Booker"],
        "player": "Tony",
    },
    "Old Shell": {
        "aliases": [],
        "player": "Erik",
    },
    "Cassius Bellona": {
        "aliases": ["Cassius"],
        "player": "Jake",
    },
    "Ryan-Nigamus": {
        "aliases": [],
        "player": "Nigamus",
    },
}


def parse_session_number(filepath):
    match = re.search(r'Session\s+(\d+)', filepath.name)
    return int(match.group(1)) if match else 0


def strip_wikilinks(text):
    return re.sub(r'\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]', lambda m: m.group(2) or m.group(1), text)


def char_mentioned(text, char_name, aliases):
    """Check if a character is mentioned in text."""
    text_clean = strip_wikilinks(text)
    names_to_check = [char_name] + aliases
    for name in names_to_check:
        if name.lower() in text_clean.lower():
            return True
    return False


def extract_character_moments(content, session_num, char_name, aliases):
    """Extract all mentions and moments for a specific character."""
    moments = {
        'highlights': [],
        'character_moments': [],
        'quotes': [],
        'combat': [],
        'loot': [],
    }

    # Highlights table
    highlights_match = re.search(
        r'## Highlights\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n##|\Z)',
        content, re.DOTALL
    )
    if highlights_match:
        for line in highlights_match.group(1).strip().split('\n'):
            safe_line = re.sub(r'\\\|', '\x00', line)
            cols = [c.strip().replace('\x00', '|') for c in safe_line.split('|')[1:-1]]
            if len(cols) >= 2:
                player = strip_wikilinks(cols[0]).strip()
                moment = strip_wikilinks(cols[1]).strip()
                if char_mentioned(player, char_name, aliases):
                    moments['highlights'].append(moment)

    # Character Moments section
    char_section = re.search(
        r'### Party\n(.*?)(?=\n### NPCs|\n## )',
        content, re.DOTALL
    )
    if char_section:
        for line in char_section.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('- ') and char_mentioned(line, char_name, aliases):
                moments['character_moments'].append(strip_wikilinks(line[2:]))

    # Memorable Quotes
    quotes_match = re.search(r'## Memorable Quotes\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if quotes_match:
        for line in quotes_match.group(1).strip().split('\n'):
            if char_mentioned(line, char_name, aliases):
                # Clean up quote formatting
                quote = line.strip().lstrip('> ').strip()
                if quote:
                    moments['quotes'].append(quote)

    # Loot
    loot_match = re.search(
        r'## Loot Acquired\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n\*\*Gold|\n##|\Z)',
        content, re.DOTALL
    )
    if loot_match:
        for line in loot_match.group(1).strip().split('\n'):
            if char_mentioned(line, char_name, aliases):
                cols = [c.strip() for c in line.split('|')[1:-1]]
                if len(cols) >= 3 and cols[0].strip():
                    item = strip_wikilinks(cols[0]).strip()
                    moments['loot'].append(item)

    return moments


def build_journal_section(all_moments):
    """Build the ## Journal section content."""
    output = "## Journal\n\n"

    has_any = False
    for session_num in sorted(all_moments.keys()):
        moments = all_moments[session_num]
        has_content = any(moments[k] for k in moments)
        if not has_content:
            continue

        has_any = True
        output += f"### Session {session_num}\n\n"

        if moments['highlights']:
            output += "**Highlight:**\n"
            for h in moments['highlights']:
                output += f"- {h}\n"
            output += "\n"

        if moments['character_moments']:
            output += "**Key Moments:**\n"
            for m in moments['character_moments']:
                output += f"- {m}\n"
            output += "\n"

        if moments['quotes']:
            output += "**Memorable Quotes:**\n"
            for q in moments['quotes']:
                output += f"> {q}\n\n"

        if moments['loot']:
            output += "**Loot Acquired:**\n"
            for item in moments['loot']:
                output += f"- {item}\n"
            output += "\n"

        output += "---\n\n"

    if not has_any:
        output += "\n"

    return output


def update_character_sheet(char_name, all_moments):
    """Update the ## Journal section in a character sheet file."""
    sheet_file = PARTY_DIR / f"{char_name}.md"
    if not sheet_file.exists():
        print(f"  WARNING: {sheet_file.name} not found, skipping")
        return False

    content = sheet_file.read_text(encoding='utf-8')
    new_journal = build_journal_section(all_moments)

    # Replace existing ## Journal section (everything from ## Journal to ## Notes)
    journal_match = re.search(
        r'## Journal\n.*?(?=## Notes)',
        content, re.DOTALL
    )
    if journal_match:
        content = content[:journal_match.start()] + new_journal + content[journal_match.end():]
    else:
        # No journal section yet - insert before ## Notes
        notes_match = re.search(r'## Notes', content)
        if notes_match:
            content = content[:notes_match.start()] + new_journal + content[notes_match.start():]
        else:
            content += "\n" + new_journal + "## Notes\n"

    sheet_file.write_text(content, encoding='utf-8')
    return True


def run():
    session_files = sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)
    if not session_files:
        print("No session recaps found.")
        return

    updated = 0
    for char_name, info in PARTY.items():
        all_moments = {}

        for session_file in session_files:
            content = session_file.read_text(encoding='utf-8')
            session_num = parse_session_number(session_file)
            moments = extract_character_moments(content, session_num, char_name, info['aliases'])
            all_moments[session_num] = moments

        if update_character_sheet(char_name, all_moments):
            session_count = sum(1 for m in all_moments.values() if any(m[k] for k in m))
            print(f"  {char_name}: {session_count} sessions with content")
            updated += 1

    print(f"\nUpdated {updated} character sheets")


if __name__ == "__main__":
    run()
