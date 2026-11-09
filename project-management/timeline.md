# Timeline (Gantt)

The project ran from **2026-09-23** to **2026-11-09** (about seven
weeks), in six phases (0–5), plus a final phase still remaining
(packaging & deployment). Dates are taken directly from `git log`;
GitHub renders the chart below natively.

```mermaid
gantt
    title Pac-Man — Project Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Phase 0 - Setup
    Repo bootstrap & uv setup                 :done, p0a, 2026-09-23, 1d
    mlx / mazegenerator packages + wrapper    :done, p0b, 2026-09-24, 5d

    section Phase 1 - Parallel groundwork
    Config system (hlaaz)                     :done, p1a, 2026-10-02, 8d
    Assets, main menu, gameplay skeleton (wkerdad) :done, p1b, 2026-10-04, 3d

    section Phase 2 - Integration, Ghost AI & cleanup
    Branch merge & config validation          :done, p2a, 2026-10-18, 1d
    Ghost AI - BFS pathfinding (iterative)    :done, p2b, 2026-10-20, 13d

    section Phase 3 - Core rendering
    Pacman / ghosts / pacgums drawn           :done, p3, 2026-10-28, 1d

    section Phase 4 - Full UI
    Pause, instructions, highscores, cheats, end screen, level flow (18 commits) :done, p4, 2026-11-02, 1d

    section Phase 5 - Hardening
    Highscore dedup fix, config sanitization  :done, p5a, 2026-11-07, 1d
    pydantic removal, flake8/mypy --strict compliance :done, p5b, 2026-11-08, 1d
    Final ghost AI fix (random coords)        :done, p5c, 2026-11-09, 1d
    Root entry point (pac-man.py) + docs      :done, p5d, 2026-11-09, 1d
    Highscore load-on-init & ghost speed fix  :done, p5e, 2026-11-09, 1d

    section Remaining
    Packaging & deployment (Steam/Itch.io)    :active, p6, after p5e, 10d
```

See [`kanban.md`](kanban.md) for the current snapshot of what's done,
in progress and still to do.

## Phases at a glance

| Phase | Dates | Focus |
|-------|-------|-------|
| 0. Setup | 2026-09-23 – 2026-09-28 | Repository bootstrap, dependency management, external packages |
| 1. Parallel groundwork | 2026-10-02 – 2026-10-09 | Config system on one branch; assets/menu/gameplay skeleton on another |
| 2. Integration, Ghost AI & cleanup | 2026-10-18 – 2026-11-01 | Branch merge, full config validation, ghost AI with BFS pathfinding, a directory reorganization along the way |
| 3. Core rendering | 2026-10-28 | Pac-Man, ghosts and pacgums drawn and rendered on screen |
| 4. Full UI | 2026-11-02 | Pause/instructions/highscores/end screens, cheat mode, level flow — **18 commits in one day**, the most productive day of the project |
| 5. Hardening | 2026-11-07 – 2026-11-09 | Highscore & config fixes, pydantic → dataclasses, lint/mypy --strict compliance, root entry point, two more small direct-to-`main` fixes |
| 6. Remaining | — | Packaging & deployment to a public platform |

Four GitHub pull requests mark the points where feature branches were
formally merged back into `main`: **PR #3** `feat/ghost-ai` (merged
2026-10-30), **PR #4** `fix/ghost-ai` (merged 2026-11-02), **PR #5**
`work_with_the_conf` — the big UI/config merge (merged 2026-11-02), and
**PR #6** `fix/highscores` (merged 2026-11-09). Two later commits
(`fix loading the highscore in screen`, `fix speed of ghosts`, both
2026-11-09) were pushed directly to `main` without a PR.
