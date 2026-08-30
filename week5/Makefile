.PHONY: run test format lint seed web-install web-dev web-build

HOST ?= 127.0.0.1
PORT ?= 8000

export PYTHONPATH := .

web-install:
	cd frontend && npm install

web-dev:
	cd frontend && npm run dev

web-build:
	cd frontend && npm run build

run: web-build
	uvicorn backend.app.main:app --reload --host $(HOST) --port $(PORT)

test:
	pytest -q backend/tests

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
