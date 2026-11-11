# space-shuttle-qa-stand

[![CI](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml)

**A portfolio test stand, not a production service.** It is a small web app with a JSON API,
built to be tested: the API and UI automation suites (pytest + Requests / Selenium / Allure)
run against it instead of third-party training stands. It has stable locators, a documented
contract, a seeded test user and switchable "known defects" for the tests to catch.

The story: **Space Shuttle Inc** rents shuttles on Coruscant. A shuttle flies to the customer by
itself, steered by its autopilot. The story is being added stage by stage (see `PLAN.md`, Track 2):
the landing, the re-skin and the autopilot / station / order API are in; the order form, order
tracking and the shipyard builder come next.

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

On every start the stand applies migrations and seeds, idempotently:

- the test user from `TEST_NAME` / `TEST_EMAIL` / `TEST_PASSWORD` (the same variables the tests read);
- the eight Coruscant stations from `app/data/stations.json`;
- the fleet of nine autopilots from `app/data/fleet.json` (`ilves`, `pupu`, `kissa`, `kettu`, `karhu`,
  `pollo`, `siili`, `orava`, `hirvi`), all with the password `FLEET_PASSWORD`.

If a test deletes the test user or a fleet autopilot, a restart (`docker compose restart app`) brings it back.

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
| `FLEET_PASSWORD` | stand, tests | Password of the seeded fleet autopilots, exactly 4 digits (default `0101`) |
| `STAND_TZ` | stand | Time zone in which the stand counts days (default `UTC`) |
| `PICKUP_MINUTES` | stand | Minutes from "Autopilot is on site" to "Okay, let's fly now" (default 10) |
| `TEST_HOOKS` | stand | `1` switches on `/api/v1/testing/*` (default off; CI switches it on) |
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

## Autopilot, station and order API

Same base path and error body. Autopilots are droid employees, a separate entity from web
accounts: no tokens. Bodies are checked by the stand's own rules, so a missing field, `null`
or a number where a string is expected all give the `400` below.

| Endpoint | Success | Errors |
|---|---|---|
| `POST /autopilot` `{login, password, firstName}` | `201 {"ok": true}` | `400` "Insufficient data to create an account" (a field is missing or breaks its rule) · `409` "This login is already in use. Please try another one" |
| `POST /autopilot/login` `{login, password}` | `200 {"id": <int>}` | `400` "Insufficient data to log in" · `404` "Account not found" (wrong pair or unknown login) |
| `DELETE /autopilot/{id}` | `200 {"ok": true}` | `400` "Insufficient data to delete the autopilot" (no id) · `404` "There is no autopilot with such id" (also for a non-numeric id) |
| `GET /stations/search?s=` | `200 {"stations": [{number, name, color}]}` — names containing `s`, case-insensitive, from 1 character; without `s` all stations | — |
| `POST /orders` | `201 {"track": <int>}` | `400` with the message of the first invalid field |
| `GET /orders[?autopilotId=]` | `200 {"orders": [...]}` — all orders, or those accepted by the autopilot | `404` "Autopilot with identifier {autopilotId} not found" |
| `GET /orders/track?t=` | `200 {"order": {...}}` | `400` "Insufficient data to perform the search" (no `t`) · `404` "Order not found" |
| `PUT /orders/accept/{id}?autopilotId=` | `200 {"ok": true}` | `400` "Insufficient data to perform the search" · `404` "There is no order with such id" / "There is no autopilot with such id" · `409` "This order is already in progress" |
| `PUT /orders/finish/{id}` | `200 {"ok": true}` | `404` "There is no order with such id" · `409` "This order cannot be finished" (not accepted yet, or already finished) |
| `PUT /orders/cancel` `{track}` | `200 {"ok": true}` | `400` "Insufficient data to perform the search" · `404` "Order not found" · `409` "This order is already in progress" |

`{id}` in accept / finish is the order's `id` (from `GET /orders/track`), not its track number.

**Autopilot rules.** `login` — 2–10 Latin ("Aurebesh") letters; `password` — exactly 4 digits, sent as
a string; `firstName` — 2–10 Latin letters, required. Passwords are stored as argon2id hashes in
`autopilots.password_hash`. Deleting an autopilot frees its login; orders it had accepted are no
longer found by track or listed.

**Order fields.**

| Field | Rule | Message |
|---|---|---|
| `firstName` | Latin letters, space, hyphen; 2–15 | Enter the correct name |
| `lastName` | Latin letters; 2–15 | Enter the correct last name |
| `address` | Latin letters, digits, space, hyphen, dot, comma; 5–50 after trimming | Enter the correct address |
| `station` | number of an existing station (JSON number) | Select a station |
| `phone` | digits and `+`; 10–12 | Enter the correct phone number |
| `deliveryDate` | `YYYY-MM-DD`, not earlier than tomorrow (in `STAND_TZ`) | Enter a valid date |
| `rentTime` | integer 1–7 (days) | Enter a valid rental period |
| `color` | optional; `[]`, `["PINKY_SWEAR"]`, `["GRAY_RAINBOW"]` or both | Enter a valid color |
| `comment` | optional; Latin letters, space, hyphen, dot, comma; up to 24 | Enter a valid comment |

`track` is a random unique 5-digit number. A canceled order is no longer found or listed.

**Order object:** `{id, track, firstName, lastName, address, station: {number, name, color}, phone,
rentTime, deliveryDate, comment, color, status, autopilotId, autopilotFirstName, createdAt,
acceptedAt, finishedAt, rentalEndsAt}`.

**Status** is computed, not stored:

| `status` | When |
|---|---|
| `hangar` | created, not accepted |
| `heading` | accepted by an autopilot |
| `on_site` | finished (the autopilot has arrived) |
| `flying` | `PICKUP_MINUTES` after finish |
| `ended` | `rentTime` days after finish (`rentalEndsAt`) |
| `delayed` | the delivery day is over (after 23:59 in `STAND_TZ`) and the order is not finished; finish brings it to `on_site` |

### Time shift for tests

With `TEST_HOOKS=1` (off by default; without it the path is a `404`):

`POST /api/v1/testing/orders/{track}/time-shift` `{"days": N, "hours": N, "minutes": N}` (any of the
three, numbers) → `200 {"order": {...}}`; `400` for a body without usable numbers, `404` "Order not found".

Every order has its own clock. The call moves that clock forward (shifts add up), so `delayed`,
`flying` and `ended` are reachable without waiting, and no other order or date check is affected.
For example: finish an order, shift it by `{"minutes": 10}` → `flying`; by `{"days": 7}` more → `ended`.

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
| `/` | Rental landing: title and pitch, FAQ accordion of 8 questions (one answer open at a time), a second **Order** button at the bottom → `/order`, cookie banner with **Got it** (not shown again once accepted). |
| `/holonet` | Partner stub page (HoloNet news); the header mark opens it in a new tab. |
| `/shipyard` | Placeholder for the future builder. Guest: **Sign in** button → `/login`. Logged in: **Place order** button (no action yet). |
| `/order`, `/track` | Placeholders until the order form and order tracking arrive. |
| `/register` | Name, Email, Password, **Sign up**; "Already registered? **Sign in**" → `/login`. Success → `/login` (no auto-login). |
| `/login` | Email, Password, **Sign in**; **Sign up** → `/register`; **Forgot password?** → `/forgot-password`. Success → `/shipyard`. |
| `/forgot-password` | Email + **Recover** → success message (no email is actually sent); "Remembered your password? **Sign in**" → `/login`. |
| `/account` | Logged-in only (guests are redirected to `/login`): name, email, **Log out** → `/login`. |

Header on every page:

- logo "Space **Shuttle** Inc": "Space Shuttle" links to `/`, "Inc" is plain text and leads nowhere;
- partner mark **HoloNet** → `/holonet` in a **new tab**;
- **Shipyard** → `/shipyard`; **Order** → `/order`;
- **Order Status** reveals the **Order Number** field and **Go!**; the button or Enter → `/track?t=<number>`;
- **Account** → `/login` for guests, `/account` when logged in.

There are exactly four entry points to `/login`: the **Sign in** button on `/shipyard`, header **Account**,
the link on `/register` and the link on `/forgot-password`.

An unknown path gets an HTML 404 page with the header and a link home; under `/api/` a 404 stays JSON.

The cookie banner (home page only) is fixed to the bottom of the window. Until it is accepted it
covers whatever is under it, including the lower **Order** button when that is scrolled to the
bottom edge. Acceptance is remembered in the `cookies_accepted` cookie.

FAQ elements also have fixed ids: `accordion__heading-N` (question) and `accordion__panel-N` (answer), N = 0…7.
Texts live in `app/data/faq.json`.

The session is an httpOnly cookie `access_token` holding the same JWT the API issues.
Forms have `novalidate` and no `maxlength`: every error is our own DOM element under the field.

### Locators

Every interactive element and every message has a `data-testid` (form controls also have the same `id`).
Pattern: `<page>-<element>-<kind>`.

| Page | `data-testid` |
|---|---|
| every page | `header-logo-link`, `header-logo-inc`, `header-holonet-link`, `header-shipyard-link`, `header-order-button`, `header-status-button`, `header-status-form`, `header-status-input`, `header-status-go-button`, `header-account-link`, `<page>-page` on `<main>`, `<page>-title` on `<h1>` |
| `/` | `home-pitch`, `home-faq-title`, `home-faq`, `home-faq-question-N`, `home-faq-answer-N` (N = 0…7), `home-order-button`, `home-cookie-banner`, `home-cookie-text`, `home-cookie-accept-button` |
| `/holonet` | `holonet-intro`, `holonet-news`, `holonet-news-item-N` |
| `/shipyard` | `shipyard-sign-in-button`, `shipyard-order-button`, `shipyard-builder-placeholder` |
| `/order`, `/track` | `order-placeholder`, `track-placeholder` (temporary) |
| 404 | `not-found-message`, `not-found-home-link` |
| `/register` | `register-form`, `register-name-input`, `register-name-error`, `register-email-input`, `register-email-error`, `register-password-input`, `register-password-error`, `register-submit-button`, `register-login-link` |
| `/login` | `login-form`, `login-form-error`, `login-email-input`, `login-email-error`, `login-password-input`, `login-password-error`, `login-submit-button`, `login-register-link`, `login-forgot-password-link` |
| `/forgot-password` | `forgot-password-form`, `forgot-password-email-input`, `forgot-password-email-error`, `forgot-password-submit-button`, `forgot-password-success-message`, `forgot-password-login-link` |
| `/account` | `account-name`, `account-email`, `account-logout-form`, `account-logout-button` |

Error elements are always in the DOM and `hidden` while empty: check visibility, not presence.
The same goes for the header search form and the FAQ answers.

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
e.g. to assert that `users.password_hash` and `autopilots.password_hash` hold an argon2id hash,
not the password.

## CI

`.github/workflows/ci.yml` runs on pushes to `main`, on pull requests and manually
(**Run workflow** in the Actions tab):

1. `.env` from `.env.example` with `TEST_HOOKS=1`, exported to the job environment
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
  services/         business logic shared by API and pages
  templates/        Jinja2 templates
  static/           CSS and page scripts
  data/             story data as JSON (FAQ, stations, fleet): edit names and texts here, not in code
  clock.py          stand time zone and the per-order clock
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
