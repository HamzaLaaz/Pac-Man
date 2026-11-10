CONFIG ?= config.json

.PHONY: install run debug clean fclean lint lint-strict

install:
	uv sync

run:
	uv run python3 pac-man.py $(CONFIG)

debug:
	uv run python3 -m pdb pac-man.py $(CONFIG)

build:
	@uv run python3 -m nuitka pac-man.py --onefile --include-package=mlx --include-data-dir=assets=assets --include-data-files=config.json=config.json 2>/dev/null && \
	mkdir -p pacman-1337 && \
	mv pac-man.bin pacman-1337 && \
	cp -r assets pacman-1337 && \
	cp config.json pacman-1337 && \
	zip -r pacman-1337.zip pacman-1337 2>/dev/null && \
	rm -rf pac-man.dist pac-man.onefile-build pac-man.build && \
	clear && \
	echo "packaging the codebase is done"

clean:
	@rm -rf */__pycache__ */*/__pycache__ */*/*/__pycache__ __pycache__
	@rm -rf .mypy_cache */.mypy_cache .pytest_cache

fclean: clean
	@rm -rf .venv

lint:
	@uv run flake8 . --exclude .venv
	@uv run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@uv run flake8 . --exclude .venv
	@uv run mypy . --strict
