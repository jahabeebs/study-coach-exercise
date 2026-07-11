# Study Coach — one command per activity. Run from assessment/.

.PHONY: setup verify-setup test evals dev-backend dev-frontend submit bundle

setup:            ## Install backend and frontend dependencies
	cd backend && uv sync
	cd frontend && npm install

verify-setup:     ## Confirm your environment is ready (run before starting the clock)
	cd backend && uv run python -c "import app.main; print('backend imports: ok')"
	cd backend && uv run pytest -q --no-header -x -k "test_health or test_sections" 2>&1 | tail -1
	cd frontend && node --version >/dev/null && echo "node: ok"
	@test -f .env && grep -q "ANTHROPIC_API_KEY=sk" .env && echo "api key: found in .env" \
		|| echo "api key: NOT set — copy .env.example to .env and add your key (needed for evals + live app, not for tests)"
	@echo "verify-setup complete"

test:             ## Run the test suite (no API key needed)
	cd backend && uv run pytest

evals:            ## Run the eval suite (needs ANTHROPIC_API_KEY; writes evals/reports/)
	cd backend && uv run python ../evals/run_evals.py

dev-backend:      ## Run the API on :8000
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:     ## Run the web app on :5173 (proxies /api to :8000)
	cd frontend && npm run dev

submit:           ## Check your work is ready and print how to submit (repo flow)
	bash submit.sh

bundle:           ## Email fallback only: package study-coach-submission.bundle
	bash submit.sh --bundle
