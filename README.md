# space-shuttle-qa-stand

[![CI](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml)

**A portfolio test stand, not a production service.** It is a small web app with a JSON API,
built to be tested: the API and UI automation suites (pytest + Requests / Selenium / Allure)
run against it instead of third-party training stands. It has stable locators, a documented
contract, a seeded test user and switchable "known defects" for the tests to catch.

The stand is story-agnostic for now (accounts only). Story features — a builder, a booking
section and a pilots/flights API — come later; see `PLAN.md`.

**Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, PostgreSQL 16, argon2,
JWT, server-rendered Jinja2 + vanilla JS, Docker Compose, GitHub Actions.

## Quick start

Requires Docker with Compose v2.

```bash
cp .env.example .env
docker compose up -d --build --wait
curl http://localhost:8000/health   # {"status":"ok"}
```

| What | URL |
|---|---|
| Web UI | http://localhost:8000/ |
| Swagger UI (API docs) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health — `200 {"status":"ok"}`, or `503 {"status":"error"}` if the database is down |

- Logs: `docker compose logs app`
- Stop and wipe the database: `docker compose down -v`

On every start the stand applies migrations and seeds the test user from
`TEST_NAME` / `TEST_EMAIL` / `TEST_PASSWORD` (the same variables the tests read).
If a test deletes that user, a restart (`docker compose restart app`) brings it back.

## Environment variables

One `.env` (copied from `.env.example`, which holds fake values only) feeds both the stand and the tests.
`.env` is git-ignored.

| Variable | Used by | Meaning |
|---|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | stand, tests | Database credentials (avoid `@ : / #` in the password: it goes into a URL) |
| `POSTGRES_PORT` | stand, tests | Host port the database is published on |
| `DB_HOST` | tests | Database host for SQL checks (`localhost`) |
| `APP_PORT` | stand | Host port the app is published on |
| `BASE_URL` | tests | Stand URL; keep it in sync with `APP_PORT` |
| `JWT_SECRET` | stand | HS256 key for access tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | stand | Token and session lifetime (default 60) |
| `TEST_NAME`, `TEST_EMAIL`, `TEST_PASSWORD` | stand, tests | Seeded test user |
| `BUG_<NAME>` | stand | Switches a seeded defect on (see [Known defects](#known-defects)) |

The app gets `DATABASE_URL` from `docker-compose.yml`, assembled from the `POSTGRES_*` variables.

## Account API

Base path `/api/v1`. Every error has the body `{"ok": false, "message": "<text>"}`;
validation errors are `400` (not FastAPI's default `422`).

| Endpoint | Success | Errors |
|---|---|---|
| `POST /auth/register` `{name, email, password}` | `201 {id, name, email, access_token}` | `400` missing / empty / invalid field, `409` email already registered |
| `POST /auth/login` `{email, password}` | `200 {id, access_token}` | `400` missing / empty field, `401` wrong email or password |
| `GET /auth/me` (Bearer token) | `200 {id, name, email}` | `401` no token / bad or expired token |
| `DELETE /auth/me` (Bearer token) | `200 {"ok": true}` | `401` as above |

## Validation rules

The same rules and messages apply to the API, the web forms (server side) and the
browser checks (`app/validation.py` is the single source; JS gets them from the page).

| Field | Rule | Messages |
|---|---|---|
| name | 1–50 characters after trimming | `Name is required`, `Name is too long` |
| email | `x@y.z` shape, up to 254 characters, unique case-insensitively (trimmed and lowercased on register **and** login) | `Email is required`, `Invalid email`, `Email is too long`, `User with this email already exists` |
| password | 6–128 characters | `Password is required`, `Invalid password` (too short), `Password is too long` |

Lengths are counted in characters. Passwords are stored as argon2id hashes in
`users.password_hash`; `users.name` is `VARCHAR(50)`, `users.email` is `VARCHAR(254)`.

## UI

| Page | What it does |
|---|---|
| `/` | Placeholder for the future builder. Guest: **Sign in** button → `/login`. Logged in: **Place order** button (no action yet). |
| `/register` | Name, Email, Password, **Sign up**; "Already registered? **Sign in**" → `/login`. Success → `/login` (no auto-login). |
| `/login` | Email, Password, **Sign in**; **Sign up** → `/register`; **Forgot password?** → `/forgot-password`. Success → `/`. |
| `/forgot-password` | Email + **Recover** → success message (no email is actually sent); "Remembered your password? **Sign in**" → `/login`. |
| `/account` | Logged-in only (guests are redirected to `/login`): name, email, **Log out** → `/login`. |

Header on every page: logo → `/`, **Builder** → `/`, **Account** → `/login` for guests, `/account` when logged in.
There are exactly four entry points to `/login`: the home button, header **Account**, the link on `/register`
and the link on `/forgot-password`.

The session is an httpOnly cookie `access_token` holding the same JWT the API issues.
Forms have `novalidate` and no `maxlength`: every error is our own DOM element under the field.

### Locators

Every interactive element and every message has a `data-testid` (form controls also have the same `id`).
Pattern: `<page>-<element>-<kind>`.

| Page | `data-testid` |
|---|---|
| every page | `header-logo`, `header-builder-link`, `header-account-link`, `<page>-page` on `<main>`, `<page>-title` on `<h1>` |
| `/` | `home-sign-in-button`, `home-place-order-button`, `home-builder-placeholder` |
| `/register` | `register-form`, `register-name-input`, `register-name-error`, `register-email-input`, `register-email-error`, `register-password-input`, `register-password-error`, `register-submit-button`, `register-login-link` |
| `/login` | `login-form`, `login-form-error`, `login-email-input`, `login-email-error`, `login-password-input`, `login-password-error`, `login-submit-button`, `login-register-link`, `login-forgot-password-link` |
| `/forgot-password` | `forgot-password-form`, `forgot-password-email-input`, `forgot-password-email-error`, `forgot-password-submit-button`, `forgot-password-success-message`, `forgot-password-login-link` |
| `/account` | `account-name`, `account-email`, `account-logout-form`, `account-logout-button` |

Error elements are always in the DOM and `hidden` while empty: check visibility, not presence.

## Tests

The suites live in this repo, next to the stand:

```
tests/
  api/              API tests (requests), marker `api`
  ui/               UI tests (Selenium), marker `ui`
  requirements.txt  pinned test dependencies
pytest.ini          test paths, markers, Allure results directory
```

Run them against a running stand:

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r tests/requirements.txt
pytest                 # everything
pytest -m api          # API only
pytest -m ui           # UI only
allure serve allure-results   # needs the Allure CLI locally
```

`BASE_URL`, the test user and the database settings come only from the environment
(`python-dotenv` can load them from `.env`). To test another stand, change `BASE_URL`.

**Browsers.** UI tests run headless Chrome (`--headless=new`) or Firefox (`-headless`).
Selenium ≥ 4.6 includes Selenium Manager: it finds the installed browser and a matching
driver, downloading the driver on first use if needed, so there is nothing to install by hand.
How a run picks a browser (for example a `BROWSER` env var) is up to the test suite.

**SQL checks** connect to `DB_HOST:POSTGRES_PORT` with the `POSTGRES_*` credentials,
e.g. to assert that `users.password_hash` holds an argon2id hash, not the password.

## CI

`.github/workflows/ci.yml` runs on pushes to `main`, on pull requests and manually
(**Run workflow** in the Actions tab):

1. `.env` from `.env.example`, exported to the job environment
2. `docker compose up --build --wait`, then `curl $BASE_URL/health`
3. Python 3.12 + `tests/requirements.txt`
4. Prints the versions of Chrome, ChromeDriver, Firefox and geckodriver on the runner
   (the runner image ships all four; the step fails if one is missing)
5. `pytest`. Exit code 5 ("no tests collected") is reported as a notice and treated as success;
   any other failure fails the job
6. Allure report (pinned Allure CLI) uploaded as the `allure-report` artifact
7. On failure: `docker compose logs`; always: `docker compose down -v`

The Allure report is not published to GitHub Pages yet.

## Project layout

```
app/                FastAPI app
  api/              /health and the JSON API (/api/v1)
  web/              server-rendered pages and the cookie session
  services/         account logic shared by API and pages
  templates/        Jinja2 templates
  static/           CSS and the form-validation JS
  migrations/       Alembic migrations
  strings.py        every user-visible text
  validation.py     field rules shared by API, forms and JS
  defects.py        seeded-defect flags
tests/              test suites (see above)
docker-compose.yml  db + app
```

## Known defects

The stand can deliberately reproduce bugs ("seeded defects") so tests can catch them.
Each defect is off by default and is switched on with `BUG_<NAME>=1` in `.env`
(registry: `app/defects.py`). A misspelled `BUG_*` name or a value other than
`1/true/yes/on` or `0/false/no/off` stops the stand from starting, so a typo can never
silently switch a defect off.

| Flag | Area | Behaviour when enabled | Expected behaviour |
|---|---|---|---|
| — | — | No seeded defects yet | — |
