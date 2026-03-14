"""
Test suite for the Obsidian note exporter (app/json_to_obsidian.py).

Run with:
    pytest tests/
"""

import json
import os
import pytest
from app.json_to_obsidian import CharacterNote, convert_character, sync_all


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def char():
    """A fully-populated 2024 edition character."""
    return {
        "name": "Thorn",
        "class": "Fighter",
        "subclass": "Battle Master",
        "level": 5,
        "race": "Human",
        "background": "Soldier",
        "alignment": "Lawful Good",
        "edition": "2024",
        "stats": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 13, "CHA": 8},
        "saving_throws": {
            "STR": True, "DEX": False, "CON": True,
            "INT": False, "WIS": False, "CHA": False,
        },
        "skills": {
            "Athletics": {"stat": "STR", "prof": True, "expert": False},
            "Perception": {"stat": "WIS", "prof": True, "expert": False},
            "Stealth": {"stat": "DEX", "prof": False, "expert": False},
            "Acrobatics": {"stat": "DEX", "prof": False, "expert": False},
        },
        "hp": {"current": 42, "max": 52, "temp": 5},
        "hit_dice": {"total": 5, "used": 1, "die": "d10"},
        "ac": 18,
        "initiative_bonus": 1,
        "speed": 30,
        "death_saves": {"successes": 1, "failures": 0},
        "inspiration": True,
        "spell_slots": {str(i): {"total": 0, "used": 0} for i in range(1, 10)},
        "spells": [],
        "inventory": [{"name": "Longsword", "qty": 1, "desc": ""}],
        "features": [{"name": "Action Surge", "level": 2, "desc": "Take an extra action."}],
        "attacks": [{"name": "Longsword", "bonus": "+6", "damage": "1d8+3"}],
        "notes": "Remember to use maneuvers.",
        "currency": {"pp": 0, "gp": 50, "ep": 0, "sp": 10, "cp": 0},
        "proficiencies": "All armor, shields, simple and martial weapons.",
        "backstory": "", "allies": "",
        "age": "28", "height": "6'1\"", "weight": "", "eyes": "Brown", "skin": "", "hair": "",
    }


@pytest.fixture
def char_2014(char):
    """A 2014 edition character with personality fields."""
    char["edition"] = "2014"
    char["personality_traits"] = "I face problems head-on."
    char["ideals"] = "Honor in all things."
    char["bonds"] = "My unit is my family."
    char["flaws"] = "I have a weakness for strong drink."
    char["exhaustion"] = 2
    char["conditions"] = []
    return char


@pytest.fixture
def vault(tmp_path):
    """A temporary directory acting as the Obsidian vault."""
    return str(tmp_path / "vault")


@pytest.fixture
def data_dir(tmp_path):
    """A temporary character_sheets directory with one character file."""
    d = tmp_path / "character_sheets"
    d.mkdir()
    return d


# ──────────────────────────────────────────────────────────────────────────────
# FRONTMATTER
# ──────────────────────────────────────────────────────────────────────────────

class TestFrontmatter:
    def test_starts_and_ends_with_fences(self, char):
        fm = CharacterNote(char).frontmatter()
        lines = fm.strip().splitlines()
        assert lines[0] == '---'
        assert lines[-1] == '---'

    def test_contains_name(self, char):
        fm = CharacterNote(char).frontmatter()
        assert 'name: Thorn' in fm

    def test_contains_class_and_level(self, char):
        fm = CharacterNote(char).frontmatter()
        assert 'class: Fighter' in fm
        assert 'level: 5' in fm

    def test_contains_hp_and_ac(self, char):
        fm = CharacterNote(char).frontmatter()
        assert 'hp_current: 42' in fm
        assert 'hp_max: 52' in fm
        assert 'ac: 18' in fm

    def test_contains_edition(self, char):
        fm = CharacterNote(char).frontmatter()
        assert 'edition: "2024"' in fm

    def test_contains_tags(self, char):
        fm = CharacterNote(char).frontmatter()
        assert 'tags:' in fm
        assert 'character' in fm

    def test_inspiration_true(self, char):
        char["inspiration"] = True
        fm = CharacterNote(char).frontmatter()
        assert 'inspiration: true' in fm

    def test_inspiration_false(self, char):
        char["inspiration"] = False
        fm = CharacterNote(char).frontmatter()
        assert 'inspiration: false' in fm


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────

class TestHeader:
    def test_contains_character_name(self, char):
        header = CharacterNote(char).header()
        assert '# Thorn' in header

    def test_contains_class_and_level(self, char):
        header = CharacterNote(char).header()
        assert 'Level 5' in header
        assert 'Fighter' in header

    def test_contains_subclass(self, char):
        header = CharacterNote(char).header()
        assert 'Battle Master' in header

    def test_contains_race_and_background(self, char):
        header = CharacterNote(char).header()
        assert 'Human' in header
        assert 'Soldier' in header


# ──────────────────────────────────────────────────────────────────────────────
# COMBAT SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestCombatSection:
    def test_contains_hp(self, char):
        section = CharacterNote(char).combat_section()
        assert '42/52' in section

    def test_contains_temp_hp_when_nonzero(self, char):
        section = CharacterNote(char).combat_section()
        assert 'temp' in section

    def test_contains_ac(self, char):
        section = CharacterNote(char).combat_section()
        assert '18' in section

    def test_contains_speed(self, char):
        section = CharacterNote(char).combat_section()
        assert '30 ft' in section

    def test_contains_initiative(self, char):
        section = CharacterNote(char).combat_section()
        assert '+1' in section

    def test_contains_hit_dice(self, char):
        section = CharacterNote(char).combat_section()
        assert '5d10' in section
        assert 'used: 1' in section

    def test_inspiration_yes(self, char):
        char["inspiration"] = True
        section = CharacterNote(char).combat_section()
        assert '**Inspiration:** Yes' in section

    def test_inspiration_no(self, char):
        char["inspiration"] = False
        section = CharacterNote(char).combat_section()
        assert '**Inspiration:** No' in section

    def test_death_saves_shown_when_nonzero(self, char):
        char["death_saves"] = {"successes": 2, "failures": 1}
        section = CharacterNote(char).combat_section()
        assert '2/3' in section
        assert '1/3' in section

    def test_death_saves_dash_when_zero(self, char):
        char["death_saves"] = {"successes": 0, "failures": 0}
        section = CharacterNote(char).combat_section()
        assert '—' in section


# ──────────────────────────────────────────────────────────────────────────────
# STATS SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestStatsSection:
    def test_contains_all_ability_scores(self, char):
        section = CharacterNote(char).stats_section()
        for ab in ('STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'):
            assert ab in section

    def test_ability_modifier_calculation(self, char):
        # STR 16 → +3, CHA 8 → -1
        section = CharacterNote(char).stats_section()
        assert '+3' in section
        assert '-1' in section

    def test_proficient_saving_throw_pip(self, char):
        # STR and CON are proficient
        section = CharacterNote(char).stats_section()
        assert '● +6 Strength' in section   # STR 16 mod +3, prof +3 = +6
        assert '○' in section               # non-proficient saves

    def test_proficient_skill_pip(self, char):
        section = CharacterNote(char).stats_section()
        assert '●' in section

    def test_expertise_skill_pip(self, char):
        char["skills"]["Stealth"]["expert"] = True
        section = CharacterNote(char).stats_section()
        assert '◆' in section

    def test_passive_perception(self, char):
        # WIS 13 → +1 mod, proficient in Perception → +3 prof = +4 total, passive = 14
        section = CharacterNote(char).stats_section()
        assert '**Passive Perception:** 14' in section

    def test_proficiencies_shown_when_present(self, char):
        section = CharacterNote(char).stats_section()
        assert 'All armor' in section

    def test_proficiencies_omitted_when_empty(self, char):
        char["proficiencies"] = ""
        section = CharacterNote(char).stats_section()
        assert 'Proficiencies' not in section


# ──────────────────────────────────────────────────────────────────────────────
# SPELLS SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestSpellsSection:
    def test_no_spells_message(self, char):
        section = CharacterNote(char).spells_section()
        assert 'No spells' in section

    def test_active_spell_slots_shown(self, char):
        char["spell_slots"]["1"] = {"total": 4, "used": 1}
        section = CharacterNote(char).spells_section()
        assert '1st' in section
        assert '3/4' in section

    def test_spell_slot_pips(self, char):
        char["spell_slots"]["1"] = {"total": 3, "used": 1}
        section = CharacterNote(char).spells_section()
        assert '●●○' in section

    def test_spellbook_lists_spells(self, char):
        char["spells"] = [
            {"name": "Fireball", "level": 3, "school": "Evocation",
             "casting_time": "1 action", "range": "150 ft", "prepared": True},
        ]
        section = CharacterNote(char).spells_section()
        assert 'Fireball' in section

    def test_prepared_spell_checkmark(self, char):
        char["spells"] = [{"name": "Shield", "level": 1, "prepared": True}]
        section = CharacterNote(char).spells_section()
        assert '✓ Shield' in section

    def test_unprepared_spell_bullet(self, char):
        char["spells"] = [{"name": "Shield", "level": 1, "prepared": False}]
        section = CharacterNote(char).spells_section()
        assert '· Shield' in section

    def test_spells_grouped_by_level(self, char):
        char["spells"] = [
            {"name": "Fireball", "level": 3, "prepared": True},
            {"name": "Shield", "level": 1, "prepared": True},
        ]
        section = CharacterNote(char).spells_section()
        assert section.index('1st') < section.index('3rd')


# ──────────────────────────────────────────────────────────────────────────────
# INVENTORY SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestInventorySection:
    def test_lists_items(self, char):
        section = CharacterNote(char).inventory_section()
        assert 'Longsword' in section

    def test_shows_quantity(self, char):
        char["inventory"] = [{"name": "Arrow", "qty": 20, "desc": ""}]
        section = CharacterNote(char).inventory_section()
        assert '20×' in section

    def test_shows_description_when_present(self, char):
        char["inventory"] = [{"name": "Potion", "qty": 1, "desc": "Heals 2d4+2 HP"}]
        section = CharacterNote(char).inventory_section()
        assert 'Heals 2d4+2 HP' in section

    def test_empty_inventory_message(self, char):
        char["inventory"] = []
        section = CharacterNote(char).inventory_section()
        assert 'Empty' in section

    def test_currency_shown(self, char):
        section = CharacterNote(char).inventory_section()
        assert '50 GP' in section
        assert '10 SP' in section

    def test_zero_currency_omitted(self, char):
        section = CharacterNote(char).inventory_section()
        assert 'PP' not in section
        assert 'EP' not in section


# ──────────────────────────────────────────────────────────────────────────────
# FEATURES SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestFeaturesSection:
    def test_lists_feature_name(self, char):
        section = CharacterNote(char).features_section()
        assert 'Action Surge' in section

    def test_shows_feature_level(self, char):
        section = CharacterNote(char).features_section()
        assert 'level 2' in section

    def test_shows_feature_description(self, char):
        section = CharacterNote(char).features_section()
        assert 'Take an extra action.' in section

    def test_no_features_message(self, char):
        char["features"] = []
        section = CharacterNote(char).features_section()
        assert 'None listed' in section

    def test_attacks_table_shown(self, char):
        section = CharacterNote(char).features_section()
        assert 'Longsword' in section
        assert '+6' in section
        assert '1d8+3' in section

    def test_attacks_omitted_when_empty(self, char):
        char["attacks"] = []
        section = CharacterNote(char).features_section()
        assert '## Attacks' not in section


# ──────────────────────────────────────────────────────────────────────────────
# APPEARANCE SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestAppearanceSection:
    def test_shows_populated_fields(self, char):
        section = CharacterNote(char).appearance_section()
        assert 'Age' in section
        assert '28' in section
        assert 'Brown' in section

    def test_empty_when_no_data(self, char):
        for f in ('age', 'height', 'weight', 'eyes', 'skin', 'hair', 'backstory', 'allies'):
            char[f] = ''
        section = CharacterNote(char).appearance_section()
        assert section == ''

    def test_shows_backstory(self, char):
        char["backstory"] = "Grew up in the mountains."
        section = CharacterNote(char).appearance_section()
        assert 'Grew up in the mountains.' in section

    def test_shows_allies(self, char):
        char["allies"] = "The Iron Watch."
        section = CharacterNote(char).appearance_section()
        assert 'The Iron Watch.' in section


# ──────────────────────────────────────────────────────────────────────────────
# 2014 EDITION SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestEdition2014Section:
    def test_empty_for_2024_character(self, char):
        section = CharacterNote(char).edition_2014_section()
        assert section == ''

    def test_shows_personality_traits(self, char_2014):
        section = CharacterNote(char_2014).edition_2014_section()
        assert 'I face problems head-on.' in section

    def test_shows_ideals_bonds_flaws(self, char_2014):
        section = CharacterNote(char_2014).edition_2014_section()
        assert 'Honor in all things.' in section
        assert 'My unit is my family.' in section
        assert 'I have a weakness for strong drink.' in section

    def test_shows_exhaustion_when_nonzero(self, char_2014):
        section = CharacterNote(char_2014).edition_2014_section()
        assert '**Exhaustion Level:** 2' in section

    def test_omits_exhaustion_when_zero(self, char_2014):
        char_2014["exhaustion"] = 0
        section = CharacterNote(char_2014).edition_2014_section()
        assert 'Exhaustion' not in section

    def test_omits_empty_personality_fields(self, char_2014):
        char_2014["ideals"] = ""
        section = CharacterNote(char_2014).edition_2014_section()
        assert 'Ideals' not in section


# ──────────────────────────────────────────────────────────────────────────────
# NOTES SECTION
# ──────────────────────────────────────────────────────────────────────────────

class TestNotesSection:
    def test_shows_notes(self, char):
        section = CharacterNote(char).notes_section()
        assert 'Remember to use maneuvers.' in section

    def test_empty_when_no_notes(self, char):
        char["notes"] = ""
        section = CharacterNote(char).notes_section()
        assert section == ''


# ──────────────────────────────────────────────────────────────────────────────
# FULL BUILD
# ──────────────────────────────────────────────────────────────────────────────

class TestBuild:
    def test_build_returns_string(self, char):
        result = CharacterNote(char).build()
        assert isinstance(result, str)

    def test_build_contains_all_major_sections(self, char):
        result = CharacterNote(char).build()
        for heading in ('## Combat', '## Ability Scores', '## Spells',
                        '## Inventory', '## Features', '## Notes'):
            assert heading in result

    def test_build_starts_with_frontmatter(self, char):
        result = CharacterNote(char).build()
        assert result.startswith('---')

    def test_build_2014_includes_character_details(self, char_2014):
        result = CharacterNote(char_2014).build()
        assert '## Character Details' in result

    def test_build_missing_fields_do_not_crash(self):
        """A bare-minimum character dict should not raise."""
        result = CharacterNote({"name": "Ghost"}).build()
        assert 'Ghost' in result


# ──────────────────────────────────────────────────────────────────────────────
# CONVERT CHARACTER (file output)
# ──────────────────────────────────────────────────────────────────────────────

class TestConvertCharacter:
    def test_creates_markdown_file(self, char, vault):
        os.makedirs(vault)
        path = convert_character(char, vault)
        assert os.path.exists(path)

    def test_filename_matches_character_name(self, char, vault):
        os.makedirs(vault)
        path = convert_character(char, vault)
        assert os.path.basename(path) == 'Thorn.md'

    def test_file_contains_character_name(self, char, vault):
        os.makedirs(vault)
        path = convert_character(char, vault)
        with open(path, encoding='utf-8') as f:
            content = f.read()
        assert 'Thorn' in content

    def test_file_is_valid_utf8(self, char, vault):
        os.makedirs(vault)
        path = convert_character(char, vault)
        with open(path, encoding='utf-8') as f:
            f.read()  # should not raise

    def test_filename_sanitizes_special_characters(self, vault):
        os.makedirs(vault)
        char = {"name": "Th/orn<>|"}
        path = convert_character(char, vault)
        assert os.path.exists(path)
        assert '/' not in os.path.basename(path)


# ──────────────────────────────────────────────────────────────────────────────
# SYNC ALL
# ──────────────────────────────────────────────────────────────────────────────

class TestSyncAll:
    def _write_char(self, data_dir, char):
        name = char.get("name", "char")
        path = data_dir / f"{name}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(char, f)

    def test_creates_vault_dir_if_missing(self, char, data_dir, vault, monkeypatch):
        monkeypatch.setattr('app.json_to_obsidian.DATA_DIR', str(data_dir))
        self._write_char(data_dir, char)
        sync_all(vault)
        assert os.path.isdir(vault)

    def test_creates_note_for_each_character(self, char, data_dir, vault, monkeypatch):
        monkeypatch.setattr('app.json_to_obsidian.DATA_DIR', str(data_dir))
        char2 = dict(char, name="Lyra")
        self._write_char(data_dir, char)
        self._write_char(data_dir, char2)
        sync_all(vault)
        files = os.listdir(vault)
        assert 'Thorn.md' in files
        assert 'Lyra.md' in files

    def test_single_character_filter(self, char, data_dir, vault, monkeypatch):
        monkeypatch.setattr('app.json_to_obsidian.DATA_DIR', str(data_dir))
        char2 = dict(char, name="Lyra")
        self._write_char(data_dir, char)
        self._write_char(data_dir, char2)
        sync_all(vault, character_name="Thorn")
        files = os.listdir(vault)
        assert 'Thorn.md' in files
        assert 'Lyra.md' not in files

    def test_no_characters_prints_message(self, data_dir, vault, monkeypatch, capsys):
        monkeypatch.setattr('app.json_to_obsidian.DATA_DIR', str(data_dir))
        sync_all(vault)
        assert 'No character files found' in capsys.readouterr().out

    def test_overwrites_existing_note(self, char, data_dir, vault, monkeypatch):
        monkeypatch.setattr('app.json_to_obsidian.DATA_DIR', str(data_dir))
        self._write_char(data_dir, char)
        sync_all(vault)

        char["level"] = 9
        self._write_char(data_dir, char)
        sync_all(vault)

        with open(os.path.join(vault, 'Thorn.md'), encoding='utf-8') as f:
            content = f.read()
        assert 'level: 9' in content
