.PHONY: install dev test lint run check

install:
	python -m pip install -r requirements.txt

dev:
	python -m pip install -r requirements-dev.txt

test:
	python -m pytest -q

lint:
	ruff check src tests app.py

run:
	streamlit run app.py

check: lint test
