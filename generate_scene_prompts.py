"""
Generate image prompts for session recap illustrations.

Reads a session recap, identifies 3-4 key scenes, and generates
descriptive prompts suitable for AI image generation. Outputs to
a prompts file that can be fed to an image generation tool.
"""

import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).parent / "Tenelis"
SESSIONS_DIR = VAULT_ROOT / "02 - Sessions"
OUTPUT_DIR = VAULT_ROOT / "assets" / "scenes"

# Party member visual descriptions for consistent image generation
PARTY_VISUALS = {
    "Netanyahu D. Kirkuenly": "Yuan-ti Bard, serpentine features with subtle scales, charming and cunning expression, carrying a lute and staff",
    "Net": "Yuan-ti Bard, serpentine features with subtle scales, charming and cunning expression, carrying a lute and staff",
    "Booker Locke": "Human Rogue, lean and wiry build, dark clothing, twin daggers, alert and cautious eyes",
    "Booker": "Human Rogue, lean and wiry build, dark clothing, twin daggers, alert and cautious eyes",
    "Old Shell": "Tortle Ranger, large shell on back, weathered green skin, carrying a bow and quiver, calm and observant",
    "Cassius Bellona": "Human Fighter (Eldritch Knight), armored in plate, longsword at hip, military bearing, determined expression",
    "Cassius": "Human Fighter (Eldritch Knight), armored in plate, longsword at hip, military bearing, determined expression",
    "Ryan-Nigamus": "Human Barbarian, muscular build, wild appearance, carrying a greataxe, fierce expression",
}


def parse_session_number(filepath):
    match = re.search(r'Session\s+(\d+)', filepath.name)
    return int(match.group(1)) if match else 0


def strip_wikilinks(text):
    """Remove wikilink formatting, keeping display text."""
    return re.sub(r'\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]', lambda m: m.group(2) or m.group(1), text)


def extract_key_scenes(content, session_num):
    """Identify the most visually interesting scenes from a session recap."""
    scenes = []

    # Get highlights
    highlights_match = re.search(r'## Highlights\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if highlights_match:
        for line in highlights_match.group(1).strip().split('\n'):
            # Protect escaped pipes inside wikilinks before splitting
            safe_line = re.sub(r'\\\|', '\x00', line)
            cols = [c.strip().replace('\x00', '|') for c in safe_line.split('|')[1:-1]]
            if len(cols) >= 2:
                player = strip_wikilinks(cols[0]).strip()
                moment = strip_wikilinks(cols[1]).strip()
                if moment:
                    scenes.append({
                        'player': player,
                        'moment': moment,
                        'type': 'highlight',
                    })

    # Get combat encounters
    combat_match = re.search(r'## Combat Encounters\n\n\|.*?\|\n\|[-\s|]+\|\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if combat_match:
        for line in combat_match.group(1).strip().split('\n'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 3:
                enemy = strip_wikilinks(cols[0]).strip()
                notable = strip_wikilinks(cols[2]).strip() if len(cols) > 2 else ""
                if enemy and enemy != "None":
                    scenes.append({
                        'enemy': enemy,
                        'notable': notable,
                        'type': 'combat',
                    })

    # Get key story beats from Key Events
    events_match = re.search(r'### Story\n(.*?)(?=\n###|\n## )', content, re.DOTALL)
    if events_match:
        for line in events_match.group(1).strip().split('\n'):
            match = re.match(r'^\d+\.\s+(.+)$', line.strip())
            if match:
                event = strip_wikilinks(match.group(1))
                scenes.append({
                    'event': event,
                    'type': 'story',
                })

    return scenes


def find_party_in_scene(scene_text):
    """Identify which party members are in a scene."""
    present = []
    for name, desc in PARTY_VISUALS.items():
        if name.lower() in scene_text.lower():
            present.append((name, desc))
    # Deduplicate (Net/Netanyahu, Booker/Booker Locke, etc.)
    seen_descs = set()
    unique = []
    for name, desc in present:
        if desc not in seen_descs:
            seen_descs.add(desc)
            unique.append((name, desc))
    return unique


def generate_prompts(scenes, session_num):
    """Generate image prompts from scenes, picking the best 3-4."""
    prompts = []

    # Prioritize: combat > highlights > story
    combat_scenes = [s for s in scenes if s['type'] == 'combat']
    highlight_scenes = [s for s in scenes if s['type'] == 'highlight']
    story_scenes = [s for s in scenes if s['type'] == 'story']

    selected = []
    # Take combat scenes first
    for scene in combat_scenes[:1]:
        selected.append(scene)
    # Then best highlights (skip combat-related ones to avoid duplication)
    for scene in highlight_scenes[:3]:
        selected.append(scene)
    # Fill with story if needed
    remaining = 4 - len(selected)
    for scene in story_scenes[:remaining]:
        selected.append(scene)

    for i, scene in enumerate(selected[:4]):
        if scene['type'] == 'combat':
            desc = scene.get('notable', scene.get('enemy', ''))
            scene_text = f"Combat scene: {scene['enemy']}. {desc}"
        elif scene['type'] == 'highlight':
            scene_text = f"{scene['player']}: {scene['moment']}"
        else:
            scene_text = scene.get('event', '')

        # Find party members
        party = find_party_in_scene(scene_text)

        prompt = f"D&D 5e fantasy illustration, dramatic lighting, painterly style. "
        prompt += f"Scene from Session {session_num}: {scene_text}. "

        if party:
            prompt += "Characters present: "
            prompt += "; ".join([f"{name} ({desc})" for name, desc in party[:3]])
            prompt += ". "

        prompt += "Medieval fantasy setting, detailed environment, no text or UI elements."

        # Generate filename
        slug = re.sub(r'[^a-z0-9]+', '-', scene_text[:50].lower()).strip('-')
        filename = f"session-{session_num}-{slug}"

        prompts.append({
            'prompt': prompt,
            'filename': filename,
            'scene_summary': scene_text,
        })

    return prompts


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Determine which session to process
    if len(sys.argv) > 1:
        target = int(sys.argv[1])
        session_files = [f for f in SESSIONS_DIR.glob("Session * Recap.md")
                        if parse_session_number(f) == target]
    else:
        session_files = sorted(SESSIONS_DIR.glob("Session * Recap.md"), key=parse_session_number)
        session_files = session_files[-1:]  # Latest only

    if not session_files:
        print("No session recap found.")
        return

    for session_file in session_files:
        content = session_file.read_text(encoding='utf-8')
        session_num = parse_session_number(session_file)

        scenes = extract_key_scenes(content, session_num)
        prompts = generate_prompts(scenes, session_num)

        if not prompts:
            print(f"Session {session_num}: No scenes identified.")
            continue

        # Write prompts file
        output_file = OUTPUT_DIR / f"session-{session_num}-prompts.md"
        output = f"# Session {session_num} - Image Prompts\n\n"
        output += f"Generated {len(prompts)} scene prompts from session recap.\n\n"

        for i, p in enumerate(prompts, 1):
            output += f"## Scene {i}: {p['scene_summary'][:80]}\n\n"
            output += f"**Filename:** `{p['filename']}.png`\n\n"
            output += f"**Prompt:**\n\n> {p['prompt']}\n\n"
            output += "---\n\n"

        output_file.write_text(output, encoding='utf-8')
        print(f"Session {session_num}: Generated {len(prompts)} image prompts")
        print(f"  Output: {output_file}")
        for p in prompts:
            print(f"    - {p['filename']}")


if __name__ == "__main__":
    run()
