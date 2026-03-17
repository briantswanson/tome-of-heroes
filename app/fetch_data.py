#!/usr/bin/env python3
"""
fetch_data.py — Run this once to download D&D 5e 2024 data from 5etools GitHub
and build game_data.json for the character sheet app.

Usage:
    python -m app.fetch_data

Requires: pip install requests
"""

import json
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Please run: pip install requests")
    sys.exit(1)

BASE = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data"
OUT = Path(__file__).parent.parent / "data" / "game_data.json"

HEADERS = {"User-Agent": "dnd-charsheet-app/1.0"}

SRD_SOURCES = {
    # Core 2024
    "PHB2024", "XPHB",
    # Core 2014
    "PHB", "XGE", "TCE", "MPMM", "MM", "DMG", "SRD5", "basicRules",
    # Supplements with player options
    "MTF",     # Mordenkainen's Tome of Foes
    "VGM",     # Volo's Guide to Monsters
    "SCAG",    # Sword Coast Adventurer's Guide
    "EGW",     # Explorer's Guide to Wildemount
    "MOT",     # Mythic Odysseys of Theros
    "GGR",     # Guildmasters' Guide to Ravnica
    "ERLW",    # Eberron: Rising from the Last War
    "FTD",     # Fizban's Treasury of Dragons
    "VRGR",    # Van Richten's Guide to Ravenloft
    "SCC",     # Strixhaven: A Curriculum of Chaos
    "BAM",     # Boo's Astral Menagerie (Spelljammer races)
    "WBtW",    # The Wild Beyond the Witchlight
    "DSotDQ",  # Dragonlance: Shadow of the Dragon Queen
    "BMT",     # The Book of Many Things
    "PAitM",   # Planescape: Adventures in the Multiverse
    "AI",      # Acquisitions Incorporated
    "GoS",     # Ghosts of Saltmarsh
    "IDRotF",  # Icewind Dale: Rime of the Frostmaiden
}

# Higher value = preferred when deduplicating by name
SOURCE_PRIORITY = {
    "XPHB": 4, "PHB2024": 4,
    "TCE": 3, "XGE": 3,
    "MPMM": 2, "MTF": 2, "VGM": 2,
    "PHB": 1, "SCAG": 1, "EGW": 1, "MOT": 1, "GGR": 1,
    "ERLW": 1, "FTD": 1, "VRGR": 1, "SCC": 1, "BAM": 1,
    "WBtW": 1, "DSotDQ": 1, "BMT": 1, "PAitM": 1,
}


def dedupe_by_name(items):
    """Keep one entry per name, preferring higher-priority (newer) sources."""
    best = {}
    for item in items:
        name = item["name"]
        priority = SOURCE_PRIORITY.get(item.get("source", ""), 0)
        if name not in best or priority > SOURCE_PRIORITY.get(best[name].get("source", ""), 0):
            best[name] = item
    return sorted(best.values(), key=lambda x: x["name"])


def fetch(url):
    print(f"  Fetching {url.split('/')[-1]}...")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def clean_str(val):
    """Flatten a 5etools entry (string or {entries:[...]} object) to plain text."""
    if isinstance(val, str):
        return re.sub(r'\{@\w+ ([^}]+?)\}', r'\1', val)
    if isinstance(val, dict):
        parts = []
        for e in val.get("entries", []):
            parts.append(clean_str(e))
        return " ".join(parts)
    if isinstance(val, list):
        return " ".join(clean_str(v) for v in val)
    return str(val)

# ── RACES ──────────────────────────────────────────────────────────────────


def parse_races(raw):
    races = []
    for r in raw.get("race", []):
        if "UA" in r.get("source", ""):
            continue
        if r.get("_copy"):
            continue  # skip variant copies

        ability_bonuses = {}
        for ab in r.get("ability", []):
            for stat, val in ab.items():
                if stat == "choose":
                    continue
                ability_bonuses[stat.upper()] = val

        traits = []
        for entry in r.get("entries", []):
            if isinstance(entry, dict) and entry.get("type") == "entries":
                trait_name = entry.get("name", "")
                trait_text = clean_str(entry.get("entries", []))
                if trait_name:
                    traits.append({"name": trait_name, "desc": trait_text[:300]})

        speed = r.get("speed", 30)
        if isinstance(speed, dict):
            speed = speed.get("walk", 30)

        size = r.get("size", ["M"])
        if isinstance(size, list):
            size = size[0]
        size_map = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large"}
        size = size_map.get(size, size)

        races.append({
            "name": r["name"],
            "source": r.get("source", ""),
            "speed": speed,
            "size": size,
            "ability_bonuses": ability_bonuses,
            "traits": traits[:6],
            "darkvision": r.get("darkvision", 0),
            "languages": r.get("languageProficiencies", [{}])[0] if r.get("languageProficiencies") else {}
        })

    return dedupe_by_name(races)


# ── CLASSES ────────────────────────────────────────────────────────────────
SPELL_SLOT_TABLE = {
    # level -> [slots per spell level 1-9]
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
}
HALF_CASTER = {k: [v if i < 5 else 0 for i, v in enumerate(vals)] for k, vals in SPELL_SLOT_TABLE.items()}
THIRD_CASTER = {
    1: [0] * 9, 2: [0] * 9, 3: [2, 0, 0, 0, 0, 0, 0, 0, 0], 4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    5: [3, 0, 0, 0, 0, 0, 0, 0, 0], 6: [3, 0, 0, 0, 0, 0, 0, 0, 0], 7: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    8: [4, 2, 0, 0, 0, 0, 0, 0, 0], 9: [4, 2, 0, 0, 0, 0, 0, 0, 0], 10: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    11: [4, 3, 0, 0, 0, 0, 0, 0, 0], 12: [4, 3, 0, 0, 0, 0, 0, 0, 0], 13: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    14: [4, 3, 2, 0, 0, 0, 0, 0, 0], 15: [4, 3, 2, 0, 0, 0, 0, 0, 0], 16: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    17: [4, 3, 3, 0, 0, 0, 0, 0, 0], 18: [4, 3, 3, 0, 0, 0, 0, 0, 0], 19: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    20: [4, 3, 3, 1, 0, 0, 0, 0, 0],
}
WARLOCK_SLOTS = {
    1: [1, 0, 0, 0, 0, 0, 0, 0, 0], 2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [0, 2, 0, 0, 0, 0, 0, 0, 0], 4: [0, 2, 0, 0, 0, 0, 0, 0, 0],
    5: [0, 0, 2, 0, 0, 0, 0, 0, 0], 6: [0, 0, 2, 0, 0, 0, 0, 0, 0],
    7: [0, 0, 0, 2, 0, 0, 0, 0, 0], 8: [0, 0, 0, 2, 0, 0, 0, 0, 0],
    9: [0, 0, 0, 0, 2, 0, 0, 0, 0], 10: [0, 0, 0, 0, 2, 0, 0, 0, 0],
    11: [0, 0, 0, 0, 3, 0, 0, 0, 0], 12: [0, 0, 0, 0, 3, 0, 0, 0, 0],
    13: [0, 0, 0, 0, 3, 0, 0, 0, 0], 14: [0, 0, 0, 0, 3, 0, 0, 0, 0],
    15: [0, 0, 0, 0, 3, 0, 0, 0, 0], 16: [0, 0, 0, 0, 3, 0, 0, 0, 0],
    17: [0, 0, 0, 0, 4, 0, 0, 0, 0], 18: [0, 0, 0, 0, 4, 0, 0, 0, 0],
    19: [0, 0, 0, 0, 4, 0, 0, 0, 0], 20: [0, 0, 0, 0, 4, 0, 0, 0, 0],
}

CASTER_TYPE = {
    "Bard": "full", "Cleric": "full", "Druid": "full",
    "Sorcerer": "full", "Wizard": "full",
    "Paladin": "half", "Ranger": "half",
    "Artificer": "half",
    "Eldritch Knight": "third", "Arcane Trickster": "third",
    "Warlock": "warlock",
}


def parse_classes(raw):
    classes = []
    for cls in raw.get("class", []):
        if "UA" in cls.get("source", ""):
            continue

        name = cls["name"]
        hit_die = cls.get("hd", {}).get("faces", 8)

        # Proficiencies
        profs = {"armor": [], "weapons": [], "tools": [], "skills": []}
        for p in cls.get("startingProficiencies", {}).get("armor", []):
            profs["armor"].append(clean_str(p))
        for p in cls.get("startingProficiencies", {}).get("weapons", []):
            profs["weapons"].append(clean_str(p))

        skill_choices = cls.get("startingProficiencies", {}).get("skills", [])
        skill_list = []
        if skill_choices:
            sc = skill_choices[0]
            if isinstance(sc, dict):
                skill_list = sc.get("from", [])
                skill_list = [s.get("skill", s) if isinstance(s, dict) else s for s in skill_list]

        saving_throws = [s.upper() for s in cls.get("proficiency", [])]

        # Subclasses
        subclasses = [sub["name"] for sub in raw.get("subclass", [])
                      if sub.get("className") == name][:12]

        # Spellcasting
        caster = CASTER_TYPE.get(name, "none")
        spell_slots_by_level = {}
        if caster == "full":
            spell_slots_by_level = {str(lvl): slots for lvl, slots in SPELL_SLOT_TABLE.items()}
        elif caster == "half":
            spell_slots_by_level = {str(lvl): slots for lvl, slots in HALF_CASTER.items()}
        elif caster == "warlock":
            spell_slots_by_level = {str(lvl): slots for lvl, slots in WARLOCK_SLOTS.items()}

        # Primary ability
        primary = cls.get("primaryAbility", [{}])
        primary_str = ""
        if primary and isinstance(primary[0], dict):
            primary_str = " or ".join(primary[0].keys()).upper()

        classes.append({
            "name": name,
            "source": cls.get("source", ""),
            "hit_die": f"d{hit_die}",
            "hit_die_faces": hit_die,
            "primary_ability": primary_str,
            "saving_throws": saving_throws,
            "armor_proficiencies": profs["armor"],
            "weapon_proficiencies": profs["weapons"],
            "skill_choices": skill_list,
            "num_skill_choices": (
                skill_choices[0].get("count", 2)
                if skill_choices and isinstance(skill_choices[0], dict)
                else 2
            ),
            "caster_type": caster,
            "spell_slots_by_level": spell_slots_by_level,
            "subclasses": sorted(subclasses),
        })

    return dedupe_by_name(classes)

# ── BACKGROUNDS ─────────────────────────────────────────────────────────────


def parse_backgrounds(raw):
    bgs = []
    for bg in raw.get("background", []):
        if "UA" in bg.get("source", ""):
            continue

        skills = []
        for sp in bg.get("skillProficiencies", [{}])[0].items() if bg.get("skillProficiencies") else []:
            if sp[1] is True:
                skills.append(sp[0])

        tools = []
        for tp in bg.get("toolProficiencies", [{}]):
            if isinstance(tp, dict):
                tools += [k for k, v in tp.items() if v is True]

        equipment = []
        for eq in bg.get("startingEquipment", []):
            if isinstance(eq, dict):
                for item in eq.get("_", []):
                    if isinstance(item, dict):
                        equipment.append(item.get("item", item.get("special", "")))
                    elif isinstance(item, str):
                        equipment.append(item)

        feat = ""
        for entry in bg.get("entries", []):
            if isinstance(entry, dict) and entry.get("name") in ("Feature", "Background Feature"):
                feat = entry.get("name", "")

        bgs.append({
            "name": bg["name"],
            "source": bg.get("source", ""),
            "skill_proficiencies": skills[:4],
            "tool_proficiencies": tools[:3],
            "equipment": [e for e in equipment if e][:8],
            "feature": feat,
        })

    return dedupe_by_name(bgs)

# ── SPELLS ──────────────────────────────────────────────────────────────────


def parse_spells(raw_list):
    spells = []
    for sp in raw_list:
        if "UA" in sp.get("source", ""):
            continue

        # Classes that can use this spell
        classes = []
        for sc in sp.get("classes", {}).get("fromClassList", []):
            classes.append(sc["name"])

        level = sp.get("level", 0)
        school_map = {"A": "Abjuration", "C": "Conjuration", "D": "Divination",
                      "E": "Enchantment", "V": "Evocation", "I": "Illusion",
                      "N": "Necromancy", "T": "Transmutation"}
        school = school_map.get(sp.get("school", ""), sp.get("school", ""))

        time_entry = sp.get("time", [{}])[0]
        casting_time = f"{time_entry.get('number', 1)} {time_entry.get('unit', 'action')}"

        range_entry = sp.get("range", {})
        rtype = range_entry.get("type", "")
        rdist = range_entry.get("distance", {})
        if rtype == "point":
            r_amount = rdist.get("amount", "")
            r_unit = rdist.get("type", "")
            spell_range = f"{r_amount} {r_unit}".strip() if r_amount else r_unit
        else:
            spell_range = rtype

        components = sp.get("components", {})
        comp_str = "".join(k.upper() for k in ["v", "s", "m"] if components.get(k))

        duration = sp.get("duration", [{}])[0]
        dur_type = duration.get("type", "")
        dur_str = dur_type
        if dur_type == "timed":
            d = duration.get("duration", {})
            dur_str = f"{d.get('amount', '')} {d.get('type', '')}".strip()

        desc_parts = []
        for entry in sp.get("entries", []):
            desc_parts.append(clean_str(entry))
            if len(" ".join(desc_parts)) > 400:
                break
        desc = " ".join(desc_parts)[:400]

        ritual = sp.get("meta", {}).get("ritual", False)
        concentration = any(d.get("concentration") for d in sp.get("duration", []))

        spells.append({
            "name": sp["name"],
            "level": level,
            "school": school,
            "casting_time": casting_time,
            "range": spell_range,
            "components": comp_str,
            "duration": dur_str,
            "ritual": ritual,
            "concentration": concentration,
            "classes": list(set(classes)),
            "desc": desc,
            "source": sp.get("source", ""),
        })

    return sorted(spells, key=lambda x: (x["level"], x["name"]))


def main():
    print("\n⚔️  D&D 5e Data Fetcher")
    print("=" * 40)

    data = {"races": [], "classes": [], "backgrounds": [], "spells": []}

    # Races
    print("\n📖 Fetching races...")
    try:
        raw = fetch(f"{BASE}/races.json")
        data["races"] = parse_races(raw)
        print(f"   ✓ {len(data['races'])} races loaded")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    # Classes + Subclasses
    print("\n⚔️  Fetching classes...")
    try:
        raw = fetch(f"{BASE}/class/index.json")
        all_class_data = {"class": [], "subclass": []}
        for cls_file in raw.values():
            try:
                cd = fetch(f"{BASE}/class/{cls_file}")
                all_class_data["class"].extend(cd.get("class", []))
                all_class_data["subclass"].extend(cd.get("subclass", []))
                time.sleep(0.1)
            except Exception as ce:
                print(f"   ! Skipped {cls_file}: {ce}")
        data["classes"] = parse_classes(all_class_data)
        print(f"   ✓ {len(data['classes'])} classes loaded")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    # Backgrounds
    print("\n🎭 Fetching backgrounds...")
    try:
        raw = fetch(f"{BASE}/backgrounds.json")
        data["backgrounds"] = parse_backgrounds(raw)
        print(f"   ✓ {len(data['backgrounds'])} backgrounds loaded")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    # Spells (multiple files)
    print("\n✨ Fetching spells...")
    try:
        index = fetch(f"{BASE}/spells/index.json")
        all_spells = []
        for src, fname in index.items():
            try:
                sd = fetch(f"{BASE}/spells/{fname}")
                all_spells.extend(sd.get("spell", []))
                time.sleep(0.1)
            except BaseException:
                pass
        data["spells"] = parse_spells(all_spells)
        print(f"   ✓ {len(data['spells'])} spells loaded")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    # Write output — server expects edition-keyed structure
    output = {"2024": data, "2014": data}
    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)

    total = sum(len(v) for v in data.values())
    print(f"\n✅ Done! Wrote {total} entries to game_data.json")
    print(
        f"   Races: {len(data['races'])} | Classes: {len(data['classes'])}"
        f" | Backgrounds: {len(data['backgrounds'])} | Spells: {len(data['spells'])}")
    print("\n🎲 Restart your server and the character creator will use this data.\n")


if __name__ == "__main__":
    main()
