# 🚀 Space Warriors

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green?style=for-the-badge&logo=python&logoColor=white)

An arcade-style top-down space shooter! Survive waves of enemies, dodge asteroids, and upgrade your ship to achieve the highest score.

## 🎮 Features
- **Dynamic Waves**: Enemies get faster and more aggressive as you clear levels.
- **Boss Fights**: Take on tough boss enemies that fire spread bullets.
- **Upgrades**: Unlock special ships and collect health boosters in space.
- **Responsive Controls**: Play seamlessly with either Mouse or Keyboard.
- **Customizable**: Tweak sound, music, and control settings from the options menu.

## 🛠️ Installation & Setup

We use `uv` for fast dependency management.

1. **Install uv** (if you haven't already):
   *MacOS / Linux:*
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   *Windows:*
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Sync Dependencies**:
   Navigate to the project directory and run:
   ```bash
   uv sync
   ```

3. **Run the Game**:
   ```bash
   uv run main.py
   ```

## ⌨️ Controls

* **Mouse Control (Default)**: Move ship with the mouse cursor (auto-fires).
* **Keyboard Control**: Use `Left / Right` or `A / D` arrows to move. Press `Space` to shoot.

---

*Footnote: Made using GPT 5.6 Terra Codex CLI, GitHub Copilot, and Antigravity CLI. Initial gameplay was made by me by hand, and the rest was built using Codex and Antigravity CLI.*
