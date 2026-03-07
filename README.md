# ⚔️ D&D 5e 2024 Character Sheet Server

A local-network character sheet app for D&D 5e (2024 revised edition).
Players connect via their phone browsers — no app install needed.

## Setup

1. **Install Flask** (if you haven't already):
   ```
   pip install flask
   ```

2. **Run the server:**
   ```
   cd dnd_app
   python server.py
   ```

3. **Share with players:**
   The terminal will print something like:
   ```
   🎲 D&D Character Sheet Server
      Local:   http://localhost:5000
      Network: http://192.168.1.42:5000
   ```
   Give players the **Network URL** — they open it in their phone browser.

## Features

- **Main Tab** — Character info, HP tracking with +/− buttons, AC/Initiative/Speed, death saves, inspiration
- **Stats Tab** — All 6 ability scores with auto-calculated modifiers, saving throws, all 18 skills (with proficiency & expertise toggles)
- **Spells Tab** — Spell slot tracking (tap pips to use/recover), full spellbook with prepared toggle
- **Gear Tab** — Inventory with quantity tracking, currency (PP/GP/EP/SP/CP)
- **Notes Tab** — Class features/traits, free-text notes

## Data

Character data is saved as JSON files in the `data/` folder.
Each character gets their own file (e.g., `data/Thorin.json`).
Changes auto-save every ~800ms after any edit.

## Tips

- Each player creates their own character on the shared URL
- The DM can monitor `data/` folder for character state
- Works great on mobile — designed mobile-first
- Runs entirely on your local network, no internet required
