# Risk Analysis

Risks identified during the project, their actual impact, and how they
were (or will be) mitigated.

| Risk | Likelihood | Impact | Mitigation | Outcome |
|------|------------|--------|------------|---------|
| Two people editing the same core files on parallel branches (`main.py`, `screens/`) | High | Medium — lost time, not lost work | Later reorganized the code into smaller, more focused modules (`screens/`, `screens/classes/`) to reduce file overlap between concerns | Happened (see [`team-organization.md`](team-organization.md)); resolved each time, never lost code |
| Hand-written JSON comment parser having edge-case bugs | Medium | Low — caught by manual testing, not a crash | Added upfront sanitization and dedicated fix commits as edge cases were found | Happened twice (index error, flake error); both fixed within a day |
| Ghost AI behavior being subjective/hard to verify as "correct" | High | Low — gameplay-only, not a crash risk | Iterative fix passes (wall collision, target calculation, scared-mode movement, random coordinate generation), each tested manually in-game | Took ~3 weeks across several commits; considered stable as of 2026-11-09 |
| Relying on an external, unmodifiable maze-generator package | Medium | Medium — a bug or crash in that package would be outside our control | Wrapped the call in `try/except`, turned any failure into a clear `RuntimeError` instead of a crash, and validated the returned maze's dimensions | No failure observed so far; mitigation is in place regardless |
| No automated test suite | High (by design, not yet done) | Medium — regressions must be caught manually | Compensated with `flake8` + `mypy --strict` as a static safety net, and manual acceptance testing per feature (see [`acceptance-tests.md`](acceptance-tests.md)) | Accepted risk for now; flagged as a remaining gap |
| Deployment/packaging to a public platform not started | Certain (not yet done) | High for the mandatory part of the subject | Explicitly deferred; will be picked up in a dedicated phase before submission | Open — tracked here so it isn't forgotten |
| Dropping `pydantic` mid-project could have broken config behavior | Low (planned refactor) | Medium if done carelessly | Rewrote validation logic incrementally, re-ran the game and the lint suite after each step | Completed cleanly over two commits on 2026-11-08 |
