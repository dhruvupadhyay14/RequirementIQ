# Development Guide

Prereqs:
- Docker & Docker Compose
- Node 18+, npm
- Python 3.12

Run everything locally (dev mode):

1. Copy `.env.example` to `.env` and fill values.
2. Start services:

```bash
docker compose up --build
```

Frontend:
- URL: http://localhost:5173
Backend:
- URL: http://localhost:8000 (health at `/health`)
