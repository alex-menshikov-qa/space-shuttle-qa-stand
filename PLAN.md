# PLAN — QA test stand, track 1 (stand skeleton, story-agnostic)

## Goal
A self-hosted test stand that Sasha's portfolio test suites (pytest + Requests / Selenium / Allure) can run against instead of the Yandex Practicum training stands. Porting the tests must come down to changing locators, paths and test data — not test logic. This is a **portfolio stand, not production**, and the README says so.

Track 1 builds only what does not depend on the story (a space company, still being written): accounts (API + UI), DB, Docker, CI, test configs. Contract sections covered: **A1–A5, C6, D**, plus the empty framework for **E** (seeded defects).

## Ground rules
- Work on `feat/stand-skeleton`, draft PR into `main`; merge only after Sasha's OK. One commit (or a few) per stage; after each stage — a short report (what was done, how to check by hand) and stop.
- **No tests from me.** Everything in `tests/` (tests, conftest, fixtures, page objects) is Sasha's. My scope: app, DB, Docker, CI, configs, README. CI proves the stand is alive via healthcheck/curl, not pytest.
- No secrets or real personal data: everything through env; `.env.example` holds fake values; `.env` is git-ignored.
- English everywhere in the repo. Neutral working names (`users`, `auth`, "Builder").
- All user-visible text lives in **templates + one strings module** (`app/strings.py`), so the story PR can re-skin the stand without touching logic.

## Stack (versions pinned exactly in `app/requirements.txt` / `tests/requirements.txt`)
Python 3.12 · FastAPI · Pydantic v2 + pydantic-settings · SQLAlchemy 2 + Alembic · PostgreSQL 16 · psycopg 3 · argon2-cffi · PyJWT · Jinja2 · uvicorn. Front end: server-rendered Jinja2 + a little vanilla JS, no bundlers, no SPA.

## Repository layout
```
app/
  Dockerfile, entrypoint.sh, requirements.txt, alembic.ini
  main.py            # app factory: routers, static, templates, error handlers
  config.py          # Settings from env (pydantic-settings)
  db.py              # engine, session dependency
  models.py          # SQLAlchemy models (User)
  schemas.py         # Pydantic request/response models
  security.py        # argon2 hashing, JWT encode/decode
  validation.py      # shared field rules (name / email / password) used by API AND web forms
  strings.py         # every user-visible string: UI labels, error messages
  defects.py         # seeded-defect flags (BUG_<NAME>=1), all off by default
  errors.py          # unified error format + exception handlers
  seed.py            # idempotent test-user seed
  services/users.py  # register / authenticate / get / delete — one code path for API and UI
  api/health.py      # GET /health
  api/v1/auth.py     # /api/v1/auth/*
  web/               # page routes + cookie session helpers
  templates/         # base.html, partials/header.html, home, register, login, forgot_password, account
  static/            # css/main.css, js/forms.js
  migrations/        # Alembic env + versions
tests/
  api/.gitkeep  ui/.gitkeep  requirements.txt
pytest.ini  docker-compose.yml  .env.example  .gitignore  .dockerignore
.github/workflows/ci.yml  PLAN.md  README.md
```
Docker build context is the repo root (`dockerfile: app/Dockerfile`), `.dockerignore` excludes `tests/`, `.git`, `.env`.

## Stages

### Stage 1 — Docker Compose + app skeleton
- `db`: `postgres:16`, `pg_isready` healthcheck, named volume, port published to host as `${POSTGRES_PORT}` (tests will run SQL checks, e.g. that the password is stored as a hash).
- `app`: depends on `db` (`service_healthy`); entrypoint runs `alembic upgrade head` → seed → `uvicorn`; healthcheck hits `/health` (python one-liner, no curl in the slim image); port `${APP_PORT}`.
- `docker compose up --wait` brings everything up in one command, locally and in CI.
- `GET /health` → `200 {"status": "ok"}` after a `SELECT 1`; DB unreachable → `503 {"status": "error"}`.
- Swagger stays at `/docs`.
- Seeded-defect framework: `app/defects.py` keeps a registry of known defect names (empty for now) and `is_enabled(name)` reads `BUG_<NAME>` from env (`1/true` = on, default off; unknown names fail loudly so a typo can't silently disable a bug). README gets an empty **Known defects** table.

### Stage 2 — Account API (`/api/v1`)
These are **web-account** endpoints. The courier/pilot API from contract section C is a separate entity with its own semantics and comes later.

Unified error body: `{"ok": false, "message": "<text>"}` for every error. Validation errors → **400** (FastAPI's default 422 handler is overridden; `HTTPException` is mapped to the same shape). Messages come from `strings.py`.

Validation rules (one implementation in `validation.py`, shared by API and UI):
- `name` — non-empty after trim;
- `email` — matches `^[^\s@]+@[^\s@]+\.[^\s@]+$` (an own pattern instead of `EmailStr`, which rejects reserved domains and would make API and UI disagree); the same pattern is rendered into the templates for client-side checks, so there is a single source; unique case-insensitively (stored trimmed + lowercased, unique index). The same normalization (trim + lowercase) is applied on **login** too — in the API and in the web form — via one `normalize_email()` in `validation.py`;
- `password` — at least 6 characters.
- Max lengths (added at Sasha's request in stage 3, for boundary-value testing): `name` 1–50, `email` up to 254, `password` 6–128 characters. Enforced in `validation.py` (API, server forms and JS alike) with their own messages ("Name is too long", …), mirrored by DB column limits (`VARCHAR(50)` / `VARCHAR(254)`, migration `0002`). The UI does **not** use the `maxlength` attribute: over-limit input stays typeable and produces our own error under the field.

| Endpoint | Success | Errors |
|---|---|---|
| `POST /api/v1/auth/register` `{name, email, password}` | 201 `{id, name, email, access_token}` | 400 missing / empty / invalid field (message names the field); 409 duplicate email |
| `POST /api/v1/auth/login` `{email, password}` | 200 `{id, access_token}` | 400 missing / empty field; 401 wrong password **or** unknown user — identical message |
| `GET /api/v1/auth/me` (Bearer) | 200 `{id, name, email}` | 401 no / malformed / expired token, or user deleted |
| `DELETE /api/v1/auth/me` (Bearer) | 200 `{"ok": true}` (hard delete — for test teardown) | 401 as above |

- Passwords: argon2id (`$argon2id$...` in the `password_hash` column — trivially checkable by SQL).
- JWT: HS256, `sub` = user id, `exp` from `ACCESS_TOKEN_EXPIRE_MINUTES`, secret from `JWT_SECRET`.
- Seed: on every start, idempotently ensure the user `TEST_EMAIL` / `TEST_PASSWORD` (name `TEST_NAME`) exists — created if missing, password re-synced to env if it exists. Same variable names the tests read, so one `.env` feeds both the stand and the tests.

### Stage 3 — Account UI (contract A1–A5)
Working English paths and texts. Every interactive element and every error message gets a stable `data-testid` (and an `id` on form fields). Naming convention: `<page>-<element>-<kind>`, e.g. `header-logo`, `header-builder-link`, `header-account-link`, `home-sign-in-button`, `home-place-order-button`, `register-name-input`, `register-name-error`, `register-submit-button`, `login-form-error`, `account-logout-button`. The full list goes into the README.

- **Header (every page):** logo → `/`; "Builder" → `/`; "Account" → `/login` for guests, `/account` when logged in. Nav items are defined in one list, so a future "Booking" section is a one-line addition.
- **Home `/`:** guest — "Sign in" button → `/login`; logged in — "Place order" button instead (no action yet, visible, has a testid). The rest is a placeholder for the future builder.
- **`/register`:** Name, Email, Password; "Sign up"; link "Already registered? Sign in" → `/login`. Success → redirect to `/login` (no auto-login).
  - Empty name or email without "@" and a dot → no registration, URL unchanged, error under the field. Password < 6 chars → visible "Invalid password" under the field. Checked in JS before submit **and** on the server (direct POST re-renders the form with errors, HTTP 400, URL stays `/register`).
- **`/login`:** Email, Password; "Sign in"; links "Sign up" → `/register`, "Forgot password?" → `/forgot-password`. Success → `/` with "Place order". Bad credentials → form-level error.
- **`/forgot-password`:** email field + button; after submit — success message (no email is sent); link "Remembered your password? Sign in" → `/login`.
- **`/account`:** logged-in only, otherwise redirect to `/login`; shows name and email; "Log out" → clears the session, redirect to `/login`.
- Exactly **four entry points to login**: home button, header "Account", link on `/register`, link on `/forgot-password`.
- Session: `httpOnly` cookie (`SameSite=Lax`) carrying the same JWT the API issues. Forms use POST → 303 redirect (PRG); logout is a POST. Minimal neutral CSS, no story texts.
- Every `<form>` has `novalidate`, so native browser validation (`type="email"`, `required`) never pre-empts our own error messages — Selenium can't read native tooltips; all errors are real DOM elements with testids.

### Stage 4 — Test scaffolding + CI + Allure + README
- `tests/requirements.txt` (pinned): pytest, requests, selenium, faker, allure-pytest, python-dotenv. Root `pytest.ini`: `testpaths = tests`, markers `api` and `ui`, `--alluredir=allure-results`. `BASE_URL` and credentials come only from env. No conftest, fixtures or tests.
- `.github/workflows/ci.yml` on `push` to `main`, `pull_request` and `workflow_dispatch` (changed in stage 4 at Sasha's request: push to any branch plus `pull_request` would run CI twice for every commit on a PR branch):
  1. checkout → `cp .env.example .env`
  2. `docker compose up -d --build --wait` → `curl -fsS $BASE_URL/health`
  3. `actions/setup-python` 3.12 → `pip install -r tests/requirements.txt`
  4. print browser/driver versions (see below)
  5. `pytest`; exit code 5 ("no tests collected") is caught explicitly, logged as a `::notice::` ("No tests collected yet — treated as success"), any other non-zero code fails the job
  6. generate the Allure report with a pinned Allure CLI (Java is on the runner) → upload `allure-report` as an artifact
  7. `if: failure()` → `docker compose logs`; `if: always()` → `docker compose down -v`
- No Allure publishing to GitHub Pages (later step).

**Browsers for future UI tests.** GitHub's `ubuntu-latest` image ships Google Chrome + ChromeDriver and Firefox + geckodriver (exposed via `CHROMEWEBDRIVER` / `GECKOWEBDRIVER`). Selenium ≥ 4.6 has Selenium Manager, which finds the installed browser and a matching driver automatically, so tests just create `webdriver.Chrome(options)` / `webdriver.Firefox(options)` with headless flags (`--headless=new` / `-headless`) — nothing to install in CI. The CI step in 4 prints `google-chrome --version`, `chromedriver --version`, `firefox --version`, `geckodriver --version`, so their presence is verified on every run. Locally, Selenium Manager downloads drivers on first use. Which browser a run uses is the tests' concern (e.g. a `BROWSER` env var) — documented in README, not implemented by me.

- **README:** what this is (portfolio test stand, not production), quick start, env variables table, links (`/docs`, `/health`, UI pages), where the tests live and how to run them, the testid list, the Known defects table.
- Last step: switch the PR from draft to ready and wait for review.

## Environment variables (`.env.example`, fake values)
`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT` (host port) · `APP_PORT` · `JWT_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES` · `TEST_NAME`, `TEST_EMAIL`, `TEST_PASSWORD` · `BASE_URL` (for tests) · `DB_HOST` (for tests' SQL checks; the port is the same `POSTGRES_PORT` — one variable for the DB host port) · `BUG_<NAME>` (optional, defects). `DATABASE_URL` for the app is assembled in `docker-compose.yml`.

## Decisions
| Topic | Decision | Why |
|---|---|---|
| Password hashing | argon2id (argon2-cffi) | modern default; hash is self-describing for SQL checks |
| Auth | single JWT access token, Bearer for API, same JWT in httpOnly cookie for UI | one auth model; no refresh tokens (out of scope) |
| Email uniqueness | trim + lowercase on register **and** login (API + web), unique index | case-insensitive without a citext extension |
| Form validation | `novalidate` on every form; only our own DOM errors | Selenium can't read native browser tooltips |
| DB port for tests | tests read `POSTGRES_PORT` + `DB_HOST`, no separate `DB_PORT` | one source of truth for the host port |
| Email format | own regex shared by API, server forms and JS | identical rules everywhere, matches the contract wording |
| Error shape | `{"ok": false, "message"}`, validation → 400 | task requirement; also contains `message`, compatible with section C |
| Migrations/seed | run in the app entrypoint before uvicorn | `up --wait` yields a ready, seeded stand |
| UI forms | plain HTML forms + PRG, JS only for client-side validation | no build step, robust for Selenium |
| Texts | `strings.py` + templates only | story PR re-skins in one place |
| Defects | env flags `BUG_<NAME>`, registry in `defects.py`, all off | contract section E; ready for the C xfail cases |

## Kept open for later (not built now, but not blocked)
- **A6 Builder** — lives on `/` (home is already a placeholder with the header link and the "Place order" button); tabs/sections/ingredients come with the story.
- **B Booking** — a second section of the same site: same `base.html`, same header (one more nav item), same account/cookie; its own `web/booking` routes, partner-stub page, FAQ accordion with predictable ids.
- **C Pilots/flights API** — separate tables and routers under `/api/v1` with the contract's own semantics (`{"ok": true}`, 404 on bad login, `track`), independent from web accounts; the known training-stand bugs (409 instead of 400, 504 instead of 400) become seeded defects behind `BUG_*` flags.
- Story vocabulary (names, texts) — a separate PR, touching `strings.py` and templates.
- Out of scope for this track: hosting, Playwright, Allure on Pages, refresh tokens, real email sending. Contract section F (notes on the tests) is not touched.

## How to verify (per stage, also in each stage report)
- Stage 1: `cp .env.example .env && docker compose up -d --build --wait`; `curl localhost:8000/health`; open `/docs`; `docker compose ps` shows both healthy.
- Stage 2: curl / Swagger through every row of the API table; `psql` → `SELECT email, password_hash FROM users;` shows `$argon2id$...`; restart app → seed user is still single.
- Stage 3: click through the four login entry points, the validation cases, logout, guest redirect from `/account`; check testids in DevTools.
- Stage 4: CI run on the PR is green; log shows browser versions and the explicit "no tests collected" notice; the Allure artifact is downloadable.
