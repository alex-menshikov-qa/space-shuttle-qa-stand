# space-shuttle-qa-stand

[![CI](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml)
[![Allure report](https://img.shields.io/badge/Allure-report-blue)](https://alex-menshikov-qa.github.io/space-shuttle-qa-stand/)

**A portfolio test stand, not a production service.** It is a small web app with a JSON API and a
PostgreSQL database, built to be tested: my automation suites in `tests/` (pytest, Selenium,
Requests, Allure) run against it in CI instead of third-party training stands. It has stable
locators, a documented contract, a seeded test user, and 48 switchable
[known defects](docs/defects.md#known-defects) for the tests to catch; 41 of them reproduce bugs from my bug reports.

The story: **Space Shuttle Inc** rents shuttles on Coruscant. A shuttle flies to the customer by
itself, steered by its autopilot, a droid employee who takes orders through the API. At the Shipyard
a customer builds a shuttle from parts. The stand has a rental landing, an order form, order
tracking, a shuttle builder, and a JSON API for all of it.

**Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, PostgreSQL 16, argon2,
JWT, server-rendered Jinja2 + vanilla JS, Docker Compose, GitHub Actions.

## How this stand was built

The stand is my design and Claude Code's implementation.

**Where the requirements come from.** From my own work: the behavior my existing test suites
expected, and the manual test documentation I wrote in 2023 for Space Shuttle Inc, a fictional
product I built my QA portfolio around (a mind map of the order form, UI and API checklists, a
field-validation table, and [the bug reports SSI-3…SSI-102](docs/bug-reports/)). 41 of the 48 seeded defects reproduce
bugs from those bug reports; I had found them by hand in the training applications the
documentation grew out of.

**What Claude Code did.** It wrote the application, the database schema and migrations, the Docker
setup, and the CI workflow, stage by stage, to those requirements. Its commits are authored as
Claude. The plans it worked from, with the decisions made along the way, are in
[`docs/PLAN.md`](docs/PLAN.md).

**What I did.** I made the product decisions: the storyline, what the stand keeps from the 2023
documentation, and which bugs become seeded defects. Every stage was reviewed before merge (the
stage report, an independent AI review of the diff, and checks on the running stand), and I merged
each pull request myself. Two bugs I later found on the stand as a user are in the backlog as new
bug reports.

**What is only mine.** Everything in `tests/`. I moved the suites here from my earlier repos myself,
with Claude as a reviewer; Claude Code does not write tests in this repository.

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

- the test user from `TEST_NAME` / `TEST_EMAIL` / `TEST_PASSWORD` (the tests read `TEST_EMAIL` and `TEST_PASSWORD`);
- the eight Coruscant stations from `app/data/stations.json`;
- the shipyard catalog of 16 parts from `app/data/shipyard_parts.json`;
- the fleet of nine autopilots from `app/data/fleet.json` (`ilves`, `pupu`, `kissa`, `kettu`, `karhu`,
  `pollo`, `siili`, `orava`, `hirvi`), all with the password `FLEET_PASSWORD`.

If a test deletes the test user or a fleet autopilot, a restart (`docker compose restart app`) brings it back.
The seed creates no rental orders: a fresh stand (after `docker compose down -v`) has none, so a paging
test creates the orders it needs.

## Environment variables

One `.env` (copied from `.env.example`, which holds fake values only) feeds both the stand and the tests.
`.env` is git-ignored.

| Variable | Used by | Meaning |
|---|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | stand, manual SQL checks | Database credentials (avoid `@ : / #` in the password: it goes into a URL) |
| `POSTGRES_PORT` | stand, manual SQL checks | Host port the database is published on |
| `DB_HOST` | manual SQL checks | Database host for SQL checks (`localhost`) |
| `APP_PORT` | stand | Host port the app is published on |
| `BASE_URL` | tests | Stand URL; keep it in sync with `APP_PORT` |
| `JWT_SECRET` | stand | HS256 key for access tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | stand | Token and session lifetime (default 60) |
| `TEST_NAME` | stand | Name of the seeded test user |
| `TEST_EMAIL`, `TEST_PASSWORD` | stand, tests | Email and password of the seeded test user |
| `FLEET_PASSWORD` | stand | Password of the seeded fleet autopilots, exactly 4 digits (default `0101`) |
| `STAND_TZ` | stand | Time zone in which the stand counts days (default `UTC`) |
| `PICKUP_MINUTES` | stand | Minutes from "Autopilot is on site" to "Okay, let's fly now" (default 10) |
| `TEST_HOOKS` | stand | `1` switches on `/api/v1/testing/*` (default off; CI switches it on) |
| `BUG_<NAME>` | stand, tests | Switches a seeded defect on (see [Known defects](docs/defects.md#known-defects)); `tests/api/api_data.py` reads the flags for the conditional `xfail` |

The app gets `DATABASE_URL` from `docker-compose.yml`, assembled from the `POSTGRES_*` variables.

## Tests

The suites live in this repo, next to the stand: 50 tests in three suites, moved here from my
earlier repos.

```
tests/
  ui/               shipyard suite, 17 tests: registration, login, logout, account, shipyard tabs (Chrome)
    add/            its config (reads .env), locators and helpers
    rental/         rental suite, 12 tests: FAQ, order form, header logos (Firefox, Page Object)
      pages/        page objects
      locators/     their locators
  api/              API suite, 21 tests: autopilot registration and login, orders (requests)
  requirements.txt  pinned test dependencies
pytest.ini          test paths, markers, Allure results directory
```

Every test module is marked with its suite's marker from `pytest.ini`: `ui` or `api`. So
`pytest -m ui` runs both UI suites and `pytest -m api` the API suite; a path selects a single suite.

### Running the tests locally

Requires Docker with Compose v2, Python 3.12+, Chrome and Firefox. All commands run from the repo root.

1. Start the stand in Docker (see [Quick start](#quick-start) for `.env`):

   ```bash
   docker compose up -d --build --wait
   ```

2. Create and activate a virtual environment in the repo root (`.venv` is in `.gitignore`).

   Linux / macOS:

   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   ```

   Windows (PowerShell):

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install the dependencies and run the tests:

   ```bash
   pip install -r tests/requirements.txt
   pytest                                    # everything, 50 tests
   pytest tests/api                          # API suite, 21
   pytest tests/ui                           # both UI suites, 29
   pytest tests/ui --ignore=tests/ui/rental  # shipyard suite only, 17
   pytest tests/ui/rental                    # rental suite only, 12
   allure serve allure-results               # optional, needs the Allure CLI locally
   ```

The tests read the stand's `.env` by themselves, so there is nothing to export:
`tests/ui/add/config.py` (`BASE_URL`, `TEST_EMAIL`, `TEST_PASSWORD`), `tests/ui/rental/data.py`
(`BASE_URL`) and `tests/api/api_data.py` (`BASE_URL` and the `BUG_*` flags) load it with
python-dotenv. A variable already set in the environment wins over `.env`. Without `BASE_URL` the
suites use `http://localhost:8000`. To test another stand, change `BASE_URL`.

**If the stand is not reachable**, every suite is skipped with a reason instead of failing: the
shipyard `driver` fixture opens `BASE_URL` first, and the rental and API suites each have a
session-scoped autouse fixture that calls `GET /health`.

On Windows, if `app` exits with `exec app/entrypoint.sh: no such file or directory`, the clone
predates `.gitattributes` and the script has CRLF line endings. Restore it and rebuild:

```powershell
git rm --cached app/entrypoint.sh
git reset --hard
docker compose up -d --build --wait
```

**Browsers.** Each UI suite has its own browser, set in its `conftest.py`; there is no switch
such as a `BROWSER` variable:

- the shipyard suite runs Chrome. Locally Chrome opens a window; with the `CI` environment variable
  set (GitHub Actions sets it) it runs headless (`--headless=new`);
- the rental suite runs Firefox, always headless (`--headless`), locally too.

Selenium ≥ 4.6 includes Selenium Manager: it finds the installed Chrome and Firefox and matching
drivers, downloading a driver on first use if needed, so there is nothing to install by hand.

**xfail and seeded defects.** Two API tests check behaviour that a seeded defect breaks:
`test_login_without_password` (`BUG_LOGIN_NO_PASSWORD_504`) and
`test_create_autopilot_without_first_name` (`BUG_MISSING_NAME_409`). Each is marked `xfail` only
when its flag is on in the tests' environment (read from the same `.env` as the stand, so restart
the stand after changing it), with `strict=True` and `raises=AssertionError`: only a failed assertion
counts as the expected failure, and a pass with the flag on fails the test. With no `BUG_*` flags
every test must pass.

**SQL checks.** No suite connects to the database yet. The stand publishes it on `POSTGRES_PORT`
so that such checks can connect to `DB_HOST:POSTGRES_PORT` with the `POSTGRES_*` credentials,
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
7. On `main` only (pushes and manual runs, never pull requests): the same report is published to
   GitHub Pages by the `publish-report` job
8. On failure: `docker compose logs`; always: `docker compose down -v`

**The latest report from `main`:** https://alex-menshikov-qa.github.io/space-shuttle-qa-stand/

- It is published when tests fail too; a run that produced no test results at all (the stand
  did not start) leaves the previous report in place.
- Trend and history: before generating, CI copies `history/` from the published report into
  `allure-results`, so each report continues the previous one. The first published run has no trend.
- Pages must be set to deploy from Actions: **Settings → Pages → Build and deployment → Source:
  GitHub Actions**.

## Project layout

```
app/                FastAPI app
  api/              /health and the JSON API (/api/v1)
  web/              server-rendered pages and the cookie session
  services/         business logic shared by API and pages
  templates/        Jinja2 templates
  static/           CSS and page scripts
  data/             story data as JSON (FAQ, stations, fleet, shipyard parts): edit names and texts here, not in code
  clock.py          stand time zone and the per-order clock
  migrations/       Alembic migrations
  strings.py        every user-visible text
  validation.py     field rules shared by API, forms and JS
  defects.py        seeded-defect flags
tests/              test suites (see above)
docker-compose.yml  db + app
```

## Documentation

- [API](docs/api.md) — the JSON API contract: accounts, autopilots, stations, orders, the Shipyard, time shift, validation rules.
- [UI](docs/ui-spec.md) — the site map, the pages, their states and the locator table.
- [Known defects](docs/defects.md) — the 48 `BUG_*` flags, the bug reports that are not seeded, environments.
- [Bug reports](docs/bug-reports/) — SSI-3…SSI-102, my manual bug reports.
- [Development log](docs/PLAN.md) — the plans Claude Code worked from and the decisions made along the way.
