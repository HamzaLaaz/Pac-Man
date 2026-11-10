# Acceptance Test Plan

This is a record of what was
checked and the bugs that testing actually caught, taken from the fix
commits in git history.

## Configuration (`src/config.py`)

| Tested | Result |
|--------|--------|
| Valid config file loads correctly | Pass |
| `#`, `//` and `/* */` comments are stripped, including mixed on one line | Pass (after a fix: `fix(config): resolve comment parser index error and refine sanitization`) |
| Comment-like text inside a quoted JSON string is preserved | Pass |
| Missing file | Falls back to defaults, warning printed, no crash |
| Invalid JSON | Falls back to defaults, warning printed, no crash |
| Out-of-range values (e.g. negative lives, huge level size) | Clamped to defaults, warning printed |
| Fewer than 10 levels supplied | Padded up to 10 with default sizes |
| Unknown keys | Ignored |

## Maze generation

| Tested | Result |
|--------|--------|
| Level 1 uses the configured seed and is reproducible across runs | Pass |
| Later levels are regenerated randomly each run | Pass |
| Maze generator raising an exception | Caught, turned into a clear error, no traceback shown |
| Maze generator returning wrong dimensions | Caught, turned into a clear error |

## Ghost AI (`src/screens/ghost_ai.py`)

| Tested | Result |
|--------|--------|
| Each ghost picks a distinct target strategy by name (Blinky/Pinky/Inky/Clyde) | Pass |
| Ghosts path around walls instead of through them | Failed initially, fixed (`fix(ghost-ai): improve wall collision handling in BFS pathfinding`) |
| Ghost target/movement correctness, including scared mode | Failed initially, fixed (`Fix ghost pathfinding logic, target calculation, and scared state movement`) |
| Ghost respawn after being eaten | Pass |
| Random coordinate generation edge case | Failed initially, fixed (`fix ghost ai and random cords generation`) |

## Highscores (`src/highscores.py`)

| Tested | Result |
|--------|--------|
| Top 10 kept, sorted descending | Pass |
| Duplicate (name, score) pairs not double-counted | Failed initially, fixed (`feat(highscores): prevent duplicate entries and truncate top 10`) |
| Name sanitization (10 chars max, alphanumeric + spaces) | Pass |
| Missing/corrupt highscore file on load | Handled gracefully, no crash |

## Gameplay loop (`src/screens/game_screen.py`, `src/main.py`)

| Tested | Result |
|--------|--------|
| Eating pacgums/super-pacgums updates the score correctly | Pass |
| Eating an edible ghost updates the score and respawns the ghost | Pass |
| Losing all lives triggers game over, with score/name entry | Pass |
| Eating every pacgum wins the level and advances to the next one | Pass |
| Completing the final level triggers the victory screen | Pass |
| Level time limit expiring ends the game | Pass |
| Score and remaining lives carry over between levels | Pass |
| Pause/resume preserves timers correctly (powerup, ghost respawn, level timer) | Pass |

## UI / cheat mode

| Tested | Result |
|--------|--------|
| Main menu → start game / highscores / instructions / exit | Pass |
| Pause menu → resume / back to main menu | Pass |
| Cheat mode toggle and each cheat key (`N`, `I`, `F`, `L`, `O`, `T`) | Pass |

## Static checks (run on every change, not just once)

| Tested | Result |
|--------|--------|
| `make lint` (`flake8` + `mypy`, mandatory flags) | Pass |
| `make lint-strict` (`flake8` + `mypy --strict`) | Pass |
