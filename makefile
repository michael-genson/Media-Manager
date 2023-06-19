SHELL := /bin/bash

local-build:
	source env/secrets.sh && \
	uvicorn mediamanager.mediamanager.app:app --reload --port 9000
