"""
Vault Health Dashboard generator.

Scans the vault for:
- Stub files (under N lines of content)
- NPCs missing portraits
- Quests with missing frontmatter fields
- Locations without descriptions
- Broken wikilinks (target file doesn't exist)
- Orphaned files (no inbound links)

Outputs to Tenelis/00 - Vault Health.md
"""

import re
from pathlib import Path
from collections import defaultdict

VAULT_ROOT = Path(__file__).parent / "Tenelis"
OUTPUT = VAULT_ROOT / "00 - Vault Health.md"

STUB_THRESHOLD = 5  # lines of actual content (excluding frontmatter)
SKIP_DIRS = {"assets", ".obsidian", "99 - Templates"}


def get_content_lines(filepath):
    """Count non-frontmatter, non-empty content lines."""
    content = filepath.read_text(encoding='utf-8')
    # Strip frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    lines = [l for l in content.strip().split('\n') if l.strip()]
    return len(lines)


def extract_wikilinks(content):
    """Extract all wikilink targets from content."""
    return set(re.findall(r'\[\[([^\]|#]+?)(?:\|[^\]]+?)?\]\]', content))


def get_all_files():
    """Get all markdown files in the vault."""
    files = {}
    for f in VAULT_ROOT.rglob("*.md"):
        rel = f.relative_to(VAULT_ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        files[f.stem] = f
    return files


def check_stubs(all_files):
    """Find files with very little content."""
    stubs = []
    for name, path in sorted(all_files.items()):
        try:
            lines = get_content_lines(path)
            if lines <= STUB_THRESHOLD:
                rel = path.relative_to(VAULT_ROOT)
                stubs.append((str(rel), lines))
        except Exception:
            pass
    return stubs


def check_npc_portraits(all_files):
    """Find NPCs without portrait images."""
    npc_dir = VAULT_ROOT / "04 - NPCs"
    assets_dir = VAULT_ROOT / "assets" / "npcs"
    missing = []

    for f in npc_dir.glob("*.md"):
        if f.name == "NPC Relationship Map.md":
            continue
        content = f.read_text(encoding='utf-8')
        has_image = '![[' in content and 'assets/' in content
        if not has_image:
            missing.append(f.stem)

    return sorted(missing)


def check_quest_fields():
    """Find quests with missing frontmatter fields."""
    quest_dir = VAULT_ROOT / "03 - Quests"
    issues = []

    for f in quest_dir.glob("*.md"):
        content = f.read_text(encoding='utf-8')
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            continue

        fm = fm_match.group(1)
        missing_fields = []

        for field in ['quest_giver', 'location', 'session_started']:
            match = re.search(rf'^{field}:\s*(.*)$', fm, re.MULTILINE)
            if match:
                val = match.group(1).strip().strip('"').strip("'")
                if not val or val == '""':
                    missing_fields.append(field)
            else:
                missing_fields.append(field)

        # Check if title is still "Quest Name"
        if '# Quest Name' in content:
            missing_fields.append('title (still "Quest Name")')

        if missing_fields:
            issues.append((f.stem, missing_fields))

    return issues


def check_location_descriptions():
    """Find locations without descriptions."""
    loc_dir = VAULT_ROOT / "06 - World" / "Locations"
    empty = []

    for f in loc_dir.rglob("*.md"):
        content = f.read_text(encoding='utf-8')
        desc_match = re.search(r'## Description\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if not desc_match or len(desc_match.group(1).strip()) < 10:
            rel = f.relative_to(loc_dir)
            empty.append(str(rel))

    return sorted(empty)


def check_broken_links(all_files):
    """Find wikilinks that point to non-existent files."""
    broken = defaultdict(list)
    file_stems = set(all_files.keys())

    # Also add some known aliases
    alias_set = set()
    for name, path in all_files.items():
        try:
            content = path.read_text(encoding='utf-8')
            fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if fm_match:
                for alias_match in re.finditer(r'^\s+-\s+(.+)$', fm_match.group(1), re.MULTILINE):
                    alias_set.add(alias_match.group(1).strip().strip('"'))
        except Exception:
            pass

    known = file_stems | alias_set

    for name, path in all_files.items():
        try:
            content = path.read_text(encoding='utf-8')
            links = extract_wikilinks(content)
            for link in links:
                # Clean up path-style links
                link_name = link.split('/')[-1].strip()
                if link_name and link_name not in known:
                    broken[link_name].append(str(path.relative_to(VAULT_ROOT)))
        except Exception:
            pass

    return dict(sorted(broken.items()))


def check_orphans(all_files):
    """Find files with no inbound links."""
    inbound_counts = defaultdict(int)

    for name, path in all_files.items():
        try:
            content = path.read_text(encoding='utf-8')
            links = extract_wikilinks(content)
            for link in links:
                link_name = link.split('/')[-1].strip()
                inbound_counts[link_name] += 1
        except Exception:
            pass

    # Exclude Home, templates, index files
    skip_names = {"00 - Home", "00 - Player Setup Guide", "00 - Vault Health",
                  "Loot Log", "World Map", "NPC Relationship Map", "Timeline"}

    orphans = []
    for name, path in sorted(all_files.items()):
        if name in skip_names:
            continue
        rel = str(path.relative_to(VAULT_ROOT))
        # Only flag campaign content, not reference
        if rel.startswith("07 - Reference"):
            continue
        if rel.startswith("08 - DM"):
            continue
        if inbound_counts.get(name, 0) == 0:
            orphans.append(rel)

    return orphans


def run():
    all_files = get_all_files()
    print(f"Scanning {len(all_files)} files...\n")

    stubs = check_stubs(all_files)
    npc_portraits = check_npc_portraits(all_files)
    quest_issues = check_quest_fields()
    location_desc = check_location_descriptions()
    broken = check_broken_links(all_files)
    orphans = check_orphans(all_files)

    # Build output
    output = """---
aliases: [Vault Health]
tags: [dashboard]
---

# Vault Health Dashboard

Auto-generated report of vault issues. Run `python vault_health.py` to refresh.

"""

    # Summary
    total_issues = len(stubs) + len(npc_portraits) + len(quest_issues) + len(location_desc) + len(broken) + len(orphans)
    output += f"**Total issues found: {total_issues}**\n\n"
    output += "| Category | Count |\n|----------|-------|\n"
    output += f"| Stub files (< {STUB_THRESHOLD} content lines) | {len(stubs)} |\n"
    output += f"| NPCs without portraits | {len(npc_portraits)} |\n"
    output += f"| Quests with missing fields | {len(quest_issues)} |\n"
    output += f"| Locations without descriptions | {len(location_desc)} |\n"
    output += f"| Broken wikilinks | {len(broken)} |\n"
    output += f"| Orphaned files (no inbound links) | {len(orphans)} |\n"

    output += "\n---\n\n"

    # Stubs (only show campaign content, not reference)
    campaign_stubs = [(p, l) for p, l in stubs if not p.startswith("07 - Reference")]
    if campaign_stubs:
        output += f"## Stub Files ({len(campaign_stubs)} campaign files)\n\n"
        output += "| File | Content Lines |\n|------|---------------|\n"
        for path, lines in campaign_stubs[:30]:
            output += f"| `{path}` | {lines} |\n"
        if len(campaign_stubs) > 30:
            output += f"\n*...and {len(campaign_stubs) - 30} more*\n"
        output += "\n"

    # NPC portraits
    if npc_portraits:
        output += f"## NPCs Without Portraits ({len(npc_portraits)})\n\n"
        for npc in npc_portraits:
            output += f"- [[{npc}]]\n"
        output += "\n"

    # Quest issues
    if quest_issues:
        output += f"## Quest Field Issues ({len(quest_issues)})\n\n"
        output += "| Quest | Missing Fields |\n|-------|----------------|\n"
        for quest, fields in quest_issues:
            output += f"| [[{quest}]] | {', '.join(fields)} |\n"
        output += "\n"

    # Location descriptions
    if location_desc:
        output += f"## Locations Without Descriptions ({len(location_desc)})\n\n"
        for loc in location_desc:
            output += f"- `{loc}`\n"
        output += "\n"

    # Broken links
    if broken:
        output += f"## Broken Wikilinks ({len(broken)} unique targets)\n\n"
        output += "| Target | Referenced From |\n|--------|----------------|\n"
        for target, sources in list(broken.items())[:30]:
            src_list = ", ".join(f"`{s}`" for s in sources[:3])
            if len(sources) > 3:
                src_list += f" (+{len(sources) - 3} more)"
            output += f"| `{target}` | {src_list} |\n"
        if len(broken) > 30:
            output += f"\n*...and {len(broken) - 30} more broken links*\n"
        output += "\n"

    # Orphans
    if orphans:
        output += f"## Orphaned Files ({len(orphans)})\n\n"
        output += "Files with no inbound wikilinks (campaign content only):\n\n"
        for orph in orphans[:20]:
            output += f"- `{orph}`\n"
        if len(orphans) > 20:
            output += f"\n*...and {len(orphans) - 20} more*\n"

    OUTPUT.write_text(output, encoding='utf-8')
    print(f"Generated: {OUTPUT}")
    print(f"  {total_issues} total issues found")


if __name__ == "__main__":
    run()
