SHELL := /bin/bash

.PHONY: backend
backend:
	source env/secrets.sh && \
	python mediamanager

.PHONY: frontend
frontend:
	cd frontend && yarn run dev --host --port 3000

frontend-prod:
	cd frontend && yarn run build && yarn run start -p 3000
