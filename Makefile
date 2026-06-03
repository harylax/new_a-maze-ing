.PHONY: install run debug clean fclean lint lint-strict

.venv/.installed: pyproject.toml
	POETRY_VIRTUALENVS_IN_PROJECT=true poetry install
	touch .venv/.installed

install: .venv/.installed

run:
	poetry run python a_maze_ing.py config.txt

debug:
	poetry run python -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

fclean: clean
	rm -rf .venv
	rm poetry.lock

lint:
	poetry run flake8 . --exclude .venv
	poetry run mypy --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs \
		--exclude .venv .

lint-strict:
	poetry run flake8 . --exclude .venv
	poetry run mypy --strict . --exclude .venv