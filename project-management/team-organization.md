# Team Organization

Two-person team: **wkerdad** (Walid) and **hlaaz** (Hamza).

## Who did what

Based on the commit history, the work split naturally into two tracks
that later merged:

**wkerdad** — project setup and tooling (`uv`, the `mlx`/`mazegenerator`
package wiring), game assets, the main menu, the
entity-rendering code (Pac-Man, ghosts, pacgums all drawn on screen),
and — once the core loop was stable — the rest of the UI in one focused
push: pause screen, instructions screen, highscores screen, end screen,
cheat mode, and the level-flow logic in `main.py`. Also set up the
`Makefile` lint targets to match the subject's requirements and did the
final `flake8`/`mypy --strict` compliance pass.

**hlaaz** — the configuration system end to end: the JSON+comments
parser, validation and clamping rules, and later the `pydantic` →
`dataclasses` rewrite; and the ghost AI: BFS pathfinding, per-ghost
target strategies (Blinky/Pinky/Inky/Clyde), wall-collision handling in
the search, and the highscore de-duplication/truncation logic.

## How decisions were made

With only two people, decisions were made directly between us rather
than through a formal process: whoever was touching a feature owned its
design, and merges were reviewed through GitHub pull requests (#3–#6)
before landing on `main`. Bigger changes — like dropping `pydantic` for
plain `dataclasses` — were agreed on before starting, since they touched
code the other person also depended on.

## Working through conflicts

The hardest part of this project was not any single algorithm — it was
**working on the same codebase at the same time without stepping on each
other**. Early on, we split the work by starting two branches at once:
one for the configuration system, one for the main menu and gameplay
skeleton. That was good for parallel progress, but both branches ended
up changing the same files (`main.py`, the `screens/` package), and
merging them back together was genuinely painful — the history shows
several consecutive attempts to reconcile the two sides
(`pull the main`, `merge main into feat/config-parsing`, and later a
dedicated `fixed the merge problem` commit on 2026-11-02 right before
the big UI merge), plus a `clean trash files` commit afterwards to
remove leftovers from a conflict resolution.

A few honest takeaways from that:

- **Conflicts are not just a Git nuisance, they're a planning signal.**
  Every conflict we hit was really telling us the same thing: we had
  split work by *feature* (config vs. gameplay) instead of by *file
  ownership*, so the two features were bound to collide in `main.py`
  and `screens/`. We only partly fixed this mid-project by reorganizing
  the source tree (`refactor(src): reorganize directory structure and
  remove redundant folders`) to give each concern its own module.
- **A conflict resolved badly is worse than a conflict avoided.** The
  separate `clean trash files` commit exists because a merge left debris
  in the tree. We learned to treat "the merge compiles" as a weaker bar
  than "the merge is clean", and to always run the lint/test loop right
  after resolving a conflict, not just before the next feature commit.
- **Smaller, more frequent merges would have cost us less.** Both of the
  big conflict-heavy merges happened after each side had accumulated
  roughly a week of independent work. Merging every day or two, even
  with incomplete features, would have kept the diffs small enough that
  conflicts stayed trivial instead of structural.
- **Communication filled the gap tooling didn't.** When a merge touched
  logic neither of us fully remembered writing, we talked it through
  directly rather than guessing from the diff — which is also why no
  conflict resolution ever silently dropped a feature.

None of this blocked the project for more than a day at a time, but it
is the single most repeated pattern in our git history, and the clearest
lesson for next time: agree on module boundaries *before* splitting up
work, not after the first conflict.
