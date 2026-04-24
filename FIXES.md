# FIXES.md — Bug Report

Every bug found in the starter repository, listed with file, line number, problem description, and fix applied.

---

## api/main.py

### FIX-001
- **File:** `api/main.py`
- **Line:** 1
- **Problem:** Trailing comma in import statement with no following item — `from fastapi import FastAPI,` — causes a `SyntaxError: invalid syntax` and prevents the entire module from loading.
- **Fix:** Completed the import to include all required names: `from fastapi import FastAPI, HTTPException, JSONResponse`

---

### FIX-002
- **File:** `api/main.py`
- **Line:** 5
- **Problem:** `import HTTPException` — `HTTPException` is not a standalone package. It is part of `fastapi` and cannot be imported this way. Causes `ModuleNotFoundError` at startup.
- **Fix:** Removed the standalone import. `HTTPException` is now imported directly from `fastapi` on line 1.

---

### FIX-003
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** `os.getenv("REDIS_HOST", "rediis")` — the default value has a typo (`rediis` instead of `redis`). When `REDIS_HOST` is not set, the client connects to a non-existent host and fails silently.
- **Fix:** Corrected the default value to `"redis"`: `os.getenv("REDIS_HOST", "redis")`

---

### FIX-004
- **File:** `api/main.py`
- **Line:** 9 vs 25
- **Problem:** Redis client defined as `r` on line 9 but referenced as `redis_client` in the health check on line 25. Causes `NameError: name 'redis_client' is not defined` whenever `/health` is called.
- **Fix:** Used `r` consistently throughout the entire file including the health check: `r.ping()`

---

### FIX-005
- **File:** `api/main.py`
- **Line:** 14
- **Problem:** `r.lpush("job", job_id)` — queue name is `"job"` (singular). The worker listens on `"jobs"` (plural). Jobs are pushed to a queue no one reads.
- **Fix:** Changed to `r.lpush("jobs", job_id)` to match the worker.

---

### FIX-006
- **File:** `api/main.py`
- **Line:** 20
- **Problem:** `raise HTTPException{status_code=404, detail="Job not found"}` — curly braces used instead of parentheses. This is a `SyntaxError` that prevents the module from loading.
- **Fix:** Changed to `raise HTTPException(status_code=404, detail="Job not found")`

---

### FIX-007
- **File:** `api/main.py`
- **Line:** 28-29
- **Problem:** Missing closing parenthesis on `JSONResponse(...)` call. Causes `SyntaxError` at parse time.
- **Fix:** Added the closing parenthesis: `content={"status": "redis unavailable"})`

---

## worker/worker.py

### FIX-008
- **File:** `worker/worker.py`
- **Line:** 13
- **Problem:** `r.brpop("job", timeout=5)` — queue name is `"job"` (singular). The API pushes to `"jobs"` (plural). The worker polls forever but never finds any jobs.
- **Fix:** Changed to `r.brpop("jobs", timeout=5)` to match the API.

---

### FIX-009
- **File:** `worker/worker.py`
- **Line:** 28
- **Problem:** `f.write("ok")` is not indented inside the `with` block. Causes `IndentationError: expected an indented block after 'with' statement` which prevents the worker from starting.
- **Fix:** Indented `f.write("ok")` with 4 spaces to be inside the `with` block.

---

### FIX-010
- **File:** `worker/worker.py`
- **Line:** 30-33
- **Problem:** `handle_shutdown` function and `signal.signal()` registrations are defined **after** the `while True:` loop. Since the loop runs forever, these lines are never reached and the worker cannot be gracefully shut down.
- **Fix:** Moved the `handle_shutdown` function definition and both `signal.signal()` calls to before the `while True:` loop.

---

## frontend/app.js

### FIX-011
- **File:** `frontend/app.js`
- **Line:** 5
- **Problem:** `const API_URL = "http://localhost:8000"` — hardcoded to localhost. Inside Docker, services communicate by service name not localhost. The frontend cannot reach the API when running in a container.
- **Fix:** Changed to read from environment variable: `const API_URL = process.env.API_URL || "http://api:8000"`

---

### FIX-012
- **File:** `frontend/app.js`
- **Line:** 10
- **Problem:** `axios.post(`${API_URL}/jobs`)` — no request body forwarded. The API receives an empty payload on every job submission.
- **Fix:** Changed to `axios.post(`${API_URL}/jobs`, req.body)` to forward the request body.

---

### FIX-013
- **File:** `frontend/app.js`
- **Line:** 24
- **Problem:** `app.listen(3000)` — binds only to `127.0.0.1` by default in Node.js. Inside a Docker container this makes the service unreachable from outside the container.
- **Fix:** Changed to `app.listen(3000, "0.0.0.0")` to bind on all interfaces.

---

### FIX-014
- **File:** `frontend/app.js`
- **Problem:** No `/health` endpoint defined. The Dockerfile `HEALTHCHECK` and `docker-compose.yml` healthcheck both call `GET /health` — without it Docker marks the container as unhealthy and dependent services never start.
- **Fix:** Added a `/health` endpoint that returns `{"status": "ok"}` with HTTP 200.

---

## frontend/.eslintrc.json

### FIX-015
- **File:** `frontend/.eslintrc.json`
- **Problem:** ESLint v9+ no longer supports `.eslintrc.*` config files. The pipeline uses ESLint 10 which requires the new flat config format. Running the linter produces `ESLint couldn't find an eslint.config.(js|mjs|cjs) file`.
- **Fix:** Deleted `.eslintrc.json` and created `frontend/eslint.config.js` using the new flat config format. Added `@eslint/js` as a dev dependency.

---

## frontend/ (missing file)

### FIX-016
- **File:** `frontend/package-lock.json`
- **Problem:** `package-lock.json` was not committed to the repository. The pipeline uses `npm ci` which requires a lock file to guarantee reproducible installs. Without it the pipeline fails with `npm error code EUSAGE`.
- **Fix:** Ran `npm install` locally to generate `package-lock.json` and committed it.

---

## Dockerfile (all services)

### FIX-017
- **File:** `api/Dockerfile`, `worker/Dockerfile`, `frontend/Dockerfile`
- **Problem:** Dockerfiles were named `dockerfile` (lowercase). GitHub Actions runs on Ubuntu Linux which is case-sensitive. Hadolint and Docker could not find the files, producing `does not exist (No such file or directory)`.
- **Fix:** Renamed all three files to `Dockerfile` (capital D) using `git mv`.

---

## api/tests/test_api.py

### FIX-018
- **File:** `api/tests/test_api.py`
- **Line:** 14
- **Problem:** `from main import app, redis_client` — `redis_client` does not exist in `main.py` (the variable is named `r`). Causes `F401 imported but unused` flake8 error and would cause an `ImportError` at test runtime.
- **Fix:** Changed to `from main import app` and updated all test patches to use `patch("main.r", ...)`.

---

## Summary Table

| Fix ID | File | Type | Impact |
|---|---|---|---|
| FIX-001 | api/main.py | SyntaxError | App won't start |
| FIX-002 | api/main.py | ImportError | App won't start |
| FIX-003 | api/main.py | Typo | Redis unreachable |
| FIX-004 | api/main.py | NameError | Health check crashes |
| FIX-005 | api/main.py | Queue mismatch | Jobs never processed |
| FIX-006 | api/main.py | SyntaxError | App won't start |
| FIX-007 | api/main.py | SyntaxError | App won't start |
| FIX-008 | worker/worker.py | Queue mismatch | Worker never picks up jobs |
| FIX-009 | worker/worker.py | IndentationError | Worker won't start |
| FIX-010 | worker/worker.py | Logic error | Graceful shutdown broken |
| FIX-011 | frontend/app.js | Hardcoded URL | Frontend can't reach API in Docker |
| FIX-012 | frontend/app.js | Missing body | Jobs submitted with no payload |
| FIX-013 | frontend/app.js | Binding error | Frontend unreachable in Docker |
| FIX-014 | frontend/app.js | Missing endpoint | Container always unhealthy |
| FIX-015 | frontend/.eslintrc.json | Config format | ESLint fails in pipeline |
| FIX-016 | frontend/package-lock.json | Missing file | npm ci fails in pipeline |
| FIX-017 | All Dockerfiles | Case sensitivity | Hadolint can't find Dockerfiles |
| FIX-018 | api/tests/test_api.py | Bad import | Flake8 error + test ImportError |

