"""
Generate an NPC relationship map as a Mermaid diagram embedded in an Obsidian note.

Reads NPC frontmatter and relationship tables, faction membership, and family
connections to produce a visual graph in Tenelis/04 - NPCs/NPC Relationship Map.md.
"""

import os
import re
from pathlib import Path

VAULT_ROOT = Path(__file__).parent / "Tenelis"
NPC_DIR = VAULT_ROOT / "04 - NPCs"
FACTIONS_DIR = VAULT_ROOT / "06 - World" / "Factions"
OUTPUT_FILE = NPC_DIR / "NPC Relationship Map.md"


def parse_frontmatter(content):
    """Extract YAML frontmatter fields."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line and not line.strip().startswith('-'):
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def parse_relationships_table(content):
    """Extract relationships from the ## Relationships table."""
    rels = []
    match = re.search(r'## Relationships\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n##|\n\Z)', content, re.DOTALL)
    if not match:
        return rels
    for line in match.group(1).strip().split('\n'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) >= 2 and cols[0].strip():
            entity = re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', r'\1', cols[0])
            rel_type = re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', r'\1', cols[1])
            if entity.strip():
                rels.append((entity.strip(), rel_type.strip()))
    return rels


def load_npcs():
    """Load all NPC data from vault files."""
    npcs = {}
    for f in NPC_DIR.glob("*.md"):
        if f.name == "NPC Relationship Map.md":
            continue
        content = f.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)
        name = f.stem
        rels = parse_relationships_table(content)

        # Extract family connections from content
        family = []
        text_lower = content.lower()
        # Check for explicit family mentions
        family_patterns = [
            (r'(?:father|dad):\s*\[\[([^\]|]+)', 'father'),
            (r'(?:mother|mom):\s*\[\[([^\]|]+)', 'mother'),
            (r'(?:sister):\s*\[\[([^\]|]+)', 'sister'),
            (r'(?:brother):\s*\[\[([^\]|]+)', 'brother'),
            (r'(?:daughter):\s*\[\[([^\]|]+)', 'daughter'),
            (r'(?:son):\s*\[\[([^\]|]+)', 'son'),
            (r'(?:twin sister):\s*\[\[([^\]|]+)', 'twin'),
            (r'(?:twin brother):\s*\[\[([^\]|]+)', 'twin'),
        ]
        for pattern, rel_type in family_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                family.append((match.group(1).strip(), rel_type))

        npcs[name] = {
            'race': fm.get('race', ''),
            'faction': fm.get('faction', ''),
            'status': fm.get('status', 'unknown'),
            'attitude': fm.get('attitude', 'neutral'),
            'relationships': rels,
            'family': family,
        }

    return npcs


def load_factions():
    """Load faction membership from faction files."""
    factions = {}
    for f in FACTIONS_DIR.rglob("*.md"):
        content = f.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)
        name = f.stem
        # Extract members from content
        members = re.findall(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', content)
        factions[name] = {
            'members': list(set(members)),
            'type': fm.get('faction_type', 'Unknown'),
        }
    return factions


def sanitize_id(name):
    """Create a valid Mermaid node ID."""
    return re.sub(r'[^a-zA-Z0-9]', '_', name)


def generate_mermaid(npcs, factions):
    """Generate a Mermaid flowchart diagram."""
    lines = ["```mermaid", "graph TD"]

    # Define node styles
    lines.append("")
    lines.append("    %% Style definitions")
    lines.append("    classDef alive fill:#2d5016,stroke:#4a8c2a,color:#fff")
    lines.append("    classDef dead fill:#5c1a1a,stroke:#8b3a3a,color:#fff")
    lines.append("    classDef missing fill:#4a3d00,stroke:#8b7500,color:#fff")
    lines.append("    classDef unknown fill:#333,stroke:#666,color:#fff")
    lines.append("    classDef party fill:#1a3a5c,stroke:#2a6a9c,color:#fff")
    lines.append("    classDef faction fill:#3d1a5c,stroke:#6a2a9c,color:#fff")
    lines.append("")

    # Add party members
    lines.append("    %% Party Members")
    party_members = [
        "Netanyahu D. Kirkuenly",
        "Booker Locke",
        "Old Shell",
        "Cassius Bellona",
        "Ryan-Nigamus",
    ]
    for pc in party_members:
        nid = sanitize_id(pc)
        short = pc.split()[0] if pc != "Old Shell" else "Old Shell"
        if pc == "Netanyahu D. Kirkuenly":
            short = "Net"
        lines.append(f'    {nid}["{short}"]')

    lines.append("")
    lines.append("    %% NPCs")

    # Add NPC nodes
    status_map = {}
    for name, data in sorted(npcs.items()):
        nid = sanitize_id(name)
        status = data['status']
        status_map[nid] = status

        label = name
        if status == 'deceased':
            label = f"{name} (dead)"
        elif status == 'missing':
            label = f"{name} (missing)"

        lines.append(f'    {nid}["{label}"]')

    lines.append("")
    lines.append("    %% Faction subgraphs")

    # Group by faction
    faction_members = {}
    for name, data in npcs.items():
        faction = data.get('faction', '')
        if faction and faction not in ('', 'Unknown'):
            faction_members.setdefault(faction, []).append(name)

    for faction, members in sorted(faction_members.items()):
        fid = sanitize_id(faction)
        lines.append(f'    subgraph {fid}["{faction}"]')
        for m in members:
            lines.append(f'        {sanitize_id(m)}')
        lines.append("    end")
        lines.append("")

    # Add relationships
    lines.append("    %% Relationships")
    seen_edges = set()

    for name, data in npcs.items():
        nid = sanitize_id(name)
        for rel_entity, rel_type in data['relationships']:
            rel_id = sanitize_id(rel_entity)
            edge_key = tuple(sorted([nid, rel_id])) + (rel_type,)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                lines.append(f'    {nid} -- "{rel_type}" --> {rel_id}')

        for family_entity, family_type in data['family']:
            fam_id = sanitize_id(family_entity)
            edge_key = tuple(sorted([nid, fam_id])) + (family_type,)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                lines.append(f'    {nid} -. "{family_type}" .-> {fam_id}')

    # Add known connections from session data
    lines.append("")
    lines.append("    %% Key party connections")
    party_connections = [
        ("Netanyahu_D__Kirkuenly", "Payton_Hightower", "Sending Stone contact"),
        ("Netanyahu_D__Kirkuenly", "Aya", "Poison knowledge deal"),
        ("Booker_Locke", "Gwen_Locke", "Twin - searching for"),
        ("Cassius_Bellona", "Grig", "Friend"),
    ]
    for src, tgt, label in party_connections:
        edge_key = tuple(sorted([src, tgt])) + (label,)
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            lines.append(f'    {src} -. "{label}" .-> {tgt}')

    lines.append("")
    lines.append("    %% Apply styles")

    # Apply styles
    for nid, status in status_map.items():
        if status == 'deceased':
            lines.append(f"    class {nid} dead")
        elif status == 'missing':
            lines.append(f"    class {nid} missing")
        elif status in ('unknown', ''):
            lines.append(f"    class {nid} unknown")
        else:
            lines.append(f"    class {nid} alive")

    for pc in party_members:
        lines.append(f"    class {sanitize_id(pc)} party")

    lines.append("```")
    return "\n".join(lines)


def run():
    npcs = load_npcs()
    factions = load_factions()

    mermaid = generate_mermaid(npcs, factions)

    output = f"""---
aliases: []
tags: [reference]
---

# NPC Relationship Map

A visual map of all known NPCs, their factions, family ties, and connections to the party.

**Legend:**
- Blue nodes = Party members
- Green nodes = Alive NPCs
- Red nodes = Deceased NPCs
- Yellow nodes = Missing NPCs
- Gray nodes = Unknown status
- Solid arrows = Direct relationships
- Dashed arrows = Family connections / party ties
- Purple subgraphs = Faction groupings

{mermaid}

## Faction Summary

| Faction | Members | Status |
|---------|---------|--------|
"""

    # Build faction summary table
    faction_data = {}
    for name, data in npcs.items():
        faction = data.get('faction', '')
        if faction and faction not in ('', 'Unknown'):
            faction_data.setdefault(faction, []).append(
                f"[[{name}]] ({data['status']})"
            )

    for faction, members in sorted(faction_data.items()):
        output += f"| {faction} | {', '.join(members)} | Active |\n"

    output += f"""
## Family Trees

### Kenku Bloodline
- [[Dima]] (deceased) - father of [[Corso]] and [[Eileen Whitebeak]]
- [[Corso]] and [[Eileen Whitebeak]] are siblings (strained relationship)

### The Three Sisters
- [[Nahara]], [[Ayla]], [[Sophie]] - possibly not related by blood
- Traveled with a Knight of Drayik ~150 years ago

### Locke Family
- [[Booker Locke]] and [[Gwen Locke]] are twins
- Parents murdered by the Senin, Gwen kidnapped 6 years ago

### Aya's Family
- [[Ewing]] (missing) is [[Aya]]'s father
"""

    OUTPUT_FILE.write_text(output, encoding='utf-8')
    print(f"Generated NPC Relationship Map: {OUTPUT_FILE}")
    print(f"  {len(npcs)} NPCs, {len(faction_data)} factions mapped")


if __name__ == "__main__":
    run()
