"""
Convert Tome of Heroes character JSON files into Obsidian-compatible markdown notes.

Usage:
    python -m app.json_to_obsidian --vault /path/to/obsidian/vault
    python -m app.json_to_obsidian --vault /path/to/vault --character "Thorin"

Each character becomes a .md file with:
  - YAML frontmatter (queryable by the Obsidian Dataview plugin)
  - Human-readable sections mirroring the app's tabs
"""

import argparse
import glob
import json
import math
import os

APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'character_sheets')

ABILITIES = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
ABILITY_NAMES = {
    'STR': 'Strength', 'DEX': 'Dexterity', 'CON': 'Constitution',
    'INT': 'Intelligence', 'WIS': 'Wisdom', 'CHA': 'Charisma',
}
ORDINALS = ['Cantrip', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']


def mod(score):
    m = (score - 10) // 2
    return f"+{m}" if m >= 0 else str(m)


def prof_bonus(level):
    return math.ceil(level / 4) + 1


def skill_value(skill_data, stats, pb):
    score = stats.get(skill_data.get('stat', 'STR'), 10)
    base = (score - 10) // 2
    if skill_data.get('expert'):
        return base + pb * 2
    if skill_data.get('prof'):
        return base + pb
    return base


def fmt_mod(value):
    return f"+{value}" if value >= 0 else str(value)


class CharacterNote:
    def __init__(self, char):
        self.char = char
        self.pb = prof_bonus(char.get('level', 1))

    def frontmatter(self):
        c = self.char
        hp = c.get('hp', {})
        lines = [
            '---',
            f"name: {c.get('name', 'Unknown')}",
            f"class: {c.get('class', '')}",
            f"subclass: {c.get('subclass', '')}",
            f"level: {c.get('level', 1)}",
            f"race: {c.get('race', '')}",
            f"background: {c.get('background', '')}",
            f"alignment: {c.get('alignment', '')}",
            f'edition: "{c.get("edition", "2024")}"',
            f"hp_current: {hp.get('current', 0)}",
            f"hp_max: {hp.get('max', 0)}",
            f"ac: {c.get('ac', 10)}",
            f"speed: {c.get('speed', 30)}",
            f"proficiency_bonus: {self.pb}",
            f"inspiration: {str(c.get('inspiration', False)).lower()}",
            f"tags: [character, {c.get('class', 'adventurer').lower().replace(' ', '-')}]",
            '---',
        ]
        return '\n'.join(lines)

    def header(self):
        c = self.char
        name = c.get('name', 'Unknown Adventurer')
        level = c.get('level', 1)
        cls = c.get('class', '')
        subclass = c.get('subclass', '')
        race = c.get('race', '')
        background = c.get('background', '')

        class_str = f"Level {level} {subclass} {cls}".strip() if subclass else f"Level {level} {cls}"
        meta_parts = [p for p in [class_str, race, background] if p]

        lines = [
            f"# {name}",
            f"*{' · '.join(meta_parts)}*" if meta_parts else '',
            '',
        ]
        return '\n'.join(lines)

    def combat_section(self):
        c = self.char
        hp = c.get('hp', {})
        hd = c.get('hit_dice', {})
        ds = c.get('death_saves', {})
        init = c.get('initiative_bonus', 0)

        hp_str = f"{hp.get('current', 0)}/{hp.get('max', 0)}"
        if hp.get('temp', 0):
            hp_str += f" (+{hp['temp']} temp)"

        saves_str = (
            f"✓ {ds.get('successes', 0)}/3  ✗ {ds.get('failures', 0)}/3"
            if (ds.get('successes', 0) or ds.get('failures', 0))
            else "—"
        )

        lines = [
            '## Combat',
            '',
            "| HP | AC | Speed | Initiative | Prof Bonus |",
            "|----|----|-------|------------|------------|",
            f"| {hp_str} | {c.get('ac', 10)} "
            f"| {c.get('speed', 30)} ft | {fmt_mod(init)} | {fmt_mod(self.pb)} |",
            '',
            f"**Hit Dice:** {hd.get('total', 1)}{hd.get('die', 'd8')} "
            f"(used: {hd.get('used', 0)})",
            f"**Death Saves:** {saves_str}",
            f"**Inspiration:** {'Yes' if c.get('inspiration') else 'No'}",
            '',
        ]
        return '\n'.join(lines)

    def stats_section(self):
        c = self.char
        stats = c.get('stats', {})
        saves = c.get('saving_throws', {})
        skills = c.get('skills', {})

        # Ability scores table
        score_row = ' | '.join(str(stats.get(ab, 10)) for ab in ABILITIES)
        mod_row = ' | '.join(mod(stats.get(ab, 10)) for ab in ABILITIES)
        header_row = ' | '.join(ABILITIES)
        sep_row = ' | '.join(['---'] * 6)

        lines = [
            '## Ability Scores',
            '',
            f"| {header_row} |",
            f"| {sep_row} |",
            f"| {score_row} |",
            f"| {mod_row} |",
            '',
            '## Saving Throws',
            '',
        ]

        for ab in ABILITIES:
            score = stats.get(ab, 10)
            base = (score - 10) // 2
            proficient = saves.get(ab, False)
            total = base + (self.pb if proficient else 0)
            pip = '●' if proficient else '○'
            lines.append(f"- {pip} {fmt_mod(total)} {ABILITY_NAMES[ab]}")

        lines += ['', '## Skills', '']

        for skill_name in sorted(skills.keys()):
            sk = skills[skill_name]
            total = skill_value(sk, stats, self.pb)
            if sk.get('expert'):
                pip = '◆'
            elif sk.get('prof'):
                pip = '●'
            else:
                pip = '○'
            lines.append(f"- {pip} {fmt_mod(total)} {skill_name} *({sk.get('stat', '?')})*")

        passive = 10 + skill_value(skills.get('Perception', {}), stats, self.pb)
        lines += ['', f"**Passive Perception:** {passive}", '']

        proficiencies = c.get('proficiencies', '').strip()
        if proficiencies:
            lines += ['**Proficiencies & Languages:**', proficiencies, '']

        return '\n'.join(lines)

    def spells_section(self):
        c = self.char
        slots = c.get('spell_slots', {})
        spells = c.get('spells', [])

        active_slots = {k: v for k, v in slots.items() if v.get('total', 0) > 0}

        lines = ['## Spells', '']

        if c.get('spellcasting_class') or c.get('spell_save_dc') or c.get('spell_attack_bonus'):
            lines.append(
                f"**Spellcasting:** {c.get('spellcasting_class', '')}  "
                f"Save DC {c.get('spell_save_dc', '—')}  "
                f"Attack {fmt_mod(c.get('spell_attack_bonus', 0))}"
            )
            lines.append('')

        if active_slots:
            lines.append('### Spell Slots')
            lines.append('')
            for level_str, sl in sorted(active_slots.items(), key=lambda x: int(x[0])):
                level = int(level_str)
                total = sl.get('total', 0)
                used = sl.get('used', 0)
                remaining = total - used
                pips = '●' * remaining + '○' * used
                lines.append(f"- **{ORDINALS[level]}:** {pips} ({remaining}/{total})")
            lines.append('')

        if spells:
            lines.append('### Spellbook')
            lines.append('')
            by_level = {}
            for sp in spells:
                lvl = sp.get('level', 0)
                by_level.setdefault(lvl, []).append(sp)

            for lvl in sorted(by_level.keys()):
                lines.append(f"**{ORDINALS[lvl]}**")
                for sp in sorted(by_level[lvl], key=lambda s: s.get('name', '')):
                    prepared = '✓' if sp.get('prepared') else '·'
                    meta = [m for m in [sp.get('school'), sp.get('casting_time'), sp.get('range')] if m]
                    meta_str = f" — {', '.join(meta)}" if meta else ''
                    lines.append(f"- {prepared} {sp.get('name', 'Unknown')}{meta_str}")
                lines.append('')
        elif not active_slots:
            lines.append('*No spells.*')
            lines.append('')

        return '\n'.join(lines)

    def inventory_section(self):
        c = self.char
        currency = c.get('currency', {})
        items = c.get('inventory', [])

        cur_str = '  '.join(
            f"{currency.get(k, 0)} {k.upper()}"
            for k in ['pp', 'gp', 'ep', 'sp', 'cp']
            if currency.get(k, 0)
        ) or '—'

        lines = ['## Inventory', '', f"**Currency:** {cur_str}", '']

        if items:
            for item in items:
                qty = item.get('qty', 1)
                name = item.get('name', '')
                desc = item.get('desc', '')
                desc_str = f" — {desc}" if desc else ''
                lines.append(f"- {qty}× {name}{desc_str}")
        else:
            lines.append('*Empty.*')

        lines.append('')
        return '\n'.join(lines)

    def features_section(self):
        features = self.char.get('features', [])
        attacks = self.char.get('attacks', [])

        lines = ['## Features & Traits', '']

        if features:
            for feat in features:
                level_str = f" *(gained level {feat['level']})*" if feat.get('level') else ''
                lines.append(f"### {feat.get('name', 'Feature')}{level_str}")
                if feat.get('desc'):
                    lines.append(feat['desc'])
                lines.append('')
        else:
            lines.append('*None listed.*')
            lines.append('')

        if attacks:
            lines.append('## Attacks')
            lines.append('')
            lines.append('| Name | Bonus | Damage |')
            lines.append('|------|-------|--------|')
            for atk in attacks:
                lines.append(
                    f"| {atk.get('name', '')} | {atk.get('bonus', '')} | {atk.get('damage', '')} |"
                )
            lines.append('')

        return '\n'.join(lines)

    def appearance_section(self):
        c = self.char
        fields = {
            'Age': c.get('age', ''), 'Height': c.get('height', ''),
            'Weight': c.get('weight', ''), 'Eyes': c.get('eyes', ''),
            'Skin': c.get('skin', ''), 'Hair': c.get('hair', ''),
        }
        filled = {k: v for k, v in fields.items() if v}

        backstory = c.get('backstory', '').strip()
        allies = c.get('allies', '').strip()

        if not filled and not backstory and not allies:
            return ''

        lines = ['## Appearance & Backstory', '']

        if filled:
            lines.append('| ' + ' | '.join(filled.keys()) + ' |')
            lines.append('| ' + ' | '.join(['---'] * len(filled)) + ' |')
            lines.append('| ' + ' | '.join(filled.values()) + ' |')
            lines.append('')

        if backstory:
            lines.append('**Backstory:**')
            lines.append(backstory)
            lines.append('')

        if allies:
            lines.append('**Allies & Organizations:**')
            lines.append(allies)
            lines.append('')

        return '\n'.join(lines)

    def edition_2014_section(self):
        c = self.char
        if c.get('edition') != '2014':
            return ''

        lines = ['## Character Details', '']

        for label, key in [
            ('Personality Traits', 'personality_traits'),
            ('Ideals', 'ideals'),
            ('Bonds', 'bonds'),
            ('Flaws', 'flaws'),
        ]:
            value = c.get(key, '').strip()
            if value:
                lines.append(f"**{label}:** {value}")
                lines.append('')

        exhaustion = c.get('exhaustion', 0)
        if exhaustion:
            lines.append(f"**Exhaustion Level:** {exhaustion}")
            lines.append('')

        return '\n'.join(lines)

    def notes_section(self):
        notes = self.char.get('notes', '').strip()
        if not notes:
            return ''
        return '\n'.join(['## Notes', '', notes, ''])

    def build(self):
        sections = [
            self.frontmatter(),
            self.header(),
            self.combat_section(),
            self.stats_section(),
            self.spells_section(),
            self.inventory_section(),
            self.features_section(),
            self.appearance_section(),
            self.edition_2014_section(),
            self.notes_section(),
        ]
        return '\n'.join(s for s in sections if s)


def safe_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()


def convert_character(char, vault_dir):
    """Convert a single character dict to a markdown file in vault_dir."""
    note = CharacterNote(char)
    content = note.build()
    filename = safe_filename(char.get('name', 'Unknown')) + '.md'
    out_path = os.path.join(vault_dir, filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return out_path


def sync_all(vault_dir, character_name=None):
    """Sync all characters (or one by name) from data/character_sheets/ to vault_dir."""
    os.makedirs(vault_dir, exist_ok=True)

    if character_name:
        pattern = os.path.join(DATA_DIR, f"{safe_filename(character_name)}.json")
        files = [pattern] if os.path.exists(pattern) else []
    else:
        files = glob.glob(os.path.join(DATA_DIR, '*.json'))

    if not files:
        print("No character files found.")
        return

    written = []
    errors = []

    for filepath in files:
        try:
            with open(filepath, encoding='utf-8') as f:
                char = json.load(f)
            out_path = convert_character(char, vault_dir)
            written.append((char.get('name', '?'), out_path))
        except Exception as e:
            errors.append((filepath, str(e)))

    for name, path in written:
        print(f"  ✓ {name} → {path}")
    for filepath, err in errors:
        print(f"  ✗ {os.path.basename(filepath)}: {err}")

    print(f"\n{len(written)} note(s) written, {len(errors)} error(s).")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync Tome of Heroes characters to Obsidian vault.')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault directory (or subfolder within it)')
    parser.add_argument('--character', help='Sync only this character by name (optional)')
    args = parser.parse_args()

    print(f"Syncing to: {args.vault}\n")
    sync_all(args.vault, character_name=args.character)
