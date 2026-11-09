# Packaging & Deployment Guide

**Status: planning only — nothing in this guide has been executed yet.**
This documents exactly how to take the Pac-Man game from "runs via
`uv run`" to a packaged, deployed build on a public gaming platform, per
Chapter IV and Chapter VII of the subject. It is written so either of us
can follow it step by step when we pick this up; see
[`kanban.md`](kanban.md) for its current status.

## 0. Why this is still open

The rest of the subject's mandatory part is done (see
[`timeline.md`](timeline.md) / [`kanban.md`](kanban.md)). Packaging was
deliberately left for last, since it depends on nothing else changing —
it only needs the game to already work, which it does.

## 1. Platform constraint — read this first

The `mlx` dependency is **not** a pure-Python package despite its
`py3-none-any` wheel tag: it bundles a compiled `libmlx.so`. Inspecting
it (`file` / `ldd`) shows:

```
libmlx.so: ELF 64-bit LSB shared object, x86-64, dynamically linked
  depends on: libxcb, libxcb-keysyms, libvulkan, libXau, libXdmcp, libc, libm, ...
```

This means:

- The game can only be packaged for **Linux x86-64** as it stands.
  There is no macOS or Windows build of `libmlx.so` available to us.
- Players need a working **X11/XCB** display and a **Vulkan** driver.
  This is normal on most desktop Linux distros but not guaranteed on a
  bare server or minimal container — worth a line on the store page.
- If a macOS/Windows build is ever wanted, that requires the `mlx`
  package's maintainers to ship a build for that platform — it is not
  something we can produce ourselves from this repository.

**Decision: ship Linux-only**, and say so explicitly on the itch.io page.

## 2. Platform choice: itch.io over Steam

| | itch.io | Steam |
|---|---|---|
| Cost | Free | $100 one-time Steamworks fee |
| Approval | None, instant | Review process |
| Unlisted/private option | Yes — "Draft" or "Restricted" visibility | Yes, but heavier (Steam app review, store page requirements) |
| Upload tooling | `butler` (simple CLI) | SteamPipe / `steamcmd` (more setup) |

Given the subject only asks for "a free but unlisted/private build... for
demonstration," itch.io's Draft/Restricted mode is a direct match with
far less overhead. **Decision: itch.io.**

## 3. Before freezing anything: audit path handling

Every asset load in the codebase looks like this (from
`src/screens/game_screen.py`, `main_menu.py`, etc.):

```python
self.mlx.mlx_png_file_to_image(self.mlx_ptr, "assets/pacman-art/other/heart.png")
```

These are **relative to the process's current working directory**, not
to the script's location. This works today because we always run from
the repository root (`make run` / `python3 pac-man.py ...`). A frozen,
double-clickable build must preserve that: the launcher must `cd` into
the build's own directory before starting the executable, or the game
will fail to find its assets the moment it's launched from anywhere
else (e.g. a Desktop icon or itch.io's own launcher app, depending on
its working directory).

**Action when we get here:** verify itch.io's app launcher sets CWD to
the build folder (it does, by default, for a simple executable+folder
app — confirm once a test build exists). If not, the launcher script
from step 7 below handles it with an explicit `cd`.

## 4. Install the packaging tool

[PyInstaller](https://pyinstaller.org/) is the standard choice for
freezing a CPython application that also loads a native shared library
via `ctypes` (which is how `mlx` works) — it bundles the interpreter,
the stdlib, third-party packages, and arbitrary binary/data files into
one self-contained folder.

```sh
uv add --group dev pyinstaller
```

(as a dev-only dependency group, the same way `flake8`/`mypy` are
already declared in `pyproject.toml` — it should never be required to
just run the game from source)

## 5. Write the PyInstaller spec

A `.spec` file (not just CLI flags) is worth it here because we need to
explicitly list:

- the entry point: `pac-man.py`
- the native binary: `mlx/libmlx.so` (PyInstaller's import analysis
  cannot discover a `ctypes`-loaded `.so` on its own — it has to be
  listed under `binaries`)
- data directories: `assets/` (all of it) and a default
  `src/config.json`, plus `assets/10x20.bdf`
- `mazegenerator` and `bdfparser`, which are plain Python and should be
  auto-discovered, but are worth listing explicitly under `hiddenimports`
  since they're installed from local wheels rather than PyPI, which
  PyInstaller's static analysis sometimes misses

Sketch (to be created as `pacman.spec` at the repo root once we build
this for real):

```python
# pacman.spec
a = Analysis(
    ['pac-man.py'],
    pathex=['src'],
    binaries=[('mlx/libmlx.so' if False else '.venv/lib/python3.14/site-packages/mlx/libmlx.so', 'mlx')],
    datas=[
        ('assets', 'assets'),
        ('src/config.json', 'src'),
    ],
    hiddenimports=['mazegenerator', 'bdfparser'],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, name='pacman-bin', console=False)
coll = COLLECT(exe, a.binaries, a.datas, name='pacman')
```

(the `binaries` source path needs to point at wherever `uv sync` puts
the installed `mlx` package inside `.venv` — pin it down exactly when
writing this for real, since `uv`'s venv layout is deterministic but
worth double-checking against the Python version in use)

## 6. Build as one-dir, not one-file

```sh
uv run pyinstaller pacman.spec
```

`--onedir` (the default for a `COLLECT` target, as above) keeps
`libmlx.so` and `assets/` as real files on disk next to the executable.
`--onefile` would unpack everything into a temp directory at every
startup, which is slower and — more importantly — means the game would
no longer be looking for `assets/...` relative to a stable, predictable
directory, breaking the path assumption from step 3. **Always build
one-dir for this project.**

Expected output: `dist/pacman/` containing `pacman-bin`, `libmlx.so`,
`assets/`, `config.json`, and PyInstaller's bundled interpreter/stdlib.

## 7. Add a launcher + default config

Two small additions go inside `dist/pacman/` (automated by the
packaging script in step 9, not created by hand each time):

- **`config.json`** — a copy of `src/config.json`, shipped as the
  default so players don't need to supply one.
- **`run.sh`**:
  ```sh
  #!/bin/sh
  cd "$(dirname "$0")"
  ./pacman-bin config.json
  ```
  This satisfies two things at once: it guarantees the working directory
  is the build folder (step 3) and it supplies the one mandatory CLI
  argument the subject requires (`python3 pac-man.py config.json`'s
  packaged equivalent), so the player just runs `run.sh` (or
  double-clicks it, with the executable bit set) instead of typing a
  command.

## 8. Smoke-test in isolation

Before trusting the build, run it somewhere **without** `uv`, the dev
`.venv`, or this repository's source checkout — e.g. a disposable
container built from a minimal Linux base image, with only `dist/pacman/`
copied in. This is the only way to be sure nothing is silently working
because of leftover state in the dev environment (an unset `LD_LIBRARY_PATH`
dependency, a stray `PYTHONPATH`, etc.).

Checklist for that test:

- [ ] `./run.sh` launches the window without errors
- [ ] All assets load (title screen, ghosts, pacgums, fonts) — no
      missing-image/black-box glitches
- [ ] Highscores read/write correctly (the default `highscores.json`
      should either not exist yet, or be shipped empty)
- [ ] Cheat mode still works (quick way to exercise every game state
      without playing a full level)
- [ ] Closing the window and re-launching works cleanly

## 9. Write the packaging script

This is the artifact the subject explicitly requires at the repo root
("Your Git repository must contain the full source and the packaging
script/spec at the root"). Plan: a `package.sh` (or a `make package`
target calling it) that runs steps 5–7 end to end:

```sh
#!/bin/sh
set -e
uv run pyinstaller pacman.spec --clean --noconfirm
cp src/config.json dist/pacman/config.json
cp project-management/packaging-guide.md dist/pacman/README.txt  # or a trimmed version
printf '#!/bin/sh\ncd "$(dirname "$0")"\n./pacman-bin config.json\n' > dist/pacman/run.sh
chmod +x dist/pacman/run.sh
cd dist && zip -r pacman-linux-x86_64.zip pacman
```

Running this one script from a clean checkout should always reproduce
`dist/pacman-linux-x86_64.zip` — that's what "you may be asked to
regenerate the package during peer review" is testing for, so it needs
to work without any manual steps beyond running it.

## 10. Create the itch.io project

1. Create (or use an existing) itch.io account.
2. **New Project** → Classification: *Game* → Kind of project:
   *Executable* (not HTML, since this needs native Linux libraries).
3. Upload `pacman-linux-x86_64.zip`; tick **"This file will be played
   on"** → Linux, and check the "soft launch"/executable checkbox so
   itch.io's app offers to run it directly.
4. Set **Visibility & access** to **Draft** while testing, then to
   **Restricted** (shareable via a secret link, not publicly listed)
   for the actual submission — this is the "free but unlisted/private
   build" the subject asks for. Public is not required and shouldn't be
   used unless we actively want it discoverable.
5. Fill in a short description + the controls (see step 12).

## 11. Install and use `butler` for repeatable pushes

`butler` is itch.io's official upload CLI — once set up, re-publishing
after a rebuild is a single command instead of a manual web upload.

```sh
# one-time setup
curl -L -o butler.zip https://broth.itch.ovh/butler/linux-amd64/LATEST/archive/default
unzip butler.zip -d butler && export PATH="$PWD/butler:$PATH"
butler login

# every time there's a new build (after running the packaging script)
butler push dist/pacman <itch-username>/pacman:linux-x86_64
```

`butler` diffs against the last pushed build, so iterating is cheap.
This is also the natural place to wire packaging into CI later, if we
ever want it automatic — not needed for the subject, just worth noting.

## 12. In-package / store-page instructions

Chapter VII asks for "minimal in-package instructions (controls,
options, configuration)". Keep it short — this is a demo build, not a
manual:

```
Pac-Man — controls
  Arrows / WASD : move
  P or ESC      : pause
  C (in game)   : toggle cheat mode
    N invincibility-skip level   I invincible   F freeze ghosts
    L extra life   O speed boost   T reset timer

Run: ./run.sh
Config: edit config.json next to the executable before launching.
```

Put this as `README.txt` inside the zip (step 9 already copies a file
there) and reuse the same text for the itch.io page description field.

## 13. Closing the loop

Once a build is actually live:

- Flip the matching line in [`kanban.md`](kanban.md) from **To Do** to
  **Done**, and add the itch.io link there.
- Update the root [`README.md`](../README.md)'s description to mention
  where the build can be played, and remove the "deployment pending"
  framing.
- Re-run `make lint` / `make lint-strict` — `pacman.spec` and
  `package.sh` are new files in the repo and should stay clean too.

## Open questions to settle before actually running this

- Exact `uv`/`.venv` path for `libmlx.so` to hardcode into
  `pacman.spec` — depends on which Python version `uv sync` resolves to
  on the build machine.
- Whether `assets/` licensing allows redistribution in a public (even
  unlisted) build — worth a quick check before the first real push.
- Whether the target Linux build machine's glibc is old/new enough to
  be broadly compatible, or whether we should build on the oldest
  reasonable baseline (common PyInstaller portability concern for
  native `.so` dependencies).
