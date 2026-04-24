# hng14-stage2-devops
# Job Processing System — DevOps Stage 2

A production-ready job processing system made up of three services containerized with Docker and deployed via a full CI/CD pipeline using GitHub Actions.

---

## Architecture

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   Frontend  │──────▶ │     API     │──────▶ │    Redis    │
│  (Node.js)  │        │  (FastAPI)  │        │   (Queue)   │
│  Port 3000  │        │  Port 8000  │        │             │
└─────────────┘        └─────────────┘        └──────┬──────┘
                                                      │
                                              ┌───────▼──────┐
                                              │    Worker    │
                                              │   (Python)   │
                                              └──────────────┘
```

- **Frontend** — Node.js/Express app where users submit and track jobs
- **API** — Python/FastAPI service that creates jobs and serves status updates
- **Worker** — Python service that picks up and processes jobs from the Redis queue
- **Redis** — Shared queue between the API and worker (not exposed to host)

---

## Prerequisites

Make sure the following are installed on your machine before starting:

| Tool | Version | Check |
|---|---|---|
| Docker | 24+ | `docker --version` |
| Docker Compose | v2+ | `docker compose version` |
| Git | any | `git --version` |

---

## Quickstart — Bring the Stack Up From Scratch

### 1. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create your environment file
```bash
cp .env.example .env
```
The default values in `.env.example` work out of the box for local development. No changes needed unless you want custom ports.

### 3. Build and start all services
```bash
docker compose up --build -d
```

### 4. Verify all services are healthy
```bash
docker compose ps
```

A successful startup looks like this:
```
NAME                STATUS
redis               running (healthy)
api                 running (healthy)
worker              running (healthy)
frontend            running (healthy)
```

All four services must show `(healthy)` — not just `running`. If any show `(starting)`, wait 30 seconds and run `docker compose ps` again.

### 5. Access the application
| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Health | http://localhost:8000/health |
| API Docs | http://localhost:8000/docs |

---

## Verify It Works

**Check the API is healthy:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

**Submit a job:**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"payload": "test-job"}'
# Expected: {"job_id": "some-uuid-here"}
```

**Check the job status** (replace `JOB_ID` with the id returned above):
```bash
curl http://localhost:8000/jobs/JOB_ID
# Expected: {"job_id": "...", "status": "completed"}
```

---

## Stopping the Stack
```bash
# Stop all services
docker compose down

# Stop and remove volumes (clears Redis data)
docker compose down -v
```

---

## Environment Variables

All configuration is driven by environment variables. See `.env.example` for the full list.

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `redis` | Redis service hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `API_PORT` | `8000` | Port to expose the API on the host |
| `FRONTEND_PORT` | `3000` | Port to expose the frontend on the host |
| `API_URL` | `http://api:8000` | URL the frontend uses to reach the API |

---

## CI/CD Pipeline

The pipeline runs automatically on every push via GitHub Actions in this order:

```
lint → test → build → security scan → integration test → deploy
```

| Stage | What it does |
|---|---|
| **lint** | flake8 (Python), eslint (JS), hadolint (Dockerfiles) |
| **test** | pytest unit tests with mocked Redis, uploads coverage artifact |
| **build** | Builds and pushes all 3 images to a local registry tagged with git SHA and latest |
| **security scan** | Trivy scans all images, fails on CRITICAL CVEs, uploads SARIF artifact |
| **integration test** | Spins up full stack, submits a real job, polls until completed |
| **deploy** | Rolling update via SSH — new container must be healthy before old is stopped |

A failure in any stage stops all subsequent stages from running.

---

## Project Structure

```
.
├── api/                        # Python/FastAPI service
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── tests/
│       └── test_api.py
├── worker/                     # Python worker service
│   ├── worker.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/                   # Node.js/Express service
│   ├── app.js
│   ├── package.json
│   ├── package-lock.json
│   ├── eslint.config.js
│   ├── Dockerfile
│   └── .dockerignore
├── .github/
│   └── workflows/
│       └── pipeline.yml        # Full CI/CD pipeline
├── docker-compose.yml
├── .env.example
├── FIXES.md
└── README.md
```
