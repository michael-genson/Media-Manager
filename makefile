SHELL := /bin/bash

.PHONY: backend
backend:
	source env/secrets.sh && \
	python mediamanager

.PHONY: frontend
frontend:
	cd frontend && yarn run dev --host --port 3001

frontend-prod:
	cd frontend && yarn run build && yarn run start -p 3001

.PHONY: dev
generate:
	yarn global add json-schema-to-typescript --ignore-engines && \
	python ./dev/code-gen/generate_pydantic_exports.py && \
	python ./dev/code-gen/generate_ts_types.py
