"""
Generate per-character journals from session recaps.

Extracts each PC's key moments, quotes, and developments from all
session recaps and creates/updates journal files in 01 - Party/.
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


def generate_journal(char_name, info, all_moments):
    """Generate a character journal markdown file."""
    output = f"""---
aliases: []
tags: [journal, party]
character: "{char_name}"
player: "{info['player']}"
---

# {char_name} - Journal

A session-by-session record of **{char_name}**'s key moments, developments, and personal arc.

**Player:** {info['player']}

---

"""

    for session_num in sorted(all_moments.keys()):
        moments = all_moments[session_num]
        has_content = any(moments[k] for k in moments)
        if not has_content:
            continue

        output += f"## Session {session_num}\n\n"

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

    output += "## Character Arc Notes\n\n"
    output += "%% Track character development, relationships, and personal goals here %%\n"

    return output


def run():
    session_files = sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)
    if not session_files:
        print("No session recaps found.")
        return

    for char_name, info in PARTY.items():
        all_moments = {}

        for session_file in session_files:
            content = session_file.read_text(encoding='utf-8')
            session_num = parse_session_number(session_file)
            moments = extract_character_moments(content, session_num, char_name, info['aliases'])
            all_moments[session_num] = moments

        journal = generate_journal(char_name, info, all_moments)
        output_file = PARTY_DIR / f"{char_name} - Journal.md"
        output_file.write_text(journal, encoding='utf-8')

        session_count = sum(1 for m in all_moments.values() if any(m[k] for k in m))
        print(f"  {char_name}: {session_count} sessions with content")

    print(f"\nGenerated {len(PARTY)} character journals")


if __name__ == "__main__":
    run()
