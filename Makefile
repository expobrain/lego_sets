mypy:
	poetry run mypy .

test:
	poetry run pytest -x --cov=core --cov=lego_sets --cov-fail-under=90

install:
	poetry install --sync
