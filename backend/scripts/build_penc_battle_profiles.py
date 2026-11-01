"""Build Pendulum Color identity fingerprints from Humulos' public list."""

from __future__ import annotations

import html
import json
import re
import urllib.request
from pathlib import Path


SOURCE = "https://humulos.com/digimon/penc/list/"
OUTPUT = Path(__file__).parents[1] / "app" / "vpet" / "data" / "penc_battle_profiles.json"
ATTRIBUTE_WORDS = {"Free": 0, "Virus": 1, "Data": 2, "Vaccine": 3}
LEVELS = {
    "I": "In-Training I",
    "II": "In-Training II",
    "III": "Rookie",
    "IV": "Champion",
    "V": "Ultimate",
    "VI": "Mega",
    "VI+": "Mega",
}


def clean(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


request = urllib.request.Request(SOURCE, headers={"User-Agent": "Mozilla/5.0"})
document = urllib.request.urlopen(request, timeout=30).read().decode("utf-8")
profiles = []
for row in re.findall(r"<tr[^>]*>(.*?)</tr>", document, re.S):
    cells = [clean(value) for value in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
    if len(cells) < 9 or not re.fullmatch(r"(?:[0-9]+|C)-[0-9]+\+?", cells[0]):
        continue
    version_text, slot_text = cells[0].split("-", 1)
    version = int(version_text) if version_text.isdigit() else version_text
    slot = int(slot_text.rstrip("+"))
    power = int(cells[7]) if cells[7].isdigit() else None
    profiles.append({
        "id": cells[0],
        "name": cells[3],
        "level": LEVELS.get(cells[4], cells[4]),
        "attribute": cells[5],
        "album_id": int(cells[6]) if cells[6].isdigit() else None,
        "power": power,
        "attribute_word": ATTRIBUTE_WORDS.get(cells[5]),
        "version": version,
        "slot": slot,
        "version_name": cells[8],
    })

if len(profiles) != 331:
    raise RuntimeError(f"Expected 331 Pendulum Color profiles, found {len(profiles)}")

OUTPUT.write_text(json.dumps({
    "schemaVersion": 1,
    "source": SOURCE,
    "identity": "album_id + power + attribute_word; accepted only when the name is unique",
    "profiles": profiles,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {len(profiles)} profiles to {OUTPUT}")
