"""Shared utilities for Tenelis vault scripts."""

import re
from pathlib import Path

VAULT_ROOT = Path(__file__).parent / "Tenelis"
SESSIONS_DIR = VAULT_ROOT / "02 - Sessions"
PARTY_DIR = VAULT_ROOT / "01 - Party"
NPC_DIR = VAULT_ROOT / "04 - NPCs"
LOCATIONS_DIR = VAULT_ROOT / "06 - World" / "Locations"
LORE_DIR = VAULT_ROOT / "06 - World" / "Lore"
DM_DIR = VAULT_ROOT / "08 - DM"

PARTY = {
    "Netanyahu D. Kirkuenly": {"aliases": ["Net", "Netanyahu"], "player": "Conor"},
    "Booker Locke": {"aliases": ["Booker"], "player": "Tony"},
    "Old Shell": {"aliases": [], "player": "Erik"},
    "Cassius Bellona": {"aliases": ["Cassius"], "player": "Jake"},
    "Ryan-Nigamus": {"aliases": [], "player": "Nigamus"},
}


def parse_session_number(filepath):
    """Extract session number from a filepath like 'Session 5 Recap.md'."""
    match = re.search(r'Session\s+(\d+)', Path(filepath).name)
    return int(match.group(1)) if match else 0


def get_session_files():
    """Get all session recap files sorted by session number."""
    return sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)


def extract_wikilinks(text):
    """Extract all wikilink targets from text, ignoring display aliases and anchors."""
    return set(re.findall(r'\[\[([^\]|#]+?)(?:\|[^\]]+?)?\]\]', text))


def strip_wikilinks(text):
    """Replace [[Target|Display]] with Display, [[Target]] with Target."""
    return re.sub(r'\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]', lambda m: m.group(2) or m.group(1), text)


def parse_frontmatter(content):
    """Extract frontmatter dict-like string from markdown content. Returns (frontmatter_str, body)."""
    match = re.match(r'^---\n(.*?)\n---\n?', content, re.DOTALL)
    if not match:
        return "", content
    end = match.end()
    return match.group(1), content[end:]


def extract_section(content, heading, level=2):
    """Extract content under a markdown heading. Returns the text between this heading and the next same-level heading."""
    prefix = '#' * level
    pattern = rf'^{prefix}\s+{re.escape(heading)}\s*\n(.*?)(?=^{prefix}\s+|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_npc_table(content):
    """Extract NPCs Encountered table rows from a session recap."""
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
            npcs.append({
                'name': strip_wikilinks(cols[0]).strip(),
                'location': strip_wikilinks(cols[1]).strip(),
                'disposition': cols[2].strip(),
                'notes': cols[3].strip(),
            })
    return npcs


def parse_table_row(line):
    """Parse a markdown table row handling escaped pipes."""
    safe = re.sub(r'\\\|', '\x00', line)
    return [c.strip().replace('\x00', '|') for c in safe.split('|')[1:-1]]


def char_mentioned(text, char_name, aliases):
    """Check if a character is mentioned in text (case-insensitive)."""
    text_clean = strip_wikilinks(text).lower()
    for name in [char_name] + aliases:
        if name.lower() in text_clean:
            return True
    return False
