"""
Generate a printer-friendly D&D 5e 2024 character sheet PDF from character JSON data.
"""
import math
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


# ── Palette ──────────────────────────────────────────────────────────────────
C_BLACK = colors.HexColor('#1a1208')
C_DARK = colors.HexColor('#2a1f0a')
C_GOLD = colors.HexColor('#c9a84c')
C_GOLD_DIM = colors.HexColor('#8a6a2a')
C_RED = colors.HexColor('#8b1a1a')
C_RED_LIGHT = colors.HexColor('#c0392b')
C_PARCHMENT = colors.HexColor('#fdf6e3')
C_PARCHMENT2 = colors.HexColor('#f5ead0')
C_INK = colors.HexColor('#2c1f0a')
C_RULE = colors.HexColor('#c9a84c')
C_GRAY = colors.HexColor('#888888')
C_LIGHT_GRAY = colors.HexColor('#dddddd')
C_GREEN = colors.HexColor('#1a4a2a')
C_BLUE_DARK = colors.HexColor('#1a2a4a')

PAGE_W, PAGE_H = letter
MARGIN = 0.5 * inch
COL_W = (PAGE_W - 2 * MARGIN) / 3


def get_mod(score):
    m = (score - 10) // 2
    return f"+{m}" if m >= 0 else str(m)


def get_prof_bonus(level):
    return math.ceil(level / 4) + 1


ABILITIES = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
ABILITY_NAMES = {
    'STR': 'Strength', 'DEX': 'Dexterity', 'CON': 'Constitution',
    'INT': 'Intelligence', 'WIS': 'Wisdom', 'CHA': 'Charisma'
}
ORDINALS = ['', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']


class CharSheetPDF:
    def __init__(self, char):
        self.char = char
        self.buf = io.BytesIO()
        self.c = canvas.Canvas(self.buf, pagesize=letter)
        self.c.setTitle(f"{char.get('name', 'Character')} — D&D 5e Character Sheet")
        self.pb = get_prof_bonus(char.get('level', 1))

    # ── Drawing helpers ──────────────────────────────────────────────────────

    def set_font(self, name='Helvetica', size=10):
        self.c.setFont(name, size)

    def draw_text(self, x, y, text, font='Helvetica', size=10, color=C_INK, align='left'):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        if align == 'center':
            self.c.drawCentredString(x, y, str(text))
        elif align == 'right':
            self.c.drawRightString(x, y, str(text))
        else:
            self.c.drawString(x, y, str(text))

    def draw_rect(self, x, y, w, h, fill=None, stroke=None, stroke_width=0.5):
        self.c.setLineWidth(stroke_width)
        if fill:
            self.c.setFillColor(fill)
        if stroke:
            self.c.setStrokeColor(stroke)
        self.c.rect(x, y, w, h,
                    fill=1 if fill else 0,
                    stroke=1 if stroke else 0)

    def draw_circle(self, cx, cy, r, fill=None, stroke=None):
        self.c.setLineWidth(0.5)
        if fill:
            self.c.setFillColor(fill)
        if stroke:
            self.c.setStrokeColor(stroke)
        self.c.circle(cx, cy, r, fill=1 if fill else 0, stroke=1 if stroke else 0)

    def draw_rule(self, x, y, w, color=C_RULE, width=0.5):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(x, y, x + w, y)

    def draw_section_header(self, x, y, w, label):
        """Gold bar with white label."""
        h = 14
        self.draw_rect(x, y, w, h, fill=C_RED, stroke=None)
        self.draw_text(x + 4, y + 3.5, label.upper(),
                       font='Helvetica-Bold', size=7,
                       color=C_GOLD, align='left')
        return y - 4  # return bottom of bar

    def draw_field(self, x, y, w, label, value, label_size=6, value_size=9):
        """Underlined field with label above."""
        self.draw_text(x, y, label, font='Helvetica', size=label_size, color=C_GRAY)
        self.draw_rule(x, y - 1, w, color=C_LIGHT_GRAY)
        self.draw_text(x, y - 11, str(value) if value is not None else '',
                       font='Helvetica-Bold', size=value_size, color=C_INK)
        return y - 18

    def draw_box_stat(self, x, y, w, h, label, value, sub=None):
        """Box with a big centered value and a label below."""
        self.draw_rect(x, y, w, h, fill=None, stroke=C_GOLD_DIM, stroke_width=0.75)
        # value
        self.draw_text(x + w / 2, y + h - 18, str(value),
                       font='Helvetica-Bold', size=14, color=C_RED, align='center')
        # label
        self.draw_text(x + w / 2, y + 3, label,
                       font='Helvetica', size=5.5, color=C_GRAY, align='center')
        if sub is not None:
            self.draw_text(x + w / 2, y + h - 30, str(sub),
                           font='Helvetica', size=7, color=C_GOLD_DIM, align='center')

    # ── Sections ────────────────────────────────────────────────────────────

    def draw_header(self):
        c = self.char
        y = PAGE_H - MARGIN

        # Top banner
        self.draw_rect(MARGIN, y - 28, PAGE_W - 2 * MARGIN, 28, fill=C_BLACK, stroke=None)
        self.draw_text(PAGE_W / 2, y - 10,
                       c.get('name', 'Unnamed Adventurer'),
                       font='Helvetica-Bold', size=16, color=C_GOLD, align='center')
        self.draw_text(PAGE_W / 2, y - 22,
                       'D&D 5e 2024 — Character Sheet',
                       font='Helvetica', size=7, color=C_GOLD_DIM, align='center')

        y -= 36

        # Info row
        fields = [
            ('Class', c.get('class', '')),
            ('Subclass', c.get('subclass', '')),
            ('Level', c.get('level', 1)),
            ('Race / Species', c.get('race', '')),
            ('Background', c.get('background', '')),
            ('Proficiency Bonus', f"+{self.pb}"),
        ]
        fw = (PAGE_W - 2 * MARGIN) / len(fields)
        for i, (label, value) in enumerate(fields):
            self.draw_field(MARGIN + i * fw, y, fw - 6, label, value)

        return y - 22

    def draw_ability_scores(self, x, y, w):
        self.draw_section_header(x, y, w, 'Ability Scores')
        y -= 6
        stats = self.char.get('stats', {})
        box_w = (w - 4) / 3
        box_h = 38

        for i, ab in enumerate(ABILITIES):
            col = i % 3
            row = i // 3
            bx = x + col * (box_w + 2)
            by = y - row * (box_h + 4) - box_h

            score = stats.get(ab, 10)
            mod = get_mod(score)

            self.draw_rect(bx, by, box_w, box_h, fill=C_PARCHMENT2, stroke=C_GOLD_DIM, stroke_width=0.75)
            # Ability name
            self.draw_text(bx + box_w / 2, by + box_h - 9,
                           ab, font='Helvetica-Bold', size=7, color=C_RED, align='center')
            # Score
            self.draw_text(bx + box_w / 2, by + box_h - 21,
                           str(score), font='Helvetica-Bold', size=14, color=C_INK, align='center')
            # Modifier
            self.draw_text(bx + box_w / 2, by + 4,
                           mod, font='Helvetica-Bold', size=9, color=C_GOLD_DIM, align='center')

        return y - 2 * (box_h + 4) - 8

    def draw_saving_throws(self, x, y, w):
        self.draw_section_header(x, y, w, 'Saving Throws')
        y -= 6
        stats = self.char.get('stats', {})
        saves = self.char.get('saving_throws', {})

        for ab in ABILITIES:
            score = stats.get(ab, 10)
            base_mod = (score - 10) // 2
            prof = saves.get(ab, False)
            total = base_mod + (self.pb if prof else 0)
            mod_str = f"+{total}" if total >= 0 else str(total)

            # Pip
            if prof:
                self.draw_circle(x + 6, y - 2, 4, fill=C_GOLD, stroke=None)
            else:
                self.draw_circle(x + 6, y - 2, 4, fill=None, stroke=C_GRAY)

            self.draw_text(x + 14, y - 5.5, mod_str, font='Helvetica-Bold', size=8, color=C_INK)
            self.draw_text(x + 32, y - 5.5, ABILITY_NAMES[ab], font='Helvetica', size=8, color=C_INK)
            y -= 13

        return y - 4

    def draw_skills(self, x, y, w):
        self.draw_section_header(x, y, w, 'Skills')
        y -= 6
        skills = self.char.get('skills', {})
        stats = self.char.get('stats', {})

        for name in sorted(skills.keys()):
            sk = skills[name]
            score = stats.get(sk.get('stat', 'STR'), 10)
            base_mod = (score - 10) // 2
            bonus = self.pb * 2 if sk.get('expert') else self.pb if sk.get('prof') else 0
            total = base_mod + bonus
            mod_str = f"+{total}" if total >= 0 else str(total)

            # pip
            if sk.get('expert'):
                self.draw_circle(x + 6, y - 2, 4, fill=C_GOLD, stroke=None)
                # double ring for expertise
                self.draw_circle(x + 6, y - 2, 3, fill=None, stroke=C_PARCHMENT)
            elif sk.get('prof'):
                self.draw_circle(x + 6, y - 2, 4, fill=C_GOLD_DIM, stroke=None)
            else:
                self.draw_circle(x + 6, y - 2, 4, fill=None, stroke=C_GRAY)

            self.draw_text(x + 14, y - 5.5, mod_str, font='Helvetica-Bold', size=7.5, color=C_INK)
            self.draw_text(x + 32, y - 5.5, name, font='Helvetica', size=7.5, color=C_INK)
            self.draw_text(
                x + w - 4,
                y - 5.5,
                sk.get(
                    'stat',
                    ''),
                font='Helvetica',
                size=6,
                color=C_GRAY,
                align='right')
            y -= 12

        return y - 4

    def draw_combat_stats(self, x, y, w):
        self.draw_section_header(x, y, w, 'Combat')
        y -= 6
        c = self.char

        hp = c.get('hp', {})
        cur = hp.get('current', 0)
        mx = hp.get('max', 0)
        tmp = hp.get('temp', 0)

        # HP big display
        self.draw_rect(x, y - 34, w, 34, fill=C_PARCHMENT2, stroke=C_GOLD_DIM, stroke_width=0.75)
        self.draw_text(x + w / 2, y - 12, f"{cur} / {mx}",
                       font='Helvetica-Bold', size=16, color=C_RED, align='center')
        self.draw_text(x + w / 2, y - 23, 'HIT POINTS',
                       font='Helvetica', size=6, color=C_GRAY, align='center')
        self.draw_text(x + w / 2, y - 32, f"Temp: {tmp}",
                       font='Helvetica', size=7, color=C_GRAY, align='center')
        y -= 40

        # AC / Init / Speed row
        stat_w = w / 3
        stats_data = [
            ('AC', c.get('ac', 10)),
            ('Initiative', c.get('initiative_bonus', 0)),
            ('Speed', f"{c.get('speed', 30)} ft"),
        ]
        for i, (label, value) in enumerate(stats_data):
            sx = x + i * stat_w
            self.draw_rect(sx, y - 28, stat_w - 2, 28, fill=C_PARCHMENT2, stroke=C_GOLD_DIM, stroke_width=0.5)
            val_str = f"+{value}" if label == 'Initiative' and isinstance(value, int) and value >= 0 else str(value)
            self.draw_text(sx + (stat_w - 2) / 2, y - 16, val_str,
                           font='Helvetica-Bold', size=13, color=C_INK, align='center')
            self.draw_text(sx + (stat_w - 2) / 2, y - 26, label,
                           font='Helvetica', size=5.5, color=C_GRAY, align='center')
        y -= 34

        # Hit dice / death saves
        hd = c.get('hit_dice', {})
        self.draw_text(x, y - 8, f"Hit Dice: {hd.get('total', 1)}{hd.get('die', 'd8')}  (Used: {hd.get('used', 0)})",
                       font='Helvetica', size=7.5, color=C_INK)
        y -= 14

        ds = c.get('death_saves', {})
        suc = ds.get('successes', 0)
        fail = ds.get('failures', 0)
        self.draw_text(x, y - 8, 'Death Saves:', font='Helvetica-Bold', size=7.5, color=C_INK)
        self.draw_text(x + 60, y - 8, 'Successes:', font='Helvetica', size=7, color=C_INK)
        for i in range(3):
            self.draw_circle(x + 115 + i * 11, y - 5, 4,
                             fill=colors.green if i < suc else None, stroke=colors.green)
        self.draw_text(x + 150, y - 8, 'Failures:', font='Helvetica', size=7, color=C_INK)
        for i in range(3):
            self.draw_circle(x + 190 + i * 11, y - 5, 4,
                             fill=C_RED_LIGHT if i < fail else None, stroke=C_RED_LIGHT)
        y -= 14

        # Inspiration
        insp = c.get('inspiration', False)
        self.draw_circle(x + 6, y - 4, 5, fill=C_GOLD if insp else None, stroke=C_GOLD_DIM)
        self.draw_text(x + 16, y - 7, 'Inspiration', font='Helvetica', size=7.5, color=C_INK)

        return y - 14

    def draw_spell_slots(self, x, y, w):
        self.draw_section_header(x, y, w, 'Spell Slots')
        y -= 6
        slots = self.char.get('spell_slots', {})

        active_slots = {k: v for k, v in slots.items() if v.get('total', 0) > 0}
        if not active_slots:
            self.draw_text(x, y - 10, 'No spell slots configured.',
                           font='Helvetica', size=8, color=C_GRAY)
            return y - 18

        pip_r = 4
        row_h = 14
        for level_str, sl in sorted(active_slots.items(), key=lambda x: int(x[0])):
            level = int(level_str)
            total = sl.get('total', 0)
            used = sl.get('used', 0)

            label = ORDINALS[level] if level > 0 else 'Cantrip'
            self.draw_text(x, y - row_h + 4, f"{label} ({total - used}/{total})",
                           font='Helvetica', size=7.5, color=C_INK)

            px = x + 80
            for i in range(total):
                is_used = i < used
                self.draw_circle(px + i * (pip_r * 2 + 3), y - row_h + 4 + pip_r / 2, pip_r,
                                 fill=C_BLUE_DARK if is_used else C_GOLD,
                                 stroke=C_GOLD_DIM)
            y -= row_h

        return y - 6

    def draw_spells(self, x, y, w):
        self.draw_section_header(x, y, w, 'Spellbook')
        y -= 6
        spells = self.char.get('spells', [])

        if not spells:
            self.draw_text(x, y - 10, 'No spells known.', font='Helvetica', size=8, color=C_GRAY)
            return y - 18

        sorted_spells = sorted(spells, key=lambda s: s.get('level', 0))
        for sp in sorted_spells:
            level = sp.get('level', 0)
            level_str = 'Cantrip' if level == 0 else ORDINALS[level]
            prepared = sp.get('prepared', False)

            # prepared dot
            self.draw_circle(x + 5, y - 4, 3.5,
                             fill=C_GOLD if prepared else None, stroke=C_GOLD_DIM)
            self.draw_text(x + 14, y - 7, sp.get('name', ''),
                           font='Helvetica-Bold', size=8, color=C_INK)
            meta_parts = [level_str]
            if sp.get('school'):
                meta_parts.append(sp['school'])
            if sp.get('casting_time'):
                meta_parts.append(sp['casting_time'])
            if sp.get('range'):
                meta_parts.append(sp['range'])
            self.draw_text(x + 14, y - 16, '  ·  '.join(meta_parts),
                           font='Helvetica', size=6.5, color=C_GRAY)
            y -= 20

            if y < MARGIN + 40:
                break  # avoid overflow (second page not implemented)

        return y - 4

    def draw_inventory(self, x, y, w):
        self.draw_section_header(x, y, w, 'Equipment & Inventory')
        y -= 6
        items = self.char.get('inventory', [])
        currency = self.char.get('currency', {})

        # Currency row
        cur_labels = [('PP', 'pp'), ('GP', 'gp'), ('EP', 'ep'), ('SP', 'sp'), ('CP', 'cp')]
        cw = w / len(cur_labels)
        for i, (label, key) in enumerate(cur_labels):
            cx = x + i * cw
            self.draw_rect(cx, y - 20, cw - 2, 20, fill=C_PARCHMENT2, stroke=C_GOLD_DIM, stroke_width=0.5)
            self.draw_text(cx + (cw - 2) / 2, y - 11, str(currency.get(key, 0)),
                           font='Helvetica-Bold', size=9, color=C_INK, align='center')
            self.draw_text(cx + (cw - 2) / 2, y - 19, label,
                           font='Helvetica', size=5.5, color=C_GRAY, align='center')
        y -= 26

        if not items:
            self.draw_text(x, y - 10, 'Empty.', font='Helvetica', size=8, color=C_GRAY)
            return y - 18

        # Column headers
        self.draw_text(x, y - 8, 'Item', font='Helvetica-Bold', size=7, color=C_GOLD_DIM)
        self.draw_text(x + w - 30, y - 8, 'Qty', font='Helvetica-Bold', size=7, color=C_GOLD_DIM, align='right')
        self.draw_rule(x, y - 10, w, color=C_GOLD_DIM)
        y -= 14

        for item in items:
            self.draw_text(x, y - 7, item.get('name', ''), font='Helvetica-Bold', size=8, color=C_INK)
            self.draw_text(x + w - 4, y - 7, str(item.get('qty', 1)),
                           font='Helvetica', size=8, color=C_INK, align='right')
            if item.get('desc') or item.get('weight'):
                meta = []
                if item.get('weight'):
                    meta.append(f"{item['weight']} lbs")
                if item.get('desc'):
                    meta.append(item['desc'])
                self.draw_text(x + 4, y - 15, ' · '.join(meta), font='Helvetica', size=6.5, color=C_GRAY)
                y -= 8
            self.draw_rule(x, y - 17, w, color=C_LIGHT_GRAY, width=0.3)
            y -= 20

            if y < MARGIN + 30:
                break

        return y - 4

    def draw_features(self, x, y, w):
        self.draw_section_header(x, y, w, 'Features & Traits')
        y -= 6
        features = self.char.get('features', [])
        if not features:
            self.draw_text(x, y - 10, 'None listed.', font='Helvetica', size=8, color=C_GRAY)
            return y - 18

        for feat in features:
            self.draw_text(x, y - 9, feat.get('name', ''), font='Helvetica-Bold', size=8.5, color=C_INK)
            y -= 12
            if feat.get('desc'):
                # Wrap description manually at ~80 chars
                desc = feat['desc']
                words = desc.split()
                line = ''
                for word in words:
                    test = (line + ' ' + word).strip()
                    if len(test) > 80:
                        self.draw_text(x + 4, y - 7, line, font='Helvetica', size=7.5, color=C_INK)
                        y -= 10
                        line = word
                        if y < MARGIN + 30:
                            break
                    else:
                        line = test
                if line:
                    self.draw_text(x + 4, y - 7, line, font='Helvetica', size=7.5, color=C_INK)
                    y -= 10
            y -= 4

            if y < MARGIN + 30:
                break

        return y - 4

    def draw_notes(self, x, y, w):
        self.draw_section_header(x, y, w, 'Notes')
        y -= 6
        notes = self.char.get('notes', '').strip()
        if not notes:
            self.draw_text(x, y - 10, '—', font='Helvetica', size=8, color=C_GRAY)
            return y - 18

        words = notes.split()
        line = ''
        for word in words:
            test = (line + ' ' + word).strip()
            if len(test) > 78:
                self.draw_text(x, y - 8, line, font='Helvetica', size=8, color=C_INK)
                y -= 11
                line = word
                if y < MARGIN + 20:
                    break
            else:
                line = test
        if line:
            self.draw_text(x, y - 8, line, font='Helvetica', size=8, color=C_INK)
            y -= 11
        return y - 4

    # ── Layout ───────────────────────────────────────────────────────────────

    def build(self):
        # Background
        self.draw_rect(0, 0, PAGE_W, PAGE_H, fill=C_PARCHMENT, stroke=None)

        y = self.draw_header()
        y -= 6

        # Draw a subtle top rule
        self.draw_rule(MARGIN, y, PAGE_W - 2 * MARGIN, color=C_GOLD, width=1)
        y -= 8

        col1_x = MARGIN
        col2_x = MARGIN + COL_W + 6
        col3_x = MARGIN + 2 * COL_W + 12

        # ── Column 1: Abilities + Saving Throws + Skills ──────────────────
        y1 = y
        y1 = self.draw_ability_scores(col1_x, y1, COL_W - 6)
        y1 -= 8
        y1 = self.draw_saving_throws(col1_x, y1, COL_W - 6)
        y1 -= 8
        y1 = self.draw_skills(col1_x, y1, COL_W - 6)

        # ── Column 2: Combat + Spell Slots + Spells ───────────────────────
        y2 = y
        y2 = self.draw_combat_stats(col2_x, y2, COL_W - 6)
        y2 -= 8
        y2 = self.draw_spell_slots(col2_x, y2, COL_W - 6)
        y2 -= 8
        y2 = self.draw_spells(col2_x, y2, COL_W - 6)

        # ── Column 3: Inventory + Features + Notes ────────────────────────
        y3 = y
        y3 = self.draw_inventory(col3_x, y3, COL_W - 6)
        y3 -= 8
        y3 = self.draw_features(col3_x, y3, COL_W - 6)
        y3 -= 8
        y3 = self.draw_notes(col3_x, y3, COL_W - 6)

        # Footer
        self.draw_rule(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, color=C_GOLD_DIM, width=0.5)
        self.draw_text(PAGE_W / 2, MARGIN - 8,
                       'D&D 5e 2024 Character Sheet  ·  Generated by Tome of Heroes',
                       font='Helvetica', size=6, color=C_GRAY, align='center')

        self.c.save()
        self.buf.seek(0)
        return self.buf


def generate_pdf(char_data):
    """Generate PDF and return BytesIO buffer."""
    sheet = CharSheetPDF(char_data)
    return sheet.build()
