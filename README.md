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
   - *"Add a field for character backstory on the Notes tab"*
   - *"Fix the HP buttons so they don't go below 0"*
   - *"Change the font color of the character name to gold"*

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
