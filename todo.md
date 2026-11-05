# TODO – Pac-Man Project Improvements

## 1. Ghost Movement and Speed
- [ ] Fix ghost movement speed to ensure consistent and smooth movement.
- [ ] Make sure all ghosts move at the intended speed.
- [ ] Ensure ghost speed does not change unexpectedly between levels.
- [ ] Verify that ghosts continue moving correctly when changing direction.
- [ ] Test ghost movement in normal and scared modes.

## 2. Cheat Mode
- [ ] Fix cheat mode keyboard bindings.
- [ ] Ensure each cheat action is triggered by the correct key.
- [ ] Prevent cheat keys from interfering with normal player controls.
- [ ] Handle key presses consistently and avoid accidental repeated activation.
- [ ] Test all cheat mode features.

## 3. Mypy – Type Checking
- [ ] Fix all mypy errors across the project.
- [ ] Add or correct missing type annotations.
- [ ] Fix incorrect return types and argument types.
- [ ] Ensure imports and type references are correctly handled.
- [ ] Verify that mypy runs successfully on the entire project.

## 4. Flake8 – Code Quality
- [ ] Fix all flake8 warnings and errors.
- [ ] Remove unused imports and variables.
- [ ] Fix line length and formatting issues.
- [ ] Improve code organization where necessary.
- [ ] Verify that flake8 passes across the entire project.

## 5. Circular Imports
- [ ] Investigate the circular import between `GhostAI` and `GameScreen`.
- [ ] Refactor imports if necessary to remove circular dependencies.
- [ ] Use type-only imports or `TYPE_CHECKING` where appropriate.
- [ ] Ensure the solution works with both mypy and flake8.
- [ ] Verify that the project starts without import errors.

## 6. Makefile
- [ ] Review and improve the existing Makefile.
- [ ] Add or fix the `run` command.
- [ ] Add a command to run mypy.
- [ ] Add a command to run flake8.
- [ ] Add a command to run tests.
- [ ] Add a `check` command to run all code-quality checks.
- [ ] Add a `clean` command to remove generated files and caches.
- [ ] Ensure all commands work correctly in the project environment.

## Final Verification
- [ ] Run the game and test all ghost behaviors.
- [ ] Test all cheat mode controls.
- [ ] Run mypy with no errors.
- [ ] Run flake8 with no errors.
- [ ] Run all available tests.
- [ ] Verify that the Makefile commands work correctly.
- [ ] Ensure the project starts and runs without errors.
