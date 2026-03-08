from flask import Flask, request, jsonify, send_from_directory, send_file
import json
import os
import glob
from pdf_export import generate_pdf

app = Flask(__name__, static_folder='static')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
GAME_DATA_PATH = os.path.join(os.path.dirname(__file__), 'game_data.json')
os.makedirs(DATA_DIR, exist_ok=True)

_game_data_cache = None


def load_game_data():
    global _game_data_cache
    if _game_data_cache is None:
        if os.path.exists(GAME_DATA_PATH):
            with open(GAME_DATA_PATH) as f:
                _game_data_cache = json.load(f)
        else:
            _game_data_cache = {
                "2024": {
                    "races": [],
                    "classes": [],
                    "backgrounds": [],
                    "spells": []},
                "2014": {
                    "races": [],
                    "classes": [],
                    "backgrounds": [],
                    "spells": []}}
    return _game_data_cache


def char_path(name):
    safe = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    return os.path.join(DATA_DIR, f"{safe}.json")


def migrate_character(char):
    if 'edition' not in char:
        char['edition'] = '2024'
    if 'rest_system' not in char:
        char['rest_system'] = 'standard'
    if char.get('edition') == '2014':
        for f in ['personality_traits', 'ideals', 'bonds', 'flaws']:
            if f not in char:
                char[f] = ''
        if 'exhaustion' not in char:
            char['exhaustion'] = 0
        if 'conditions' not in char:
            char['conditions'] = []
    # v4 fields — official sheet parity
    if 'attacks' not in char:
        char['attacks'] = []
    for f in ['backstory', 'allies', 'proficiencies', 'age', 'height', 'weight', 'eyes', 'skin', 'hair']:
        if f not in char:
            char[f] = ''
    return char


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/game-data', methods=['GET'])
def game_data():
    edition = request.args.get('edition', '2024')
    data = load_game_data()
    return jsonify(data.get(edition, data.get('2024', {})))


@app.route('/api/characters', methods=['GET'])
def list_characters():
    files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    chars = []
    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
                chars.append(
                    {
                        'id': os.path.basename(f)[
                            :-5],
                        'name': data.get(
                            'name',
                            ''),
                        'class': data.get(
                            'class',
                            ''),
                        'level': data.get(
                            'level',
                            1),
                        'edition': data.get(
                            'edition',
                            '2024'),
                        'race': data.get(
                            'race',
                            '')})
        except BaseException:
            pass
    return jsonify(chars)


@app.route('/api/characters/<name>', methods=['GET'])
def get_character(name):
    p = char_path(name)
    if not os.path.exists(p):
        return jsonify({'error': 'Not found'}), 404
    with open(p) as f:
        return jsonify(migrate_character(json.load(f)))


@app.route('/api/characters/<name>', methods=['PUT'])
def save_character(name):
    with open(char_path(name), 'w') as f:
        json.dump(request.json, f, indent=2)
    return jsonify({'ok': True})


@app.route('/api/characters', methods=['POST'])
def create_character():
    data = request.json
    name = data.get('name', 'New Character')
    edition = data.get('edition', '2024')
    base = {
        "name": name,
        "edition": edition,
        "class": "",
        "subclass": "",
        "race": "",
        "background": "",
        "alignment": "",
        "level": 1,
        "xp": 0,
        "proficiency_bonus": 2,
        "stats": {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10},
        "saving_throws": {"STR": False, "DEX": False, "CON": False, "INT": False, "WIS": False, "CHA": False},
        "skills": {
            "Acrobatics": {"stat": "DEX", "prof": False, "expert": False},
            "Animal Handling": {"stat": "WIS", "prof": False, "expert": False},
            "Arcana": {"stat": "INT", "prof": False, "expert": False},
            "Athletics": {"stat": "STR", "prof": False, "expert": False},
            "Deception": {"stat": "CHA", "prof": False, "expert": False},
            "History": {"stat": "INT", "prof": False, "expert": False},
            "Insight": {"stat": "WIS", "prof": False, "expert": False},
            "Intimidation": {"stat": "CHA", "prof": False, "expert": False},
            "Investigation": {"stat": "INT", "prof": False, "expert": False},
            "Medicine": {"stat": "WIS", "prof": False, "expert": False},
            "Nature": {"stat": "INT", "prof": False, "expert": False},
            "Perception": {"stat": "WIS", "prof": False, "expert": False},
            "Performance": {"stat": "CHA", "prof": False, "expert": False},
            "Persuasion": {"stat": "CHA", "prof": False, "expert": False},
            "Religion": {"stat": "INT", "prof": False, "expert": False},
            "Sleight of Hand": {"stat": "DEX", "prof": False, "expert": False},
            "Stealth": {"stat": "DEX", "prof": False, "expert": False},
            "Survival": {"stat": "WIS", "prof": False, "expert": False},
        },
        "hp": {"current": 10, "max": 10, "temp": 0},
        "hit_dice": {"total": 1, "used": 0, "die": "d8"},
        "ac": 10,
        "initiative_bonus": 0,
        "speed": 30,
        "death_saves": {"successes": 0, "failures": 0},
        "spell_slots": {str(i): {"total": 0, "used": 0} for i in range(1, 10)},
        "spells": [],
        "inventory": [],
        "features": [],
        "notes": "",
        "inspiration": False,
        "currency": {"pp": 0, "gp": 0, "ep": 0, "sp": 0, "cp": 0},
    }
    if edition == '2014':
        base.update({"personality_traits": "", "ideals": "", "bonds": "",
                    "flaws": "", "exhaustion": 0, "conditions": []})
    base.update(data)
    with open(char_path(name), 'w') as f:
        json.dump(base, f, indent=2)
    return jsonify({'ok': True, 'id': name})


@app.route('/api/characters/<name>', methods=['DELETE'])
def delete_character(name):
    p = char_path(name)
    if os.path.exists(p):
        os.remove(p)
    return jsonify({'ok': True})


@app.route('/api/characters/<name>/pdf', methods=['GET'])
def export_pdf(name):
    p = char_path(name)
    if not os.path.exists(p):
        return jsonify({'error': 'Not found'}), 404
    with open(p) as f:
        char = migrate_character(json.load(f))
    buf = generate_pdf(char)
    filename = f"{char.get('name', 'character').replace(' ', '_')}_sheet.pdf"
    return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=filename)


if __name__ == '__main__':
    import socket
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except BaseException:
        local_ip = '127.0.0.1'
    print("\n🎲 D&D Character Sheet Server (5e 2014 + 2024)")
    print("   Local:   http://localhost:5000")
    print(f"   Network: http://{local_ip}:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
