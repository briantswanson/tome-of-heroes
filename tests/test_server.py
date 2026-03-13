"""
Test suite for Tome of Heroes Flask server.

Run with:
    pip install pytest
    pytest tests/
"""

import json
import pytest
import app.server as server


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def client(tmp_path):
    """Flask test client with an isolated temp data directory."""
    data_dir = tmp_path / "character_sheets"
    data_dir.mkdir()

    orig_data_dir = server.DATA_DIR
    orig_game_data_path = server.GAME_DATA_PATH
    orig_cache = server._game_data_cache

    server.DATA_DIR = str(data_dir)
    server.GAME_DATA_PATH = str(tmp_path / "game_data.json")
    server._game_data_cache = None

    server.app.config["TESTING"] = True
    with server.app.test_client() as c:
        yield c

    server.DATA_DIR = orig_data_dir
    server.GAME_DATA_PATH = orig_game_data_path
    server._game_data_cache = orig_cache


def create_char(client, name="Thorn", edition="2024", **kwargs):
    """Helper: POST a new character and return the response."""
    return client.post("/api/characters", json={"name": name, "edition": edition, **kwargs})


# ──────────────────────────────────────────────────────────────────────────────
# INDEX
# ──────────────────────────────────────────────────────────────────────────────

class TestIndex:
    def test_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_returns_html(self, client):
        r = client.get("/")
        assert b"Tome of Heroes" in r.data


# ──────────────────────────────────────────────────────────────────────────────
# CHARACTER LIST
# ──────────────────────────────────────────────────────────────────────────────

class TestCharacterList:
    def test_empty_list(self, client):
        r = client.get("/api/characters")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_list_after_create(self, client):
        create_char(client, "Lyra")
        data = client.get("/api/characters").get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Lyra"

    def test_list_multiple_characters(self, client):
        create_char(client, "Lyra")
        create_char(client, "Thorn")
        names = {c["name"] for c in client.get("/api/characters").get_json()}
        assert names == {"Lyra", "Thorn"}

    def test_list_includes_summary_fields(self, client):
        create_char(client, "Lyra", level=5, **{"class": "Wizard"})
        entry = client.get("/api/characters").get_json()[0]
        assert entry["level"] == 5
        assert entry["class"] == "Wizard"
        assert entry["edition"] == "2024"

    def test_list_includes_id(self, client):
        create_char(client, "Lyra")
        entry = client.get("/api/characters").get_json()[0]
        assert "id" in entry


# ──────────────────────────────────────────────────────────────────────────────
# CREATE CHARACTER
# ──────────────────────────────────────────────────────────────────────────────

class TestCreateCharacter:
    def test_create_returns_ok(self, client):
        r = create_char(client, "Aldric")
        assert r.status_code == 200
        assert r.get_json()["ok"] is True

    def test_create_returns_id(self, client):
        r = create_char(client, "Aldric")
        assert "id" in r.get_json()

    def test_create_2024_has_required_fields(self, client):
        create_char(client, "Aldric", edition="2024")
        c = client.get("/api/characters/Aldric").get_json()
        for field in ("stats", "skills", "saving_throws", "spell_slots",
                      "hp", "inventory", "features", "attacks", "currency"):
            assert field in c, f"missing field: {field}"

    def test_create_2024_default_edition(self, client):
        create_char(client, "Aldric", edition="2024")
        c = client.get("/api/characters/Aldric").get_json()
        assert c["edition"] == "2024"

    def test_create_2024_attacks_empty(self, client):
        create_char(client, "Aldric")
        c = client.get("/api/characters/Aldric").get_json()
        assert c["attacks"] == []

    def test_create_2024_default_hp(self, client):
        create_char(client, "Aldric")
        c = client.get("/api/characters/Aldric").get_json()
        assert c["hp"]["current"] == 10
        assert c["hp"]["max"] == 10
        assert c["hp"]["temp"] == 0

    def test_create_2024_default_stats(self, client):
        create_char(client, "Aldric")
        c = client.get("/api/characters/Aldric").get_json()
        for ab in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
            assert c["stats"][ab] == 10

    def test_create_2014_has_personality_fields(self, client):
        create_char(client, "Aldric", edition="2014")
        c = client.get("/api/characters/Aldric").get_json()
        for field in ("personality_traits", "ideals", "bonds", "flaws"):
            assert field in c, f"missing 2014 field: {field}"

    def test_create_2014_has_exhaustion(self, client):
        create_char(client, "Aldric", edition="2014")
        c = client.get("/api/characters/Aldric").get_json()
        assert c["exhaustion"] == 0
        assert c["conditions"] == []

    def test_create_custom_fields_applied(self, client):
        create_char(client, "Aldric", level=7, **{"class": "Fighter", "race": "Dwarf"})
        c = client.get("/api/characters/Aldric").get_json()
        assert c["level"] == 7
        assert c["class"] == "Fighter"
        assert c["race"] == "Dwarf"

    def test_create_default_spell_slots(self, client):
        create_char(client, "Aldric")
        c = client.get("/api/characters/Aldric").get_json()
        for level in [str(i) for i in range(1, 10)]:
            assert c["spell_slots"][level]["total"] == 0
            assert c["spell_slots"][level]["used"] == 0


# ──────────────────────────────────────────────────────────────────────────────
# GET CHARACTER
# ──────────────────────────────────────────────────────────────────────────────

class TestGetCharacter:
    def test_get_existing(self, client):
        create_char(client, "Mira")
        r = client.get("/api/characters/Mira")
        assert r.status_code == 200
        assert r.get_json()["name"] == "Mira"

    def test_get_not_found_returns_404(self, client):
        r = client.get("/api/characters/DoesNotExist")
        assert r.status_code == 404

    def test_get_applies_migration(self, client):
        """A character file missing 'attacks' gets it added on read."""
        create_char(client, "Mira")
        path = server.char_path("Mira")
        with open(path) as f:
            data = json.load(f)
        del data["attacks"]
        with open(path, "w") as f:
            json.dump(data, f)

        c = client.get("/api/characters/Mira").get_json()
        assert "attacks" in c
        assert c["attacks"] == []


# ──────────────────────────────────────────────────────────────────────────────
# UPDATE CHARACTER
# ──────────────────────────────────────────────────────────────────────────────

class TestUpdateCharacter:
    def test_update_returns_ok(self, client):
        create_char(client, "Ren")
        c = client.get("/api/characters/Ren").get_json()
        r = client.put("/api/characters/Ren", json=c)
        assert r.get_json()["ok"] is True

    def test_update_persists_changes(self, client):
        create_char(client, "Ren")
        c = client.get("/api/characters/Ren").get_json()
        c["level"] = 12
        c["notes"] = "dragon slayer"
        client.put("/api/characters/Ren", json=c)

        updated = client.get("/api/characters/Ren").get_json()
        assert updated["level"] == 12
        assert updated["notes"] == "dragon slayer"

    def test_update_hp(self, client):
        create_char(client, "Ren")
        c = client.get("/api/characters/Ren").get_json()
        c["hp"]["current"] = 3
        c["hp"]["max"] = 45
        client.put("/api/characters/Ren", json=c)

        updated = client.get("/api/characters/Ren").get_json()
        assert updated["hp"]["current"] == 3
        assert updated["hp"]["max"] == 45

    def test_update_skills(self, client):
        create_char(client, "Ren")
        c = client.get("/api/characters/Ren").get_json()
        c["skills"]["Stealth"]["prof"] = True
        client.put("/api/characters/Ren", json=c)

        updated = client.get("/api/characters/Ren").get_json()
        assert updated["skills"]["Stealth"]["prof"] is True


# ──────────────────────────────────────────────────────────────────────────────
# DELETE CHARACTER
# ──────────────────────────────────────────────────────────────────────────────

class TestDeleteCharacter:
    def test_delete_removes_character(self, client):
        create_char(client, "Kael")
        client.delete("/api/characters/Kael")
        assert client.get("/api/characters/Kael").status_code == 404

    def test_delete_returns_ok(self, client):
        create_char(client, "Kael")
        r = client.delete("/api/characters/Kael")
        assert r.get_json()["ok"] is True

    def test_delete_nonexistent_still_ok(self, client):
        r = client.delete("/api/characters/Ghost")
        assert r.status_code == 200
        assert r.get_json()["ok"] is True

    def test_delete_only_removes_target(self, client):
        create_char(client, "Kael")
        create_char(client, "Lyra")
        client.delete("/api/characters/Kael")
        names = {c["name"] for c in client.get("/api/characters").get_json()}
        assert "Lyra" in names
        assert "Kael" not in names


# ──────────────────────────────────────────────────────────────────────────────
# GAME DATA
# ──────────────────────────────────────────────────────────────────────────────

class TestGameData:
    def test_no_file_returns_empty_structure(self, client):
        r = client.get("/api/game-data?edition=2024")
        assert r.status_code == 200
        data = r.get_json()
        assert data["races"] == []
        assert data["classes"] == []
        assert data["backgrounds"] == []
        assert data["spells"] == []

    def test_returns_correct_2024_data(self, client):
        game_data = {
            "2024": {"races": [{"name": "Elf"}], "classes": [], "backgrounds": [], "spells": []},
            "2014": {"races": [{"name": "Dwarf"}], "classes": [], "backgrounds": [], "spells": []},
        }
        with open(server.GAME_DATA_PATH, "w") as f:
            json.dump(game_data, f)
        server._game_data_cache = None

        r = client.get("/api/game-data?edition=2024").get_json()
        assert r["races"][0]["name"] == "Elf"

    def test_returns_correct_2014_data(self, client):
        game_data = {
            "2024": {"races": [{"name": "Elf"}], "classes": [], "backgrounds": [], "spells": []},
            "2014": {"races": [{"name": "Dwarf"}], "classes": [], "backgrounds": [], "spells": []},
        }
        with open(server.GAME_DATA_PATH, "w") as f:
            json.dump(game_data, f)
        server._game_data_cache = None

        r = client.get("/api/game-data?edition=2014").get_json()
        assert r["races"][0]["name"] == "Dwarf"

    def test_defaults_to_2024_when_no_edition_param(self, client):
        game_data = {
            "2024": {"races": [{"name": "Elf"}], "classes": [], "backgrounds": [], "spells": []},
        }
        with open(server.GAME_DATA_PATH, "w") as f:
            json.dump(game_data, f)
        server._game_data_cache = None

        r = client.get("/api/game-data").get_json()
        assert r["races"][0]["name"] == "Elf"


# ──────────────────────────────────────────────────────────────────────────────
# CHARACTER MIGRATION
# ──────────────────────────────────────────────────────────────────────────────

class TestMigration:
    def test_missing_edition_defaults_to_2024(self):
        result = server.migrate_character({"name": "Test"})
        assert result["edition"] == "2024"

    def test_missing_rest_system_defaults_to_standard(self):
        result = server.migrate_character({"name": "Test", "edition": "2024"})
        assert result["rest_system"] == "standard"

    def test_missing_attacks_gets_empty_list(self):
        result = server.migrate_character({"name": "Test", "edition": "2024"})
        assert result["attacks"] == []

    def test_missing_appearance_fields_added(self):
        result = server.migrate_character({"name": "Test", "edition": "2024"})
        for field in ("backstory", "allies", "proficiencies", "age",
                      "height", "weight", "eyes", "skin", "hair"):
            assert field in result, f"missing field: {field}"
            assert result[field] == ""

    def test_2014_personality_fields_added(self):
        result = server.migrate_character({"name": "Test", "edition": "2014"})
        for field in ("personality_traits", "ideals", "bonds", "flaws"):
            assert field in result, f"missing 2014 field: {field}"

    def test_2014_exhaustion_and_conditions_added(self):
        result = server.migrate_character({"name": "Test", "edition": "2014"})
        assert result["exhaustion"] == 0
        assert result["conditions"] == []

    def test_existing_fields_not_overwritten(self):
        char = {
            "name": "Test",
            "edition": "2014",
            "exhaustion": 3,
            "personality_traits": "Bold and reckless",
            "attacks": [{"name": "Sword"}],
        }
        result = server.migrate_character(char)
        assert result["exhaustion"] == 3
        assert result["personality_traits"] == "Bold and reckless"
        assert result["attacks"] == [{"name": "Sword"}]

    def test_idempotent(self):
        """Running migration twice produces the same result."""
        char = {"name": "Test", "edition": "2014"}
        once = server.migrate_character(char.copy())
        twice = server.migrate_character(once.copy())
        assert once == twice


# ──────────────────────────────────────────────────────────────────────────────
# PDF EXPORT
# ──────────────────────────────────────────────────────────────────────────────

class TestPDFExport:
    def test_pdf_returns_200(self, client):
        create_char(client, "Seraph")
        r = client.get("/api/characters/Seraph/pdf")
        assert r.status_code == 200

    def test_pdf_content_type(self, client):
        create_char(client, "Seraph")
        r = client.get("/api/characters/Seraph/pdf")
        assert "application/pdf" in r.content_type

    def test_pdf_is_valid_pdf_bytes(self, client):
        create_char(client, "Seraph")
        r = client.get("/api/characters/Seraph/pdf")
        assert r.data[:4] == b"%PDF"

    def test_pdf_not_found_returns_404(self, client):
        r = client.get("/api/characters/Nobody/pdf")
        assert r.status_code == 404

    def test_pdf_for_2014_character(self, client):
        create_char(client, "Seraph", edition="2014")
        r = client.get("/api/characters/Seraph/pdf")
        assert r.status_code == 200
        assert r.data[:4] == b"%PDF"
