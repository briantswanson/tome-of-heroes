from flask import Flask, request, jsonify, send_from_directory, send_file, Response
import json
import os
import glob
import queue
import threading
import time
from .pdf_export import generate_pdf

APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'character_sheets')
GAME_DATA_PATH = os.path.join(ROOT_DIR, 'data', 'game_data.json')
os.makedirs(DATA_DIR, exist_ok=True)

_game_data_cache = None
_roll_subscribers = []
_roll_lock = threading.Lock()


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
    return send_from_directory(STATIC_DIR, 'index.html')


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
        "attacks": [],
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


@app.route('/api/rolls', methods=['POST'])
def post_roll():
    roll = request.json
    roll['timestamp'] = time.time()
    with _roll_lock:
        dead = [q for q in _roll_subscribers if q.full()]
        for q in dead:
            _roll_subscribers.remove(q)
        for q in _roll_subscribers:
            try:
                q.put_nowait(roll)
            except queue.Full:
                pass
    return jsonify({'ok': True})


@app.route('/api/rolls/stream')
def roll_stream():
    def generate():
        q = queue.Queue(maxsize=50)
        with _roll_lock:
            _roll_subscribers.append(q)
        try:
            while True:
                try:
                    roll = q.get(timeout=30)
                    yield f"data: {json.dumps(roll)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            with _roll_lock:
                if q in _roll_subscribers:
                    _roll_subscribers.remove(q)
    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


if __name__ == '__main__':
    import socket
    import sys

    # Fix Unicode/emoji printing on Windows (cp1252 terminals)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except BaseException:
        local_ip = '127.0.0.1'
    print("\n🎲 D&D Character Sheet Server (5e 2014 + 2024)")
    print("   Local:   http://localhost:5000")
    print(f"   Network: http://{local_ip}:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
