SHELL := /bin/bash
DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev
PROD := docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod

.PHONY: help dev prod down logs restart-agent migrate revision shell test lint typecheck format env-dev env-prod

help:
	@echo "Targets:"
	@echo "  make env-dev          copy .env.example -> .env.dev (skip if exists)"
	@echo "  make env-prod         copy .env.example -> .env.prod (skip if exists)"
	@echo "  make dev              start full dev stack (agent, postgres, redis)"
	@echo "  make prod             start prod stack detached"
	@echo "  make down             stop dev stack"
	@echo "  make logs             tail agent logs"
	@echo "  make restart-agent    restart only the agent (apply config changes)"
	@echo "  make migrate          run alembic upgrade head inside agent container"
	@echo "  make revision M='msg' generate new alembic revision"
	@echo "  make shell            open bash in agent container"
	@echo "  make test             run pytest locally"
	@echo "  make lint             run ruff"
	@echo "  make typecheck        run mypy"
	@echo "  make format           run ruff format"

env-dev:
	@test -f .env.dev || (cp .env.example .env.dev && echo "created .env.dev from .env.example")

env-prod:
	@test -f .env.prod || (cp .env.example .env.prod && echo "created .env.prod from .env.example")

dev: env-dev
	$(DEV) up --build

down:
	$(DEV) down

prod: env-prod
	$(PROD) up -d --build

logs:
	$(DEV) logs -f agent

restart-agent:
	$(DEV) restart agent

migrate:
	$(DEV) exec agent alembic upgrade head

revision:
	$(DEV) exec agent alembic revision --autogenerate -m "$(M)"

shell:
	$(DEV) exec agent bash

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy app

format:
	ruff format .
	ruff check --fix .
