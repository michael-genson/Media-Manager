SHELL := /bin/bash

.PHONY: setup
setup:
	poetry install && \
	cd frontend && \
	yarn install && \
	cd ..

.PHONY: backend
backend:
	source env/secrets.sh && \
	export DEBUG=true && \
	python mediamanager

.PHONY: frontend
frontend:
	cd frontend && yarn run dev --host --port 3000

frontend-prod:
	cd frontend && yarn run build && yarn run start -p 3000

.PHONY: dev
generate:
	yarn global add json-schema-to-typescript --ignore-engines && \
	python ./dev/code-gen/generate_pydantic_exports.py && \
	python ./dev/code-gen/generate_ts_types.py
