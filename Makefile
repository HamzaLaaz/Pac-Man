run:
	uv run src/main.py

clean:
	@rm -rf */__pycache__ */.mypy_cache .mypy_cache __pycache__ */*/__pycache__
	@rm -rf .venv