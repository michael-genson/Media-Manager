SHELL := /bin/bash

local-build:
	source env/secrets.sh && \
	python -m mediamanager.mediamanager.db.db_setup && \
	uvicorn mediamanager.mediamanager.app:app --reload --port 9000
