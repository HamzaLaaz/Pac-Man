# Kanban Board

A snapshot of task status as of **2026-11-09**, reconstructed from the
feature branches, pull requests and commits in git history (no separate
board tool was used during development). See [`timeline.md`](timeline.md)
for the dated Gantt view of the same work.

## Done

- [x] Repository bootstrap, `uv` dependency management
- [x] `mlx` and `mazegenerator` ("A-Maze-ing") packages integrated
- [x] JSON config file with comment support (`#`, `//`, `/* */`)
- [x] Config validation, clamping and safe defaults (no crash on bad input)
- [x] Maze generation via the assigned external package (`perfect=False`)
- [x] Main menu, pause menu, instructions screen, highscores screen
- [x] Pac-Man, ghosts and pacgums rendering
- [x] Ghost AI (BFS pathfinding, per-ghost target strategies, scared mode)
- [x] Collision handling (pacgum / super-pacgum / ghost)
- [x] Scoring, lives, level progression (≥ 10 levels), level timer
- [x] Win / game-over screen with name entry
- [x] Persistent top-10 highscore table (dedup + truncation)
- [x] Cheat mode (invincibility, level skip, ghost freeze, extra lives, speed, timer reset)
- [x] `pydantic` → `dataclasses` refactor (dependency removal)
- [x] `flake8` and `mypy --strict` fully clean (`make lint`, `make lint-strict`)
- [x] Root entry point: `python3 pac-man.py config.json`
- [x] `README.md` and project-management documentation
- [x] Highscore load-on-init fix, ghost speed tuning
- [x] Packaging the codebase