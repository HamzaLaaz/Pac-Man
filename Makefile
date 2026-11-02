CONFIG ?= src/config.json

.PHONY: install run debug clean fclean lint lint-strict

install:
	uv sync

run:
	uv run python3 src/main.py $(CONFIG)

debug:
	uv run python3 -m pdb src/main.py  $(CONFIG)

clean:
	@rm -rf */__pycache__ */*/__pycache__ */*/*/__pycache__ __pycache__
	@rm -rf .mypy_cache */.mypy_cache .pytest_cache

fclean: clean
	@rm -rf .venv

lint:
	uv run flake8 . --exclude .venv
	uv run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 . --exclude .venv
	uv run mypy . --strict
