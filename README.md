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

On every start the stand applies migrations and seeds the test user from
`TEST_NAME` / `TEST_EMAIL` / `TEST_PASSWORD` (the same variables the tests read).

## Account API

Base path `/api/v1`. Every error has the body `{"ok": false, "message": "<text>"}`;
validation errors are `400` (not FastAPI's default `422`).

| Endpoint | Success | Errors |
|---|---|---|
| `POST /auth/register` `{name, email, password}` | `201 {id, name, email, access_token}` | `400` missing / empty / invalid field, `409` email already registered |
| `POST /auth/login` `{email, password}` | `200 {id, access_token}` | `400` missing / empty field, `401` wrong email or password |
| `GET /auth/me` (Bearer token) | `200 {id, name, email}` | `401` no token / bad or expired token |
| `DELETE /auth/me` (Bearer token) | `200 {"ok": true}` | `401` as above |

Rules: name is non-empty; email looks like `x@y.z` and is unique case-insensitively
(it is trimmed and lowercased on register and login); password has at least 6 characters.
Passwords are stored as argon2id hashes in `users.password_hash`.

## Known defects

The stand can deliberately reproduce bugs ("seeded defects") so tests can catch them.
Each defect is off by default and is switched on with `BUG_<NAME>=1` in `.env`
(registry: `app/defects.py`).

| Flag | Area | Behaviour when enabled | Expected behaviour |
|---|---|---|---|
| — | — | No seeded defects yet | — |
