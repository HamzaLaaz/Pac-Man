# Project Analysis & Key Decisions

The main technical choices made during the project, and why.

## Use the assigned external maze generator as-is

The subject requires using another group's "A-Maze-ing" package rather
than writing a generator. We bundled the assigned `mazegenerator` wheel
as a local dependency (`mazegenerator/`) and call it exactly as its
interface expects (`MazeGenerator(size=..., perfect=False, seed=...)`),
wrapping only the call site in error handling — never modifying the
package itself. This keeps us compliant and isolates any upstream bug
behind a single `try/except` in `game_screen.py`.

## JSON config with hand-written comment stripping

The subject requires a config file in JSON that also supports comments,
which standard `json` does not. Rather than pull in a third-party
"JSON5"-like library, we wrote a small character-by-character comment
stripper (`Config.remove_comments`) that understands `#`, `//` and
`/* */`, and is careful not to strip anything inside quoted strings.
This avoided a dependency for a genuinely small amount of logic, at the
cost of a few bugs along the way (see
[`acceptance-tests.md`](acceptance-tests.md)).

## Replacing `pydantic` with standard-library `dataclasses`

The config layer was first built on `pydantic` for validation. It was
later rewritten with plain `@dataclass` definitions and manual
clamping/validation functions (`Config._clamp`, `_validate_*`). This
removed a runtime dependency, kept the validation logic fully visible
and testable, and made the strict `mypy` pass easier, since `pydantic`'s
own typing interacts awkwardly with `mypy --strict` in some versions, also to simplify packaging.

## Two branches running in parallel from the start

To make progress on both the gameplay/UI side and the config side at the
same time, the two of us worked on separate branches
(`feat/config-parsing` vs. direct commits on `main`) from very early on.
This did speed up early progress, but both branches ended up touching
shared files (`main.py`, the `screens/` package), which is the direct
cause of the merge conflicts discussed in
[`team-organization.md`](team-organization.md). In hindsight, agreeing
on file/module ownership before splitting up would have avoided that
cost.

## JSON file for highscores, not a database

The subject leaves the highscore storage mechanism open. A flat JSON
file (`highscores.json`) was chosen over a database because the data is
tiny (10 entries, two fields each), it needs no concurrent access, and
it keeps the project dependency-free and consistent with the JSON config
already in use.

## Cheat mode designed for review, not for players

The cheat-mode feature set (invincibility, level skip, ghost freeze,
extra lives, speed boost, timer reset) was picked specifically to let a
reviewer exercise every win/lose/scoring path quickly during peer
review, rather than to be a "fun" feature — matching the subject's
explicit framing of cheat mode as an evaluation tool.
