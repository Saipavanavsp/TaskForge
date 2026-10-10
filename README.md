# TaskForge — Enterprise-Grade Collaborative Task Platform

TaskForge is a production-grade full-stack collaborative task management platform engineered across all **7 fundamental layers of modern web engineering**.

```
                               ┌────────────────────────────────────────┐
                               │            Client Browser              │
                               │  Next.js 15 (React 19) + Tailwind CSS  │
                               └───────────────────┬────────────────────┘
                                                   │ HTTPS / WebSockets
                                                   ▼
                               ┌────────────────────────────────────────┐
                               │           Traefik Reverse Proxy        │
                               │        SSL Termination & Rate Limit    │
                               └───────────────────┬────────────────────┘
                                                   │
                        ┌──────────────────────────┴──────────────────────────┐
                        ▼                                                     ▼
           ┌─────────────────────────┐                           ┌─────────────────────────┐
           │   FastAPI Gateway / REST│                           │   Node.js Socket Server │
           │   Python 3.12           │                           │   Real-time Engine      │
           └────────────┬────────────┘                           └────────────┬────────────┘
                        │                                                     │
       ┌────────────────┼────────────────────────┬────────────────────────────┤
       ▼                ▼                        ▼                            ▼
┌──────────────┐ ┌──────────────┐       ┌────────────────┐          ┌───────────────────┐
│ PostgreSQL 16│ │ Redis 7      │       │ MinIO / S3     │          │ OpenTelemetry     │
│ Primary DB   │ │ Cache/PubSub │       │ Object Storage │          │ Prometheus/Grafana│
└──────────────┘ └──────────────┘       └────────────────┘          └───────────────────┘
```

---

## The 7 Layers of Architecture

### Layer 1: Database & Relational Modeling
- **Primary Store:** PostgreSQL 16 with UUID primary keys (`uuid-ossp`).
- **ORM:** SQLAlchemy 2.0 with async engine (`asyncpg`) and resilient SQLite fallback for zero-dependency local runs.
- **Migrations:** Alembic revisioned migrations (`backend/alembic/versions/0001_initial_schema.py`).
- **Caching & PubSub:** Redis 7 broker supporting distributed event channels and in-memory fallback.
- **Performance:** B-tree indexes on `(project_id)`, `(status)`, `(assignee_id)`, and unique index on `(email)`.

### Layer 2: Auth & Security
- **Password Encryption:** Argon2id hashing via `passlib[argon2]`.
- **Token Rotation:** Dual JWT pipeline:
  - Short-lived Access Token (15-min expiration) delivered in `Authorization: Bearer <token>`.
  - Long-lived Refresh Token (7-day expiration) stored in an `HttpOnly`, `SameSite=Lax/Strict` cookie.
  - Automatic rotation upon `/api/v1/auth/refresh`.
- **Role-Based Access Control (RBAC):** `verify_jwt_and_role(["admin", "manager"])` middleware enforcing role permissions across Admin, Manager, and Member tiers.
- **Security Headers:** Enforced via `SecurityHeadersMiddleware` (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).

### Layer 3: Backend Services & API Design
- **REST Gateway:** Built with Python 3.12 & FastAPI, asynchronously querying the database with Pydantic v2 validation.
- **Real-Time Engine:** Node.js Socket.io server (port 4001) connected to Redis Pub/Sub, with parallel FastAPI WebSocket endpoints (`/ws/projects/{id}`).
- **REST Endpoints:**
  - `POST /api/v1/auth/register` — Create user
  - `POST /api/v1/auth/login` — Sign in and set HttpOnly refresh cookie
  - `POST /api/v1/auth/refresh` — Rotate tokens
  - `GET /api/v1/auth/me` — Authenticated profile
  - `GET /api/v1/projects` — List projects with task aggregates
  - `POST /api/v1/projects` — Create project (Admin/Manager)
  - `GET /api/v1/projects/{id}/tasks` — Filtered & paginated tasks
  - `POST /api/v1/tasks` — Create task (Admin/Manager)
  - `PATCH /api/v1/tasks/{id}` — Status & priority transition with real-time broadcast
  - `DELETE /api/v1/tasks/{id}` — Delete task (Admin/Manager)

### Layer 4: Frontend Development
- **Framework:** Next.js 15 (App Router) + React 19 + TypeScript + Tailwind CSS.
- **Optimistic UI:** TanStack Query (React Query v5) mutation with immediate cache updates and automatic rollback upon error.
- **Kanban Board:** 4-column dynamic board (`To Do`, `In Progress`, `In Review`, `Completed`) with dropdown status transitions, priority pills, and live task editing modals.
- **Real-Time Synchronization:** Listens to socket events and automatically synchronizes board state across concurrent users.
- **RBAC UI Adaptation:** Buttons, modals, and management options adapt dynamically based on the current user's role.

### Layer 5: Testing Strategy
- **Unit & Integration:** Pytest test suite covering registration, password verification, cookie issuance, token rotation, project creation, RBAC restrictions, task mutations, and health probes (13/13 passing tests).
- **End-to-End (E2E):** Automated Playwright test (`frontend/tests/kanban.spec.ts`) validating login, navigation to `/dashboard`, task status mutation via dropdown, and UI state persistence.

### Layer 6: Deployment & Infrastructure
- **Containerization:** Multi-stage Dockerfiles (`Dockerfile.backend`, `Dockerfile.frontend`, `Dockerfile.realtime`).
- **Orchestration:** `docker-compose.yml` linking Traefik v3, PostgreSQL 16, Redis 7, MinIO, FastAPI, Node.js Socket, Next.js 15, Prometheus, and Grafana.
- **Reverse Proxy:** Traefik with rate-limiting middleware (`100 req/min`, `50 burst`) and dynamic routing.
- **CI/CD Pipeline:** GitHub Actions workflow (`.github/workflows/deploy.yml`) running PostgreSQL service tests on Python 3.12 and pushing backend containers to GitHub Container Registry (`ghcr.io`).

### Layer 7: Observability & Monitoring
- **Distributed Tracing:** OpenTelemetry FastAPI instrumentation.
- **Metrics Scraping:** Prometheus metrics exposed at `/metrics` tracking `http_requests_total`, request duration histograms, and active connections.
- **Health Probes:**
  - `/api/v1/healthz/liveness` — Process heartbeat.
  - `/api/v1/healthz/readiness` — Deep probe testing PostgreSQL connectivity and Redis ping.
- **Structured Logging:** JSON log formatting with timestamps, levels, and trace correlation IDs.

---

## Quick Start & Running Locally

### Option A: Local Development (Fast Start)

#### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows (or source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)

#### 2. Real-time Socket Server (Node.js)
```bash
cd realtime
npm install
npm start
```
Socket server runs on port 4001.

#### 3. Frontend (Next.js 15)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
Client application will be live at: [http://localhost:3000](http://localhost:3000)

---

### Option B: Full Docker Compose Infrastructure

```bash
docker compose up --build
```
- Traefik Entrypoint: `http://localhost`
- Web Dashboard: `http://localhost:3000`
- API Docs: `http://localhost/api/v1/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (login: `admin` / `admin`)
- MinIO Console: `http://localhost:9001` (login: `minioadmin` / `minioadmin`)

---

## Demo Credentials (Pre-Seeded)

| Email | Password | Role | Description |
|---|---|---|---|
| `dev@taskforge.dev` | `SecurePassword123!` | **Admin** | Full system access & project creation |
| `manager@taskforge.dev` | `SecurePassword123!` | **Manager** | Task management & sprint oversight |
| `member@taskforge.dev` | `SecurePassword123!` | **Member** | Task execution & status updates |

---

## Running the Automated Test Suite

### Backend Pytest Suite
```bash
pytest backend/tests -v
```

### Playwright E2E Suite
```bash
cd frontend
npx playwright test
```
