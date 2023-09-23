.PHONY: start
start:
	uvicorn api.main:app --reload --port 9001

.PHONY: format
format:
	black .
	isort .