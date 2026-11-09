# Progress Tracking

How each phase actually played out compared to what it set out to do.
No formal burndown chart was kept; progress was tracked through commits,
branches and pull requests on GitHub.

## Phase 0 — Project setup (on time)

**Planned:** get a working repository with `uv`, and the two external
packages (`mlx`, `mazegenerator`) installable. **Actual:** done in under
a week, including one false start (`uv init` committed then reverted the
same day once the dependency layout was figured out).

## Phase 1 — Parallel groundwork (on time, but diverging)

**Planned:** start the config system and the first playable screens at
the same time, on separate branches, to save time. **Actual:** this
happened as planned — `hlaaz` built the config loader
(`feat/config-parsing`) while `wkerdad` built the assets, main menu and a
non-interactive gameplay skeleton directly on `main`. The trade-off
(explained in [`team-organization.md`](team-organization.md)) is that
the two branches touched overlapping files, which cost time later.

## Phase 2 — Integration & Ghost AI (took longer than expected)

**Planned:** merge the config branch, then add ghost movement.
**Actual:** merging took several attempts (`pull the main`,
`merge main into feat/config-parsing`, a later `fixed the merge
problem`), and the ghost AI itself needed multiple correction passes —
wall-collision handling, target calculation per ghost, and "scared mode"
movement were each fixed in separate commits across about two weeks
(2026-10-20 to 2026-11-01). This was the single slowest phase of the
project.

## Phase 3 — Core gameplay rendering (on time)

**Planned:** get Pac-Man, the ghosts and the pacgums actually drawn.
**Actual:** done in a single day (2026-10-28) once the entity classes
existed, confirming the earlier integration work had paid off.

## Phase 4 — Full UI & feature-complete (ahead of schedule)

**Planned:** add the remaining screens (pause, instructions, highscores,
end screen) and cheat mode before the next review. **Actual:** all of it
landed in one day (2026-11-02, **18 commits**) once the core gameplay
was stable — this was the most productive single day of the project and
brought the game to a feature-complete state against the mandatory part
of the subject.

## Phase 5 — Hardening & code quality (iterative, still ongoing)

**Planned:** fix remaining edge cases and make sure the project passes
the subject's lint requirements. **Actual:** covered the highscore
duplicate/truncate logic, several rounds of config-parser sanitization
fixes, a full replacement of `pydantic` with standard-library
`dataclasses` (to drop a dependency and simplify validation), and a pass
to make `flake8` and `mypy --strict` fully clean. The ghost AI received
one more fix for random coordinate generation on 2026-11-09, along with
the root entry point (`pac-man.py`, so the game launches exactly as
`python3 pac-man.py config.json` as required by the subject) and two
further direct-to-`main` fixes the same day (highscore loading on init,
ghost speed tuning) — showing that "hardening" is not strictly
sequential: bugs from earlier phases can resurface and get fixed
alongside newer work.

## Not yet done

- **Deployment / packaging** to a public gaming platform (Steam/Itch.io
  or similar) and the packaging script required by the subject have not
  been started yet — explicitly deferred to a later phase.
- **Automated tests** (`pytest`/`unittest`) are not part of the
  repository; verification so far has been manual (see
  [`acceptance-tests.md`](acceptance-tests.md)) plus the static
  guarantees from `flake8`/`mypy --strict`.
