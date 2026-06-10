"""Generate Session 11 scene illustrations via the Gemini image API."""

import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

OUT_DIR = Path(__file__).parent / "Tenelis" / "assets" / "scenes"
API_KEY = os.environ["GOOGLE_API_KEY"]

MODELS = [
    "gemini-2.5-flash-image",
    "gemini-2.0-flash-preview-image-generation",
]

STYLE = (
    "D&D 5e fantasy illustration, dramatic lighting, painterly style, "
    "medieval fantasy setting, detailed environment, no text or UI elements. "
    "All characters in natural, context-appropriate poses standing and moving "
    "like real humans. Depict ONLY the characters described - no extra figures, "
    "no silhouettes or duplicate characters in the background."
)

SCENES = [
    {
        "filename": "session-11-the-party-approaches-masha-s-house.png",
        "prompt": (
            "Exactly six travelers approach a tiny, weathered cottage standing alone "
            "on a misty moor north of an abandoned village, late afternoon gloom. "
            "In front: a Tortle Ranger - a humanoid turtle-man WALKING UPRIGHT ON TWO "
            "LEGS like a human soldier, large shell on his back, weathered green "
            "skin, holding a bow at his side - and a lean Human Rogue in dark "
            "clothing walking carefully along a fence line, scouting. Behind them "
            "walk four companions: a Yuan-ti Bard with subtle scales carrying a "
            "lute, a Human Fighter in plate armor with a longsword, a muscular Human "
            "Barbarian with a greataxe, and a broad warrior in heavy plate armor "
            "with a massive claymore on his back. Every character stands fully "
            "upright on two legs with natural human posture and gait. The cottage "
            "is small and crooked with smoke drifting from a leaning chimney. "
            + STYLE
        ),
    },
    {
        "filename": "session-11-masha-tells-the-history-of-the-demon-war.png",
        "prompt": (
            "Interior of a cramped, cluttered one-room cottage, rancid and dim, lit by "
            "a single candle and weak fire. A scraggly old woman with wild gray hair "
            "and layered ragged shawls sits in a worn chair with EMPTY HANDS, one "
            "bony finger raised mid-story, holding nothing. Listening closely around "
            "her stand exactly five adventurers, all upright on two legs with "
            "natural human posture: a Yuan-ti Bard with subtle scales who carries "
            "the only lute in the scene slung on his back, a lean Human Rogue in "
            "dark clothing, a Tortle Ranger (humanoid turtle-man standing upright "
            "like a human) with a large shell, a Human Fighter in plate armor, and "
            "a muscular Human Barbarian. The old woman has no instrument - the lute "
            "belongs to the Bard only. Shelves of jars, herbs and old talismans "
            "crowd the walls. Tense, eerie storytelling atmosphere. " + STYLE
        ),
    },
    {
        "filename": "session-11-scarecrow-ambush-outside-masha-s-house.png",
        "prompt": (
            "Night battle outside a tiny moorland cottage. Exactly six heroes fight "
            "a pack of animated scarecrows with burlap sack heads, glowing ember "
            "eyes, ragged straw bodies and crooked wooden limbs lurching out of the "
            "dark treeline. A Tortle Ranger fires his bow, a Human Rogue lunges with "
            "twin daggers, a Yuan-ti Bard gestures mid-spell, a Human Fighter in "
            "plate swings a longsword, a muscular Human Barbarian roars mid-swing "
            "with a greataxe, and a broad warrior in heavy plate cleaves with a huge "
            "claymore. Moonlight through fog, embers and straw flying. " + STYLE
        ),
    },
    {
        "filename": "session-11-the-demon-war-of-two-centuries-past.png",
        "prompt": (
            "Epic historical battle scene from two hundred years ago: armored knights "
            "with banners make a desperate stand against a horde of demons pouring "
            "through a massive torn rift in the sky that bleeds otherworldly light. "
            "The knights' formation holds a ruined battlefield, many fallen comrades "
            "around them. A towering archdemon silhouette looms within the rift. "
            "Apocalyptic clouds, fire on the horizon, mythic-history mural feel. "
            + STYLE
        ),
    },
]


def generate(prompt: str, model: str) -> bytes | None:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={API_KEY}"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    return None


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = 0
    for scene in SCENES:
        out_path = OUT_DIR / scene["filename"]
        print(f"Generating: {scene['filename']}")
        img = None
        last_err = None
        for model in MODELS:
            try:
                img = generate(scene["prompt"], model)
                if img:
                    break
            except Exception as e:  # noqa: BLE001
                last_err = e
                print(f"  {model} failed: {e}")
        if img:
            out_path.write_bytes(img)
            print(f"  Saved ({len(img) // 1024} KB)")
        else:
            failures += 1
            print(f"  FAILED: {last_err}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
