PYTHON ?= python
PIP ?= pip
BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV_DIR := $(BACKEND_DIR)/.venv
UVICORN_APP := app.main:app
BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000

.PHONY: help
help:
	@echo "Answer Quality Evaluator – common workflows"
	@echo ""
	@echo "make setup-backend   # create venv and install backend deps"
	@echo "make run-backend     # start FastAPI backend with uvicorn"
	@echo "make run-frontend    # start Next.js frontend"
	@echo "make format          # run ruff + black on backend code"
	@echo "make lint            # run ruff lint checks"
	@echo "make test            # run backend tests (if present)"
	@echo "make eval-run        # trigger an eval run via /eval/run"
	@echo "make eval-summary    # show summary for latest eval run"

.PHONY: setup-backend
setup-backend:
	@echo ">>> Setting up backend virtualenv in $(VENV_DIR)..."
	@test -d "$(VENV_DIR)" || ($(PYTHON) -m venv "$(VENV_DIR)")
	@. "$(VENV_DIR)/bin/activate" && \
		if [ -f "$(BACKEND_DIR)/requirements.txt" ]; then \
			echo ">>> Installing backend requirements.txt..."; \
			$(PIP) install -r "$(BACKEND_DIR)/requirements.txt"; \
		else \
			echo ">>> No requirements.txt found; installing minimal dependencies..."; \
			$(PIP) install fastapi uvicorn openai pydantic numpy scikit-learn python-dotenv; \
		fi
	@echo ">>> Backend setup complete."

.PHONY: run-backend
run-backend:
	@echo ">>> Starting backend on http://$(BACKEND_HOST):$(BACKEND_PORT)..."
	@cd "$(BACKEND_DIR)" && . ".venv/bin/activate" && \
		uvicorn $(UVICORN_APP) --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

.PHONY: run-frontend
run-frontend:
	@echo ">>> Starting frontend on http://localhost:3000..."
	@cd "$(FRONTEND_DIR)" && npm install && npm run dev

.PHONY: format
format:
	@echo ">>> Formatting backend code with ruff + black (if installed)..."
	@cd "$(BACKEND_DIR)" && \
		if command -v ruff >/dev/null 2>&1; then \
			echo ">>> Running ruff format..."; \
			ruff format .; \
		else \
			echo "!!! ruff not found; install with 'pip install ruff'"; \
		fi && \
		if command -v black >/dev/null 2>&1; then \
			echo ">>> Running black..."; \
			black .; \
		else \
			echo "!!! black not found; install with 'pip install black'"; \
		fi

.PHONY: lint
lint:
	@echo ">>> Running ruff lint on backend..."
	@cd "$(BACKEND_DIR)" && \
		if command -v ruff >/dev/null 2>&1; then \
			ruff check .; \
		else \
			echo "!!! ruff not found; install with 'pip install ruff'"; \
			exit 1; \
		fi

.PHONY: test
test:
	@echo ">>> Running backend tests (pytest if available)..."
	@cd "$(BACKEND_DIR)" && \
		if command -v pytest >/dev/null 2>&1; then \
			pytest; \
		else \
			echo "!!! pytest not found; install with 'pip install pytest'"; \
			exit 1; \
		fi

.PHONY: eval-run
eval-run:
	@echo ">>> Triggering eval run via /eval/run..."
	@LIMIT=$${LIMIT:-10}; \
	echo ">>> Using LIMIT=$$LIMIT"; \
	RESP=$$(curl -s -X POST "http://$(BACKEND_HOST):$(BACKEND_PORT)/eval/run" \
		-H "Content-Type: application/json" \
		-d "$$('{ printf "{ \"pipelines\": [\"A\",\"B\",\"C\"], \"limit\": %s, \"use_llm_judge\": false }" "$$LIMIT"; }")"); \
	echo "$$RESP" | jq . >/dev/null 2>&1 || { echo "$$RESP"; echo "!!! Eval run failed (JSON parse error)."; exit 1; }; \
	RUN_ID=$$(echo "$$RESP" | jq -r '.run_id'); \
	echo ">>> Eval run started. run_id=$$RUN_ID"

.PHONY: eval-summary
eval-summary:
	@echo ">>> Fetching summary for latest eval run..."
	@RUN_ID=$${RUN_ID:-$$("$(PYTHON)" scripts/latest_run.py)}; \
	if [ -z "$$RUN_ID" ]; then \
		echo "!!! No latest run_id found. Set RUN_ID=... or run 'make eval-run' first."; \
		exit 1; \
	fi; \
	echo ">>> Using run_id=$$RUN_ID"; \
	curl -s "http://$(BACKEND_HOST):$(BACKEND_PORT)/eval/summary?run_id=$$RUN_ID" | jq . || \
		{ echo "!!! Failed to fetch eval summary for run_id=$$RUN_ID"; exit 1; }

