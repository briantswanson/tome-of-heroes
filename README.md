# ⚔️ D&D 5e 2024 Character Sheet Server

A local-network character sheet app for D&D 5e (2024 revised edition).
Players connect via their phone browsers — no app install needed.

## Setup

1. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

   > **Python version note:** This project requires **Python 3.8**. The `reportlab` dependency is pinned to `3.6.13` for compatibility — newer versions require Python 3.9+.

2. **Run the server:**

   ```
   cd tome-of-heroes
   python main.py
   ```

3. **Share with players:**
   The terminal will print something like:
   ```
   🎲 D&D Character Sheet Server
      Local:   http://localhost:5000
      Network: http://192.168.1.42:5000
   ```
   Give players the **Network URL** — they open it in their phone browser.

## Flake8 and Tests

# Run Flake 8 on entire directory

```
python -m flake8 .
```

# Run test suite

```
python -m pytest
```

## Features

- **Main Tab** — Character info, HP tracking with +/− buttons, AC/Initiative/Speed, death saves, inspiration
- **Stats Tab** — All 6 ability scores with auto-calculated modifiers, saving throws, all 18 skills (with proficiency & expertise toggles)
- **Spells Tab** — Spell slot tracking (tap pips to use/recover), full spellbook with prepared toggle
- **Gear Tab** — Inventory with quantity tracking, currency (PP/GP/EP/SP/CP); Attacks & Spellcasting table with `🎲 ATK` and `💥 DMG` roll buttons per attack — tapping a button rolls instantly and shows a popup with the result (crit/fumble highlighted), also logging to the Dice tab history and Party Roll Log
- **Notes Tab** — Class features/traits, free-text notes
- **Dice Tab** — Dice roller with three modes:
  - *Normal* — Build a roll by clicking dice buttons (e.g. `+d6`, `+d4`) or type a formula directly (e.g. `2d4 + 1d6 + 4`). Supports any mix of dice types and flat bonuses.
  - *Skill Check* — Rolls d20 with your character's skill modifier pre-applied; supports Advantage/Disadvantage
  - *Saving Throw* — Rolls d20 with your character's save modifier pre-applied; supports Advantage/Disadvantage
  - *Party Roll Log* — Live feed of every roll made by all players connected to the server (powered by Server-Sent Events). Shows character name, roll label, total, and breakdown in real time.
- **Rules Tab** — New player cheat sheet split into two sections:
  - *Out of Combat* — All 18 skills with descriptions, ability score explanations, movement mechanics (walk, run, jump, climb, swim), and status conditions
  - *Combat* — Action economy (Action, Bonus Action, Reaction, Free Action), common actions (Attack, Dash, Dodge, Help, Hide, Ready, Use Object), and combat status conditions
- **Rules Tab** — New player cheat sheet with two subtabs:
  - *Reference* — All 18 skills with descriptions, ability score explanations, movement mechanics (walk, run, jump, climb, swim), action economy, common combat actions, and status conditions
  - *Homebrew Rules* — Campaign-specific rules added by the DM. Rules persist on the server and are shared across all characters. Supports adding, editing, and deleting entries, organised by category (General, Combat, Magic, Skills, Exploration, Character Creation, Other). Data is stored in `data/house_rules.json`.

## Frontend Architecture

The frontend is split into feature-scoped CSS and JS files. No bundler or module system — all files share global scope and are loaded in dependency order via `<link>` and `<script src>` tags in `static/index.html`.

### CSS — `static/css/`

| File | Covers |
|------|--------|
| `tokens.css` | CSS custom properties (`:root` vars), reset, `body` |
| `shell.css` | App chrome: screens, header, tab bar, save indicator |
| `shared-forms.css` | `.section-title`, `.add-form`, `.add-btn` used across tabs |
| `char-list.css` | Character list screen |
| `creator.css` | Character creator screen |
| `sheet-main.css` | Main tab: HP, combat stats, death saves, exhaustion, personality |
| `sheet-stats.css` | Stats tab: ability boxes, skill list, passive perception |
| `sheet-spells.css` | Spells tab: spell slots, spell list entries |
| `sheet-inventory.css` | Gear tab: attacks table, item list, currency grid |
| `sheet-features.css` | Notes tab: feature cards, notes textarea |
| `rest.css` | Rest system buttons and layout |
| `modals.css` | All modal overlays and hit die / full rest dialogs |
| `dice.css` | Dice tab: die buttons, roll history, party log |
| `sheet-rules.css` | Rules tab: subtabs, reference cards, ability grid |
| `house-rules.css` | Homebrew rules list and edit forms |
| `stretch-tracker.css` | Stretch tracker screen |

### JS — `static/js/`

Load order matters — later files depend on earlier ones.

| File | Responsibilities |
|------|-----------------|
| `utils.js` | Constants (`ABILITIES`, `SKILLS_DEF`, etc.) and math helpers (`getMod`, `getProfBonus`, `escHtml`) |
| `api.js` | Shared state (`currentChar`, `gameData`), `apiGet/Post/Put/Delete`, `loadGameData`, `populateSpellDatalist` |
| `char-list.js` | `loadCharList`, `deleteChar` |
| `creator.js` | Full character creator flow |
| `sheet-render.js` | All `render*` functions that read `currentChar` and update the DOM |
| `sheet-mutations.js` | All user input handlers that write to `currentChar` and call `scheduleSave` |
| `sheet-core.js` | `loadCharacter`, `saveCharacter`, `scheduleSave`, `switchTab`, `downloadPDF` |
| `dice.js` | Dice roller state, roll logic, history, attack/damage rolls |
| `party-log.js` | SSE connection and party roll log rendering |
| `rest.js` | Rest modals (short, long, good, relax, sanctuary) |
| `stretch-tracker.js` | Stretch tracker state and all tracker functions |
| `house-rules.js` | House rules CRUD and rendering |

### Adding a new feature

1. Create `static/css/<feature>.css` and `static/js/<feature>.js`
2. Add the `<link>` in `index.html` after the most closely related existing CSS file
3. Add the `<script src>` in `index.html` after any JS files your feature depends on
4. Add HTML markup directly to `index.html`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/characters` | List all characters |
| POST | `/api/characters` | Create a new character |
| GET | `/api/characters/<name>` | Get a character |
| PUT | `/api/characters/<name>` | Save a character |
| DELETE | `/api/characters/<name>` | Delete a character |
| GET | `/api/characters/<name>/pdf` | Export character sheet as PDF |
| POST | `/api/rolls` | Broadcast a roll event to all connected clients |
| GET | `/api/rolls/stream` | SSE stream — subscribe to live roll events from all players |

## Data

Character data is saved as JSON files in the `data/character_sheets/` folder.
Each character gets their own file (e.g., `data/character_sheets/Thorin.json`).
Changes auto-save every ~800ms after any edit.

## Tips

- Each player creates their own character on the shared URL
- The DM can monitor `data/` folder for character state
- Works great on mobile — designed mobile-first
- Runs entirely on your local network, no internet required

---

## Contributing (for friends using Claude Code)

Want to suggest a change or fix something? Here's how to do it using Claude Code, even if you're not a developer.

### What you'll need

- [Claude Code](https://claude.ai/code) installed and signed in
- This repo cloned to your computer (ask Brian if you need help with this)
- A GitHub account

### Step-by-step: make a change and open a PR

1. **Open Claude Code** in the project folder (`dnd-character-sheet/`).

2. **Describe what you want to change** in plain English. For example:
   - _"Add a field for character backstory on the Notes tab"_
   - _"Fix the HP buttons so they don't go below 0"_
   - _"Change the font color of the character name to gold"_

   Claude Code will make the changes for you.

3. **Create a branch for your change.** Tell Claude Code:

   > "Create a new branch called `feature/your-feature-name` and commit my changes."

   Claude Code will handle the git commands.

4. **Push the branch and open a pull request.** Tell Claude Code:

   > "Push this branch and open a pull request on GitHub. Title it something descriptive and explain what changed."

   Claude Code will push the branch and create the PR for you.

5. **That's it!** Brian will review the PR and merge it if it looks good.

### Tips

- Keep each PR focused on one thing — it's easier to review.
- If you're not sure if your idea is a good fit, open a GitHub Issue first to discuss it before building it.
- You can describe changes in plain English — you don't need to know how to code.
- If something breaks, just tell Claude Code what went wrong and it'll help fix it.
