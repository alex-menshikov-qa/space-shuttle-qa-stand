# space-shuttle-qa-stand

Portfolio test stand (not production) for API and UI test automation. Work in progress — see `PLAN.md`.

## Quick start

```bash
cp .env.example .env
docker compose up -d --build --wait
curl http://localhost:8000/health   # {"status":"ok"}
```

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Stop and wipe the database: `docker compose down -v`

## Known defects

The stand can deliberately reproduce bugs ("seeded defects") so tests can catch them.
Each defect is off by default and is switched on with `BUG_<NAME>=1` in `.env`
(registry: `app/defects.py`).

| Flag | Area | Behaviour when enabled | Expected behaviour |
|---|---|---|---|
| — | — | No seeded defects yet | — |
