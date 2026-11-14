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

---

# Track 2 — the Space Shuttle Inc story

## Goal
Dress the stand in its story and add the rest of the contract: A6 (shipyard), B (rental landing, order form, order status), C1–C5 (autopilot / station / order API) and the first seeded defects (E). Section F is not touched.

Space Shuttle Inc rents shuttles on Coruscant. A shuttle flies itself: its autopilot is a droid employee (login, password, first name) who takes orders through the API. At the Shipyard a customer builds a shuttle from parts. Company, product and world are our own: no third-party logos, images or quotes; the logo and part pictures are our own inline SVG / CSS, no external files or fonts.

## Ground rules (same as track 1, plus)
- Branch `feat/story`, draft PR into `main`, merge only after Sasha's OK. After each stage: report (done / how to check by hand / deviations from PLAN.md as a separate list) and stop.
- No tests from me; verification scripts live outside the repo.
- Every visible text in `strings.py` + templates. Catalog, stations, FAQ and fleet are **data** in `app/data/*.json`, not code.
- Functional texts (labels, errors, buttons) are plain and serious; irony only in decoration (FAQ, 404, empty states, part descriptions). API error texts and field limits come from the 2023 checklists verbatim and are not "improved".
- `data-testid` on every interactive element and message, `<page>-<element>-<kind>`; full list in README. Account-page testids are unchanged.
- One validation implementation for API, server and JS (`validation.py` → `client_rules()`), `novalidate`, no `maxlength`.
- Error body stays `{"ok": false, "message": "..."}`.

## New layout
```
app/
  data/               stations.json, fleet.json, faq.json, shipyard_parts.json
  clock.py            stand "now"/"today" in STAND_TZ; per-order clock offset
  models.py           + Autopilot, Station, Order, ShipyardPart, ShipyardOrder(+items)
  seed.py             + stations, fleet, shipyard parts (idempotent sync from app/data)
  services/           autopilots.py, stations.py, orders.py, shipyard.py
  api/v1/             autopilot.py, stations.py, orders.py, shipyard.py, testing.py
  web/                landing.py, order.py, track.py, shipyard.py
  templates/          home (landing), holonet, order, track, shipyard, not_found, partials/modal
  static/js/          header.js, landing.js, order.js, track.js, shipyard.js
  migrations/versions 0003 autopilots+stations+orders, 0004 shipyard
```

## Stage 1 — Re-skin and landing
- **Header (all pages):** logo "Space **Shuttle** Inc" — "Space Shuttle" links to `/` (`header-logo-link`), "Inc" is plain text (`header-logo-inc`). Partner mark "HoloNet" → `/holonet`, `target="_blank"` (`header-holonet-link`). Nav: "Shipyard" → `/shipyard` (`header-shipyard-link`); "Order" → `/order` (`header-order-button`); "Order Status" (`header-status-button`) reveals "Order Number" input + "Go!" (`header-status-input`, `header-status-go-button`), click or Enter → `/track?t=<number>`; "Account" unchanged.
- **`/` landing:** title + short pitch, bottom "Order" (`home-order-button`), cookie banner with accept button (home only, fixed to the bottom, remembered in a cookie), FAQ accordion of 8 from `faq.json`: one panel open at a time, ids exactly `accordion__heading-N` / `accordion__panel-N`, N = 0…7.
- **`/holonet`:** own HoloNet news stub page.
- **`/shipyard` stub:** the builder placeholder plus "Sign in" (`shipyard-sign-in-button`) for guests / "Place order" (`shipyard-order-button`) when logged in. Login success now redirects to `/shipyard`. Four login entry points: `/shipyard` button, header "Account", `/register` link, `/forgot-password` link.
- **404:** paths outside `/api/` get an HTML page with the header, the "Our autopilots searched every sector…" text and a link home; `/api/*` keeps JSON.
- Renamed testids: `header-logo`, `header-builder-link`, `home-sign-in-button`, `home-place-order-button` (see above).

## Stage 2 — Autopilot, station and order API (`/api/v1`)
Autopilots are their own entity (table `autopilots`), no tokens. Request fields are accepted untyped and checked by `validation.py`, so a number or null gets the documented 400, not a pydantic message.

| Request | Success | Errors |
|---|---|---|
| POST /autopilot {login, password, firstName} | 201 {"ok": true} | 400 "Insufficient data to create an account" (any field missing or invalid) · 409 "This login is already in use. Please try another one" |
| POST /autopilot/login {login, password} | 200 {"id": int} | 400 "Insufficient data to log in" · 404 "Account not found" |
| DELETE /autopilot/{id} | 200 {"ok": true} | 400 "Insufficient data to delete the autopilot" (no id) · 404 "There is no autopilot with such id" (also for a non-numeric id) |
| GET /stations/search?s= | 200 {"stations": [{number, name, color}]}, case-insensitive substring, no `s` → all | — |
| POST /orders | 201 {"track": int} | 400 with the field's form message |
| GET /orders[?autopilotId=] | 200 {"orders": [...]} | 404 "Autopilot with identifier {autopilotId} not found" |
| GET /orders/track?t= | 200 {"order": {...}} | 400 "Insufficient data to perform the search" · 404 "Order not found" |
| PUT /orders/accept/{id}?autopilotId= | 200 {"ok": true} | 400 "Insufficient data to perform the search" · 404 "There is no order with such id" / "There is no autopilot with such id" · 409 "This order is already in progress" |
| PUT /orders/finish/{id} | 200 {"ok": true} | 404 "There is no order with such id" · 409 "This order cannot be finished" (not accepted, or already finished) |
| PUT /orders/cancel {track} | 200 {"ok": true} | 400 "Insufficient data to perform the search" · 404 "Order not found" · 409 "This order is already in progress" |

- **Autopilot rules:** login — string of 2–10 Aurebesh (Latin) letters; password — string of exactly 4 digits; firstName — string of 2–10 letters, required. Password stored as an argon2id hash (`security.hash_password`). Columns are `TEXT` so seeded defects can store out-of-rule values.
- **Delete** is a hard delete (login becomes free again). Orders keep `autopilot_first_name` as a snapshot and get `autopilot_deleted = true`; such orders are no longer found by track or listed.
- **Order fields:** firstName, lastName, address, station (number), phone, rentTime (1–7), deliveryDate (`YYYY-MM-DD`, not before tomorrow), comment, color (`[]`, `["PINKY_SWEAR"]`, `["GRAY_RAINBOW"]`, both). Limits as in the form (stage 3); address is trimmed before the check. `track` — random unique 5-digit number (10000–99999), as in the canonical "Order number NNNNN".
- **Order object:** `{id, track, firstName, lastName, address, station: {number, name, color}, phone, rentTime, deliveryDate, comment, color, status, autopilotId, autopilotFirstName, createdAt, acceptedAt, finishedAt, rentalEndsAt}`; `status` is one of `hangar`, `heading`, `on_site`, `flying`, `ended`, `delayed`.
- Cancel is a soft delete (`canceled_at`); canceled orders are not found or listed.
- **"Tomorrow"** is computed by the server in `STAND_TZ` (default `UTC`).
- **Seed (idempotent):** stations and fleet from `app/data`; fleet password from `FLEET_PASSWORD` (default `0101`), re-synced on start like the test user.

## Stage 3 — Order form and order status
- **`/order`**, one page, two steps switched by JS; a direct URL opens step 1. Submits to `POST /api/v1/orders`.
- **Step 1 "For Whom is the Shuttle":** Name · Last Name · "Address: where the shuttle will arrive" · Shuttle Station (search from 1 character via `/stations/search`, colored dot before the name, pick by click) · "Phone: the autopilot will call" · "Next". Placeholders are the field names, required ones with an asterisk. Error under the field + red border; errors block step 2.

| Field | Rule | Message |
|---|---|---|
| Name | Aurebesh letters, space, hyphen; 2–15 | Enter the correct name |
| Last Name | Aurebesh letters; 2–15 | Enter the correct last name |
| Address | letters, digits, space, hyphen, dot, comma; 5–50; trimmed on blur | Enter the correct address |
| Station | required, must be picked from the list | Select a station |
| Phone | digits and "+"; 10–12 | Enter the correct phone number |

- **Step 2 "About Rent":** "When to Bring the Shuttle" — own date picker opening on the current month, days before tomorrow disabled, typing allowed in **`DD.MM.YYYY`**, required · Rental Period — custom dropdown (not `<select>`) "one day" … "seven days", required · Shuttle Color — checkboxes "pinky swear", "gray rainbow" · "Comment for Autopilot" — letters, space, hyphen, dot, comma; up to 24; optional · "Back" (step 1 data kept) and "Order".
- Step 2 errors: "Enter a valid date", "Enter a valid rental period", "Enter a valid comment".
- Valid → modal "Do you want to place the order?" Yes / No → modal "Order number NNNNN. Write it down: it will come in handy to track the status" + "View Status" → `/track?t=`. Several orders in a row work.
- **`/track?t=`** (server-rendered), as in the 2023 checklist:
  - Its own search row under the header: a long "Order Number" input (`track-number-input`) with a "View" button on the right (`track-view-button`); search by click and by Enter. Present in both variants of the page, "found" and "not found". The header "Go!" search stays as well.
  - Order data in three groups separated by gray lines: (Name, Last Name, Address, Shuttle Station with its colored dot, Phone) · (When to Bring the Shuttle, Rental Period) · (Shuttle Color, Comment for Autopilot). With no comment only the caption is shown and the value is empty. Every value has its own testid (`track-name-value`, `track-last-name-value`, `track-address-value`, `track-station-value`, `track-phone-value`, `track-date-value`, `track-period-value`, `track-color-value`, `track-comment-value`).
  - The status chain, current one highlighted:
  1. "Shuttle in the hangar" — "Your autopilot is warming up for departure"
  2. "Autopilot <firstName> is heading towards you" — after accept; shows support phone 0101
  3. "Autopilot is on site" — after finish; "Pick up the shuttle and pay the rental fee"
  4. "Okay, let's fly now" — `PICKUP_MINUTES` (default 10) after finish; "Rental ends on <day> at <time>" (finish + rentTime days)
  5. "Rental time has ended" — after the rental end; caption, verbatim: "<firstName> is heading home to recharge. Thanks for flying with us."
  - "Autopilot delayed" — delivery day is over (after 23:59 `STAND_TZ`) and the order is not finished (status 1 or 2); finish returns it to 3. Caption, verbatim from the 2023 checklist: "We won't be able to deliver the shuttle on time. To check the status of your order, please call support at: 0101". Both the status and the caption are red.
- "Cancel order" only while not accepted: modal "Do you want to cancel the order?" → "Order canceled. Come back, we are always waiting for you :)". Not found (incl. canceled) → "There is no such order. Are you sure you entered the correct number?".
- **Time travel for tests.** Status is a pure function of the order's timestamps and the order's own clock (`now + clock_offset`). `POST /api/v1/testing/orders/{track}/time-shift {"hours": N}` (also `minutes`, `days`) adds to that order's offset → 200 `{"order": {...}}`. Enabled only with `TEST_HOOKS=1`; off by default (code and `.env.example`) → 404. CI switches it on explicitly. Per-order, so tests stay parallel-safe and date validation is unaffected.

## Stage 4 — Shipyard `/shipyard`
- Title "Build your shuttle". Tabs Hulls / Engines / Modules: click scrolls to the section's `<h2>`, scroll-spy switches the active tab, first is active by default; active = class `tab--active` + `data-active="true"`.
- Part cards: inline SVG picture, name, price in credits, in-build counter (hidden at 0), "Add". Card click → modal with description and Mass, t · Power, MW · Cargo, m³ · Comfort, ★; closed by ✕, Esc, backdrop click.
- **Build:** add by drag into the build area or by "Add". Dragging and in-build reordering are built on `mousedown` / `mousemove` / `mouseup`, **not** HTML5 Drag and Drop; verified by me with Selenium ActionChains (`click_and_hold → move_to_element → release`) in headless Chrome and Firefox.
- One hull (a new one replaces the old), shown as "<name> (Top plating)" and "<name> (Belly plating)", priced twice. Any number of engines and modules, reorderable, removable. Empty: "No hull, no shuttle. Drag one here to begin."
- Total recalculated on every change on the client; the server recomputes from its own prices on order. Build state lives in `sessionStorage` (survives the guest → login round trip).
- Guest: "Sign in" → `/login`; logged in: "Order this shuttle". No hull → clear error, no order. Success → modal with the build order number. Not related to `/order` and `/track`.
- **API:** `GET /api/v1/shipyard/parts` → 200 `{"parts": [{id, category, name, price, description, mass, power, cargo, comfort}]}` · `POST /api/v1/shipyard/orders` (Bearer) `{"parts": [id, ...]}` → 201 `{"number", "total"}`; 401 without token; 400 for no hull / two hulls / unknown id · `GET /api/v1/shipyard/orders` (Bearer) → own orders. The page itself posts to the cookie-authenticated web route `POST /shipyard/orders`, same service.
- Catalog from `shipyard_parts.json` (stable `id` per part; order items snapshot name and price, so renames and re-pricing never rewrite old orders). Specs chosen by me and shown in the stage report.

## Stage 5 — Seeded defects, README, finish
Flags registered in `app/defects.py`, all off by default.

| Flag | With the flag | Without |
|---|---|---|
| BUG_AUTOPILOT_LOGIN_RULES | any non-empty login is accepted (Cyrillic, 1 or 11 chars, spaces, a number) | 400 |
| BUG_AUTOPILOT_PASSWORD_RULES | "123", "12345", "lttr", an unquoted number pass | 400 |
| BUG_AUTOPILOT_NAME_RULES | "K", 11 chars, "1234", spaces pass | 400 |
| BUG_MISSING_NAME_409 | create without firstName → 409 (login-in-use message) | 400 |
| BUG_LOGIN_NO_PASSWORD_504 | autopilot login without password → 504 | 400 |
| BUG_TRACK_DELETED_AUTOPILOT | a deleted autopilot's order is still found by track (page and API) | 404 |
| BUG_CANCELED_ORDER_VISIBLE | a canceled order is still shown (status 1; page and API) | "There is no such order…" |
| BUG_STATUS_SEARCH_ENTER | Enter in the header order search does nothing | works |
| BUG_ADD_BUTTON_STALE_TOTAL | "Add" adds the part but the total is not recalculated | recalculated |

README: Known defects table (flag, what breaks, expected behaviour), site map, all new endpoints, field rules, full testid list, updated "four login entry points". CI green → PR to ready → wait for review.

## New environment variables
`FLEET_PASSWORD` (default `0101`) · `STAND_TZ` (default `UTC`) · `PICKUP_MINUTES` (default `10`) · `TEST_HOOKS` (default off) · `BUG_*` flags above.

## Decisions (track 2)
| Topic | Decision | Why |
|---|---|---|
| Story data | JSON files in `app/data`, synced into tables by the seed (FAQ read directly) | Sasha edits names and texts without touching code |
| Time-dependent statuses | per-order clock offset behind `TEST_HOOKS` | no waiting, parallel-safe, off by default |
| Date in the UI | `DD.MM.YYYY`; API keeps `YYYY-MM-DD` | matches the existing UI tests |
| "Today" | server clock in `STAND_TZ`, passed to the date picker | browser and server never disagree |
| Deleted / canceled | autopilot hard-deleted, orders flagged; cancel is a soft delete | needed for the two "still visible" defects |
| Shipyard order from the page | cookie web route + Bearer API over one service | httpOnly cookie is unreadable by JS; API stays strictly Bearer |
| Drag and drop | mouse events, no HTML5 DnD | Selenium ActionChains works without JS workarounds |
| HTML vs JSON 404 | by path prefix (`/api/`), not by `Accept` | deterministic for `requests` and browsers |

## Out of scope
Autopilot mobile app, payment, real emails, hosting, Playwright, Allure on Pages, linking a build to a rental.

---

# Track 3 — the 2023 canon and seeded defects from the manual checklists

## Goal
In 2023 Sasha tested Space Shuttle Inc by hand and filed bugs SSI-3…SSI-62. This stand is that
product, rebuilt. Track 3 does two things:
1. brings the stand to the **canon** — the product as the 2023 checklists and the order-form mind
   map describe it;
2. turns the 2023 bugs into switchable seeded defects (`BUG_*`, as in track 2).

Sources (never committed): Check List Web (115 checks in two environments, SSI-3…SSI-28),
Check List API (SSI-29…SSI-62), Field Validation (86 checks, 13 failed), the order-form mind map.
A check that PASSED is how the product must behave. A check that FAILED was a bug: the stand
behaves correctly by default and the bug is switched on by a flag.

## Ground rules (as in track 2)
- Branch `feat/canon-defects`, draft PR into `main`, merge only by Sasha. After each stage: report
  (done / how to check by hand / deviations from PLAN.md as a separate list / CI result on the PR).
- PR events are only reported; nothing is fixed or pushed without Sasha's OK.
- No tests from me; verification scripts live outside the repo. The UI is checked with Selenium:
  Chrome always, Firefox where stated.
- Defects leave no marker in the markup or the scripts.
- English everywhere; texts in `strings.py` and templates.

## What the canon does not undo
- The date can be typed, format `DD.MM.YYYY`.
- Shuttle colour is two checkboxes, both may be ticked.
- Status captions stay as they are on the stand (the 2023 texts are outdated).
- Field names follow the mind map ("When to Bring the Shuttle"), not the checklist.
- Five statuses (Web 6.1), not four (Web 3.8).
- Everything decided in track 2 and written above.

## Decisions (track 3)
| Topic | Decision | Why |
|---|---|---|
| Autopilot `firstName` | stays required, Latin 2–10 | track 2; API checks 3.5–3.7 ("Котя", empty, missing → 201) are listed as not reproduced |
| SSI-39, `login: true` | with `BUG_AUTOPILOT_LOGIN_RULES` → 500, autopilot not registered | as in 2023; `password: true` and `firstName: true` → 201 under their own flags |
| Comment charset | Latin letters, **digits**, space, hyphen, dot, comma; up to 24 | Field Validation "Wanna 5" is a PASSED positive check |
| Black | primary buttons are `#1a1a1a` | pure black cannot get darker, and SSI-7 needs it to |
| Hover | header "Order" → `#333333`; step-2 "Order" → `#444444` | Web 1.17, mind map |
| "Cancel order" after accept | visible but disabled | Web 4.21 |
| `/track` title | the `<h1>` stays above the search row | existing testid; Web 1.21 listed as not reproduced |
| Header "Go!" | stays next to Enter | track 2 |
| Layout-only bugs | SSI-3, 8, 9, 11, 17, 20, 23: the correct layout is built, no flag | pixel-level, not worth a flag |
| Two-line messages (stage 1) | "There is no such order." / "Are you sure…", "Order canceled." / "Come back…", "Order number N." / "Write it down…" are two elements each; the old testid stays on their wrapper; the first line keeps its full stop | the canon gives the two lines different sizes |
| Calendar (stage 1) | a drop-down over the form, no longer in the page flow; weekdays are `MO` … `SU` | mind map; closing it must not move the field being clicked |
| Calendar closes on a typed date (stage 3) | once a complete date is typed the calendar closes | as a drop-down it would cover "Rental Period" |
| Error line (stage 4) | every order-form field keeps an empty line for its error; `BUG_FORM_ERROR_LAYOUT_SHIFT` (origin: new) brings the jump back | a click that left an invalid field for "Rental Period" missed |
| Booleans under `*_RULES` (stage 4) | `password: true` / `firstName: true` are stored as "true"; a whitespace-only value stays 400 | SSI-49, SSI-60; API 4.12, 5.8, 6.10 |
| Every primary button (stage 1) | black on all pages, not only the ones the task lists | one button style across the site |

## Mechanism
- `main.css` is served through the same `#if / #else / #endif` preprocessor as the page scripts
  (`/* #if NAME */` in CSS), so CSS-only defects change the styles and nothing else. The
  Firefox-only defect uses an `@supports` test only Gecko passes: no User-Agent sniffing.
- Template defects: values and structure are chosen in Python; templates receive plain data.
- Field defects: the patterns in `validation.py` consult the flags and feed both
  `order_errors()` and `client_rules()`: API, server and JS stay one implementation.

## Stage 1 — Canon: look and small behaviour
- **Buttons.** Primary (black, white centred text): "Order" (header, landing, step 2), "Next",
  "View", "View Status", "Okay", "Back" in the cancel modal. White with a black border and black
  text: "Back" on step 2, "Cancel order", "Cancel" in the cancel modal. "Order Status" merges with
  the background, black text, no hover change. Hovers as decided above.
- **Header "Order Number":** gray border, gray left-aligned placeholder.
- **`/track`:** long search input with a black border and black "View" to its right; order data
  with gray left-aligned captions and black right-aligned values in three groups; coloured dot
  level with the station name; status chain with numbered circles joined by a vertical line, a
  checkmark instead of the number once a status is passed, inactive gray, active black.
- **Not found:** under the search row a black-framed picture (own inline SVG: a shuttle lying on
  the runway, both wings detached); centred at its top "There is no such order" in large black,
  below it, smaller, "Are you sure you entered the correct number?". Testids:
  `track-not-found-image`, `track-not-found-title`, `track-not-found-hint`;
  `track-not-found-message` stays as their wrapper.
- **Cancel modals (Web section 4):** small centred window; large bold centred text at the top;
  "Back" (black) and "Cancel" (white, black border) centred at the bottom. "Order canceled" is the
  same size: large title, smaller second line, "Okay" at the bottom right, leading to the landing.
- **Order form (mind map):** placeholders with an asterisk on required fields; borders gray
  (inactive) / blue (focus) / black (valid) / red (error); calendar icon at the right edge, the
  calendar window with month and year, month arrows, two-letter weekdays, red weekends; rental
  period with a "v" icon and a list as wide as the field.
- The report carries a table of PASSED checks deliberately not reproduced, with reasons.

## Stage 2 — Defects from Check List Web
Each is its own flag, off by default; the API answers correctly unless stated.

| Flag | Bug | What breaks |
|---|---|---|
| BUG_HEADER_SEARCH_PLACEHOLDER | SSI-4 | header "Order Number" placeholder reads "Enter order number" |
| BUG_STATUS_SEARCH_ENTER (exists) | SSI-5 | unchanged |
| BUG_TRACK_NO_IMAGE | SSI-6 | no picture on "order not found" (the text stays) |
| BUG_ORDER_HOVER_VULPTEX | SSI-7 | header "Order" darkens on hover (`#000000`) instead of lightening — Firefox only |
| BUG_TRACK_WRONG_STATION | SSI-10 | `/track` shows the next station by number (the first after the last), with its colour |
| BUG_TRACK_PERIOD_GROUP | SSI-12 | "Rental Period" sits in the third group |
| BUG_TRACK_DATE_MINUS_DAY | SSI-13 | delivery date on `/track` is one day early |
| BUG_TRACK_EMPTY_COLOR | SSI-14 | no colour → the value reads `null` |
| BUG_TRACK_EMPTY_COMMENT | SSI-15 | no comment → the value reads `undefined` |
| BUG_TRACK_NO_WRAP | SSI-16 | long values do not wrap and stick out of the block |
| BUG_STATUS_ON_SITE_SKIPPED | SSI-19 | after finish status 2 holds until `PICKUP_MINUTES`, then 4 (API and page) |
| BUG_CANCELED_MODAL_FULLSCREEN | SSI-21, SSI-22 | the "Order canceled…" modal is full-screen |
| BUG_DELAYED_ONE_DAY_LATE | SSI-27 | "Autopilot delayed" comes a day late (API and page) |
| BUG_ENDED_STATUS_4_ACTIVE | SSI-28 | after the rental ends status 4 stays highlighted with 5, with "Rental ends on…" |

Not seeded: SSI-3, 8, 9, 11, 17, 18, 20, 23, 24 (pixel-level layout, or the check was SKIPPED).

## Stage 3 — Defects from Field Validation
One implementation of the field rules, so each defect acts in the form and in `POST /api/v1/orders`.

| Flag | What breaks |
|---|---|
| BUG_FORM_NAME_DASH | Name with a hyphen is rejected ("Meetra-Koth") |
| BUG_FORM_LAST_NAME_16 | Last Name accepts 16 characters ("Grandmoffftarkin"); 17 still rejected |
| BUG_FORM_ADDRESS_REQUIRED | an empty Address is accepted (1–4 characters still rejected) |
| BUG_FORM_ADDRESS_50 | Address of exactly 50 characters is rejected |
| BUG_FORM_PHONE_12 | Phone of 12 characters is rejected ("+38160123456"); 10 and 11 pass |
| BUG_FORM_COMMENT_CHARSET | Comment accepts Cyrillic, other scripts and quotes |
| BUG_FORM_COMMENT_LENGTH | Comment has no upper limit |
| BUG_FORM_DATE_TODAY | today can be picked, typed and sent to the API; yesterday cannot |

The checklist's 90-character comment contains apostrophes, so verbatim it passes only with both
COMMENT flags; the length flag alone is checked with the 25-character string and a 90-character
string of allowed characters.

## Stage 4 — API reconciliation, README, finish
- Every failed item SSI-29…SSI-61 verbatim: with the flag 201 (SSI-39: 500), without 400.
  A whitespace-only login, password or firstName stays 400 even with the flag (API 4.12, 5.8,
  6.10 passed in 2023).
- README: **Origin** column in Known defects (`SSI-n`, `Field Validation 2023`, `training stand`,
  `new`), a "not seeded" table with reasons, an "Environments" paragraph ("Beskar, 1920×1080" =
  Chrome, "Vulptex Browser, 1280×720" = Firefox), updated rules and testids.
- Regression with every flag off, then every new flag on its own. CI green → PR ready.

## Out of scope
Tests, Allure on Pages, the autopilot mobile app, new pages.

---

# Track 4 — seeded defects aligned with the real bug reports

## Goal
Track 3 seeded the defects from checklist rows, without the bug reports themselves. The reports
are now read: 98 of them, SSI-3…SSI-62 and SSI-65…SSI-102 (SSI-63 and SSI-64 are later finds and
out of this track). Track 4 makes every seeded defect behave as its report describes, gives the
order-form defects their SSI numbers, and seeds the real bugs that were written off as "skipped".
Afterwards the README line "seeded defects reproduce bugs from my bug reports" is true as is.

Sources (never committed): `web-order-status.md` (SSI-3…28, SSI-95), `web-order-form.md`
(SSI-65…94), `api.md` (SSI-29…62), `mobile.md` (SSI-96…102, no mobile app on the stand).
Reading a report: **Expected result** is the stand's default behaviour, **Actual result** is what
happens with the flag on.

## Ground rules (as in tracks 2 and 3)
- Branch `feat/defects-by-reports`, draft PR into `main`, merge only by Sasha. Stage 0 is this
  section plus questions; then stage by stage, each ending with a report (done / how to check by
  hand / deviations from PLAN.md as a separate list / CI result on the PR) and a stop.
- PR events are only reported; nothing is fixed or pushed without Sasha's OK.
- `tests/` is Sasha's: not edited, not extended.
- Defects leave no marker in the markup or the scripts (track 2 mechanism). An unknown flag still
  blocks the start; the old names of renamed flags become unknown.
- English everywhere; texts in `strings.py` and templates. Verification scripts live outside the
  repo; the UI is checked with Selenium: Chrome always, Firefox where stated.

## Stage 1 — Order status page and header (SSI-3…SSI-28)

| Was | Becomes | Bug | With the flag |
|---|---|---|---|
| `BUG_HEADER_SEARCH_PLACEHOLDER` (origin SSI-4) | same name, origin **SSI-3** | SSI-3 | unchanged: the placeholder reads "Enter order number" |
| — | `BUG_HEADER_SEARCH_EXTRA_BUTTON` | SSI-4 | a "Go!" button (`header-status-go-button`) appears to the right of the header "Order Number" field. **By default the button no longer exists**; the search starts on Enter |
| `BUG_STATUS_SEARCH_ENTER` | unchanged | SSI-5 | Enter does nothing; the description loses "Go! still works" |
| `BUG_TRACK_NO_IMAGE` | `BUG_TRACK_IMAGE_NO_RUNWAY` | SSI-6 | the picture stays (shuttle, two wings and smoke on the plain background); the whole runway is gone: tarmac, edge line, marking, skid marks |
| `BUG_ORDER_HOVER_VULPTEX` | same name | SSI-7 | Firefox only: the header "Order" does **not change colour at all** on hover (checked in Chrome and Firefox) |
| `BUG_TRACK_PERIOD_GROUP` | `BUG_TRACK_DATE_LABEL` | SSI-12 | on `/track` the date row is captioned "Delivery Date" instead of "When to Bring the Shuttle"; order and groups are right |
| `BUG_TRACK_DATE_MINUS_DAY` | `BUG_TRACK_DATE_PLUS_DAY` | SSI-13 | the date on `/track` is one day **later** than ordered; the API is right |
| `BUG_TRACK_EMPTY_COLOR` | same name | SSI-14 | no colour → "Shuttle Color" reads `any` (was `null`) |
| `BUG_TRACK_EMPTY_COMMENT` | same name | SSI-15 | no comment → the "Comment for Autopilot" row is **absent**, caption and value (was `undefined`) |
| — | `BUG_TRACK_AUTOPILOT_NAME_TRUNCATED` | SSI-18 | in "Autopilot {name} is heading towards you" a name of 10+ characters is cut to its first two plus an ellipsis; without the flag it is shown in full |
| — | `BUG_TRACK_CANCEL_HIDDEN_ON_ACCEPT` | SSI-24 | once an autopilot has accepted the order, "Cancel order" is gone from the page; without the flag it stays, disabled (track 3) |
| `BUG_DELAYED_ONE_DAY_LATE` | `BUG_DELAYED_ONE_DAY_EARLY` | SSI-27 | an undelivered order is `delayed` a day **early**: from 00:00 of the delivery day (API and page) |
| `BUG_ENDED_STATUS_4_ACTIVE` | `BUG_ENDED_STATUS_4_CAPTION` | SSI-28 | after the rental has ended the caption of status 4 becomes the next status's text, "Rental time has ended"; the highlighting is right |

Unchanged: SSI-5, 10, 16, 19, 21/22, 25, 26.

Not seeded after this stage: SSI-8, 9, 11, 17, 20, 23 (pixel-level layout) and SSI-95 (the
"There is no such order" flash on refresh is a race; a flag cannot reproduce it honestly). The
rows for SSI-3, SSI-18 and SSI-24 leave the table: "the check was SKIPPED: nothing to reproduce"
was a mistake.

Implementation notes:
- The "Go!" button, the runway, the comment row and "Cancel order" are chosen in Python and
  rendered or not; the header form submits on Enter without a submit button (one text field).
- The runway (one group) has its own testid, `track-not-found-runway`, so its absence is checkable
  the same way a missing element always is on the stand.
- Header "Go!": Sasha's tests do not use it, so it is removed by default.

## Decisions (track 4)
| Topic | Decision | Why |
|---|---|---|
| Header "Go!" | gone by default; only `BUG_HEADER_SEARCH_EXTRA_BUTTON` brings it back | SSI-4: the field has no buttons |
| Caption of status 4 | "Until the rental is over" before the flight; "Rental ends on <day> at <time>" while current **and** once passed (gray) | SSI-28 and Web 6.2: the caption must not change when the rental ends |
| "Cancel order" after accept | stays visible and disabled (track 3); the flag removes it | SSI-24: the button must still be shown |
| Long autopilot name | "long" is 10+ characters; cut to two characters plus "…" (one character), only in the status 2 title | the rule allows 2–10, so one flag is enough to see SSI-18 |
| Runway testid | `track-not-found-runway` on the group with everything that draws the runway | SSI-6 would otherwise be visible on a screenshot only |
| SSI-80…SSI-94 | nine flags (table in stage 2); SSI-87, 90, 93 not seeded | Sasha's choice from the stage 0 proposal |
| Defects not from reports | `BUG_MISSING_NAME_409`, `BUG_LOGIN_NO_PASSWORD_504` (training stand), `BUG_FORM_ERROR_LAYOUT_SHIFT`, `BUG_ADD_BUTTON_STALE_TOTAL` (new) stay with their Origin; the README gives the number of defects that reproduce reports | no "all defects come from bug reports" claim |
| Year | the README says 2023 everywhere; dates inside the reports are test data | Sasha |
| SSI-39 body | `{"code": 500, "message": "operator does not exist: character varying = boolean"}` | as the report shows it |
| `BUG_FORM_DATE_PAST` and `delayed` | an order for a past date is `delayed` from the moment it is created; one README line | follows from the status rule |

## Stage 2 — Order form (SSI-65…SSI-94)

| Was | Becomes | Bug | With the flag |
|---|---|---|---|
| — | `BUG_FORM_CONFIRM_YES_DEAD` | SSI-65 | "Yes" in "Do you want to place the order?" does not respond: no order from the form. `POST /api/v1/orders` works as usual |
| `BUG_FORM_NAME_DASH` | same | SSI-66 | unchanged |
| `BUG_FORM_LAST_NAME_16` | same | SSI-67 | unchanged |
| `BUG_FORM_ADDRESS_REQUIRED` | same | SSI-68 | unchanged |
| `BUG_FORM_ADDRESS_50` | same | SSI-69 | unchanged |
| `BUG_FORM_PHONE_12` | `BUG_FORM_PHONE_10` | SSI-70 | a Phone of 10 characters (`1234567891`) is rejected; 11 and 12 pass |
| — | `BUG_FORM_PHONE_13` | SSI-71 | a Phone of 13 characters (`1234567891011`) is accepted; 14 is not |
| `BUG_FORM_COMMENT_CHARSET` | same | SSI-72, 73, 74 | unchanged |
| `BUG_FORM_COMMENT_LENGTH` | same | SSI-75 | unchanged |
| `BUG_FORM_DATE_TODAY` | `BUG_FORM_DATE_PAST` | SSI-76 | today and any past date can be picked, typed and sent to the API |

The Origin of these flags becomes their SSI numbers instead of "Field Validation 2023".

Not seeded, with reasons:

| Bug | Why not |
|---|---|
| SSI-77 confirmation window, SSI-78 typed date, SSI-79 both colours | by design on the stand: bugs in the original product, accepted decisions of tracks 1–2 (SSI-77 was itself resolved as "kept and added to the requirements") |

SSI-80…SSI-94 (highlighting, colours, calendar, alignment), one by one. Sasha's decision
after stage 0: nine flags, three bugs not seeded.

| Bug | What the flag does | Cost | Decision |
|---|---|---|---|
| SSI-80 | after a day is picked in the calendar the date field loses focus, so it is not blue | 1 JS line | seed: `BUG_FORM_DATE_PICK_NO_HIGHLIGHT` |
| SSI-81 | "Shuttle Station" turns blue under the pointer | 1 CSS rule | seed: `BUG_FORM_STATION_HOVER` |
| SSI-82…85 | Name, Last Name, Address, Phone: the border turns black as soon as anything is typed, valid or not | 1 CSS rule (`:focus:not(:placeholder-shown)`) | seed as one flag: `BUG_FORM_TYPING_BORDER` |
| SSI-86 | the step-1 button reads "Continue" | 1 string | seed: `BUG_FORM_NEXT_LABEL` |
| SSI-87 | colour and comment content shifted left of the fields above | pixel-level alignment | not seeded |
| SSI-88 | the "Shuttle Station" placeholder is dark gray | 1 CSS rule | seed: `BUG_FORM_STATION_PLACEHOLDER_DARK` |
| SSI-89 | with one colour ticked, the text of the other turns black | 1 CSS rule | seed: `BUG_FORM_COLOR_UNTICKED_BLACK` |
| SSI-90 | the calendar opens in the middle of the field | pixel-level position | not seeded |
| SSI-91 | month and weekday names in lowercase ("august", "mo") | 2 JS lines | seed: `BUG_FORM_CALENDAR_LOWERCASE` |
| SSI-92 | weekday names and weekends in the calendar are black | 1 CSS rule | seed: `BUG_FORM_CALENDAR_BLACK` |
| SSI-93 | centred month label, light arrows on both sides, an extra "up" arrow | three layout details in one report; doable in CSS, checkable only by geometry | not seeded |
| SSI-94 | the "Rental Period" list is narrower than the field | 1 CSS rule, checkable by comparing widths | seed: `BUG_FORM_PERIOD_LIST_NARROW` |

## Stage 3 — API, README, finish
- API: the autopilot rule flags do not change, with one fix. `login: true` with
  `BUG_AUTOPILOT_LOGIN_RULES` must answer `500` with the body
  `{"code": 500, "message": "operator does not exist: character varying = boolean"}` (SSI-39),
  and `400` without the flag. Today the status is right but the body is the stand's own
  `{"ok": false, "message": "Internal server error"}`: it is replaced for this one case.
- README, Known defects: the table, the defect count wherever it is a number, the Origin legend,
  the "Environments" paragraph, the "Not seeded" tables. Mobile SSI-96…SSI-102 in one line: there
  is no mobile app on the stand.
- PLAN.md: the final "flag → SSI" table in this section.
- Regression with every flag off, then every changed and new flag on its own. CI green → PR
  ready → report and stop.

## Result: flag → SSI
45 flags; 41 reproduce bug reports (78 of the 98 reports), 4 have another origin.

| Flag | Origin |
|---|---|
| `BUG_AUTOPILOT_LOGIN_RULES` | SSI-29…SSI-40 |
| `BUG_AUTOPILOT_PASSWORD_RULES` | SSI-41…SSI-50 |
| `BUG_AUTOPILOT_NAME_RULES` | SSI-51…SSI-61 |
| `BUG_TRACK_DELETED_AUTOPILOT` | SSI-62 |
| `BUG_HEADER_SEARCH_PLACEHOLDER` | SSI-3 |
| `BUG_HEADER_SEARCH_EXTRA_BUTTON` | SSI-4 |
| `BUG_STATUS_SEARCH_ENTER` | SSI-5 |
| `BUG_TRACK_IMAGE_NO_RUNWAY` | SSI-6 |
| `BUG_ORDER_HOVER_VULPTEX` | SSI-7 |
| `BUG_TRACK_WRONG_STATION` | SSI-10 |
| `BUG_TRACK_DATE_LABEL` | SSI-12 |
| `BUG_TRACK_DATE_PLUS_DAY` | SSI-13 |
| `BUG_TRACK_EMPTY_COLOR` | SSI-14 |
| `BUG_TRACK_EMPTY_COMMENT` | SSI-15 |
| `BUG_TRACK_NO_WRAP` | SSI-16 |
| `BUG_TRACK_AUTOPILOT_NAME_TRUNCATED` | SSI-18 |
| `BUG_STATUS_ON_SITE_SKIPPED` | SSI-19 |
| `BUG_CANCELED_MODAL_FULLSCREEN` | SSI-21, SSI-22 |
| `BUG_TRACK_CANCEL_HIDDEN_ON_ACCEPT` | SSI-24 |
| `BUG_CANCELED_ORDER_VISIBLE` | SSI-25, SSI-26 |
| `BUG_DELAYED_ONE_DAY_EARLY` | SSI-27 |
| `BUG_ENDED_STATUS_4_CAPTION` | SSI-28 |
| `BUG_FORM_CONFIRM_YES_DEAD` | SSI-65 |
| `BUG_FORM_NAME_DASH` | SSI-66 |
| `BUG_FORM_LAST_NAME_16` | SSI-67 |
| `BUG_FORM_ADDRESS_REQUIRED` | SSI-68 |
| `BUG_FORM_ADDRESS_50` | SSI-69 |
| `BUG_FORM_PHONE_10` | SSI-70 |
| `BUG_FORM_PHONE_13` | SSI-71 |
| `BUG_FORM_COMMENT_CHARSET` | SSI-72, SSI-73, SSI-74 |
| `BUG_FORM_COMMENT_LENGTH` | SSI-75 |
| `BUG_FORM_DATE_PAST` | SSI-76 |
| `BUG_FORM_DATE_PICK_NO_HIGHLIGHT` | SSI-80 |
| `BUG_FORM_STATION_HOVER` | SSI-81 |
| `BUG_FORM_TYPING_BORDER` | SSI-82…SSI-85 |
| `BUG_FORM_NEXT_LABEL` | SSI-86 |
| `BUG_FORM_STATION_PLACEHOLDER_DARK` | SSI-88 |
| `BUG_FORM_COLOR_UNTICKED_BLACK` | SSI-89 |
| `BUG_FORM_CALENDAR_LOWERCASE` | SSI-91 |
| `BUG_FORM_CALENDAR_BLACK` | SSI-92 |
| `BUG_FORM_PERIOD_LIST_NARROW` | SSI-94 |
| `BUG_MISSING_NAME_409` | training stand |
| `BUG_LOGIN_NO_PASSWORD_504` | training stand |
| `BUG_FORM_ERROR_LAYOUT_SHIFT` | new |
| `BUG_ADD_BUTTON_STALE_TOTAL` | new |

Not seeded (20 reports): SSI-8, 9, 11, 17, 20, 23, 87, 90, 93 (pixel-level layout) · SSI-95 (a
race) · SSI-77, 78, 79 (by design on the stand) · SSI-96…SSI-102 (no mobile app).

Deviations accepted along the way: `BUG_FORM_DATE_PAST` goes back to 01.01.1000 (the form takes a
four-digit year); with `BUG_FORM_STATION_HOVER` the hover colour also covers an error border.

## Out of scope
Tests; SSI-63 and SSI-64; the mobile app; publishing the bug reports in the repository.

---

# Bug reports published

The 98 bug reports SSI-3…SSI-102 are in `docs/bug-reports/`: an index and four files by area
(Web order status, Web order form, API, mobile app). The texts are Sasha's, an adaptation of his
2023 reports that he proofread; they went in as they were. The only addition is an
`<a id="ssi-N"></a>` anchor before each report, so `docs/bug-reports/api.md#ssi-39` opens that
report. In the README every SSI number in the Known defects tables links to its report (a range
links to its first one), and the index says that 78 of the 98 are seeded by flags.

Out of scope: screenshots and recordings attached to the reports, the checklists and the mind
map, any change to the application or the tests.
