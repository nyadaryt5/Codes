.PHONY: install test lint typecheck ci

install:
	python3 -m pip install -r requirements.lock
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -q --cov=veridian --cov=titanfuse --cov-report=term-missing --cov-fail-under=60

lint:
	python3 -m ruff check .

typecheck:
	python3 -m mypy veridian titanfuse

ci: lint typecheck test
