# space-shuttle-qa-stand

[![CI](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml/badge.svg)](https://github.com/alex-menshikov-qa/space-shuttle-qa-stand/actions/workflows/ci.yml)

**A portfolio test stand, not a production service.** It is a small web app with a JSON API,
built to be tested: the API and UI automation suites (pytest + Requests / Selenium / Allure)
run against it instead of third-party training stands. It has stable locators, a documented
contract, a seeded test user and switchable "known defects" for the tests to catch.

The story: **Space Shuttle Inc** rents shuttles on Coruscant. A shuttle flies to the customer by
itself, steered by its autopilot — a droid employee who takes orders through the API. At the
Shipyard a customer builds a shuttle from parts. The stand has a rental landing, an order form,
order tracking, a shuttle builder, a JSON API for all of it, and nine switchable
[known defects](#known-defects). How it was planned: `PLAN.md`.

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
- the shipyard catalog of 16 parts from `app/data/shipyard_parts.json`;
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

## Shipyard API

| Endpoint | Success | Errors |
|---|---|---|
| `GET /shipyard/parts` | `200 {"parts": [{id, category, name, price, description, mass, power, cargo, comfort}]}` — the catalog in display order; `category` is `hull`, `engine` or `module` | — |
| `POST /shipyard/orders` (Bearer token of a web account) `{"parts": [id, ...]}` | `201 {"number": <int>, "total": <int>}` | `401` no / bad token · `400` "A shuttle needs a hull" · "A shuttle can have only one hull" · "Unknown part: {id}" · "Field 'parts' must be a list of part ids" |
| `GET /shipyard/orders` (Bearer token) | `200 {"orders": [{number, total, createdAt, parts: [{id, category, name, price}]}]}` — the account's own build orders | `401` |

A build is exactly one hull plus any number of engines and modules, in build order; a part may
repeat. The server computes `total` from its own prices and ignores anything else in the body;
the hull counts **twice** (top and belly plating). `number` is a random unique 6-digit number.
A build order is not a rental: it has nothing to do with `/orders` and `/track`. Order items keep
the name and price the part had when ordered.

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

### Site map

```
/                    rental landing: pitch, FAQ, Order, cookie banner
├── /order           order form, two steps        → /track?t=<number>
├── /track?t=        order status, search, cancel
├── /shipyard        shuttle builder              → /login (guest)
├── /holonet         partner stub (opens in a new tab)
├── /login           → /shipyard on success       ← /shipyard, header, /register, /forgot-password
├── /register        → /login on success
├── /forgot-password
├── /account         logged-in only, otherwise → /login
├── /docs            Swagger UI
├── /health
└── anything else    HTML 404 (JSON under /api/)
```

| Page | What it does |
|---|---|
| `/` | Rental landing: title and pitch, FAQ accordion of 8 questions (one answer open at a time), a second **Order** button at the bottom → `/order`, cookie banner with **Got it** (not shown again once accepted). |
| `/holonet` | Partner stub page (HoloNet news); the header mark opens it in a new tab. |
| `/shipyard` | Shuttle builder (see [Shipyard](#shipyard)). Guest: **Sign in** → `/login`. Logged in: **Order this shuttle**. |
| `/order` | Order form in two steps (see [Order form](#order-form)). A direct URL always opens step 1. |
| `/track?t=<number>` | Order status (see [Order status](#order-status)): own search row, order data, status chain, **Cancel order**. |
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

### Order form

One page, two steps; the page posts to `POST /api/v1/orders`, so the form and the API share the
field rules and messages listed under [Order fields](#autopilot-station-and-order-api).
Placeholders are the field names; required fields start with `*`. An invalid field gets its
message under it and a red border.

**Step 1, "For Whom is the Shuttle":** Name, Last Name, Address, Shuttle Station, Phone, **Next**.
Fields are checked when they lose focus and on **Next**; with errors the form stays on step 1.
The address is trimmed when it loses focus. Shuttle Station is a search: focusing it lists all
stations, typing filters them from the first character (`GET /api/v1/stations/search`), each with a
dot in its line color; a station counts only when picked from the list by click.

**Step 2, "About Rent":**

- **When to Bring the Shuttle** — a date picker that opens on the current month with days before
  tomorrow disabled. The date can also be typed, as `DD.MM.YYYY`; a malformed, non-existent or too
  early date gives "Enter a valid date". "Today" is the stand's (`STAND_TZ`), not the browser's.
- **Rental Period** — a custom dropdown (a `<button>` and a list, not a `<select>`): "one day" … "seven days".
- **Shuttle Color** — checkboxes "pinky swear" and "gray rainbow": both, one or none.
- **Comment for Autopilot** — optional.
- **Back** returns to step 1 with all data kept; **Order** validates step 2.

With no errors **Order** opens the modal "Do you want to place the order?" (**Yes** / **No**).
**Yes** places the order and shows "Order number NNNNN. Write it down: it will come in handy to
track the status" with **View Status** → `/track?t=NNNNN`.

The station list, the date picker and the period list open in the page flow: they push the rest
of the form down and never cover another field.

### Order status

`/track?t=<number>` has three variants: no number (search row only), found, not found (HTTP 404 with
"There is no such order. Are you sure you entered the correct number?"). The search row — the
**Order Number** field and **View**, by click or Enter — is present in all of them.

A found order shows its data in three groups (Name, Last Name, Address, Shuttle Station with its
colored dot, Phone · When to Bring the Shuttle, Rental Period · Shuttle Color, Comment for
Autopilot; an empty comment or color keeps its caption with an empty value) and the status chain:

| # | Title | Caption while current | Caption while not current |
|---|---|---|---|
| 1 | Shuttle in the hangar | Your autopilot is warming up for departure | same |
| 2 | Autopilot <firstName> is heading towards you ("Autopilot is heading towards you" before accept) | Contact number: 0101 | same |
| 3 | Autopilot is on site | Pick up the shuttle and pay the rental fee | same |
| 4 | Okay, let's fly now | Rental ends on <day> at <time> | Until the rental is over |
| 5 | Rental time has ended | <firstName> is heading home to recharge. Thanks for flying with us. | no caption |
| — | Autopilot delayed (red, takes the place of status 2) | We won't be able to deliver the shuttle on time. To check the status of your order, please call support at: 0101 | — |

Every status is an element with `data-state` = `done` / `current` / `upcoming` and
`data-current` = `true` / `false`. The page is rendered on the server: reload it to see a new status.

**Cancel order** is shown until an autopilot accepts the order: modal "Do you want to cancel the
order?" with **Back** (closes the modal, the order stays) and **Cancel** → "Order canceled. Come
back, we are always waiting for you :)" with **Okay** → `/`. A canceled order is no longer found.

### Shipyard

`/shipyard`, title "Build your shuttle": the catalog on the left, the build on the right.

- **Tabs** Hulls / Engines / Modules. A click scrolls the catalog to that section's `<h2>`; scrolling
  the catalog by hand switches the active tab by itself; the first tab is active by default.
  The active tab has the class `tab--active` and `data-active="true"` (the others `data-active="false"`).
  The catalog scrolls inside its own box (`shipyard-catalog`), so the build stays in view.
- **Part card:** picture, price in credits, name, **Add**, and a counter of how many of this part
  are in the build (hidden at 0; a hull counts as 2). A click on the card (not on **Add**) opens a
  modal with the description and Mass, t · Power, MW · Cargo, m³ · Comfort, ★; it closes by the
  cross, Esc or a click on the backdrop.
- **Adding:** drag a card into the build area, or press **Add**. A drop anywhere else adds nothing.
- **Hull:** one per build, a new one replaces the old. It is shown twice — "<name> (Top plating)"
  above and "<name> (Belly plating)" below the other parts — and priced twice. Without a hull the
  build shows "No hull, no shuttle. Drag one here to begin."
- **Engines and modules:** any number. Drag one onto another inside the build to reorder (the
  dragged part takes the place of the one it is dropped on); the cross removes it.
- **Total** is recalculated on every change. The server recomputes it on order.
- **Order this shuttle:** without a hull — "A shuttle needs a hull" and no order; otherwise a modal
  "Build order number NNNNNN" with the total, and the build is cleared. The page posts to the
  cookie-authenticated `POST /shipyard/orders`, which uses the same service as the API.
- The build is kept in `sessionStorage`, so a guest's build survives signing in.

**Dragging is built on mouse events** (`mousedown` / `mousemove` / `mouseup`), not HTML5 Drag and
Drop, so Selenium needs no JavaScript workaround:

```python
ActionChains(driver).click_and_hold(card).move_to_element(build).release().perform()
```

Checked with Selenium in headless Chrome and headless Firefox.

### Locators

Every interactive element and every message has a `data-testid` (form controls also have the same `id`).
Pattern: `<page>-<element>-<kind>`.

| Page | `data-testid` |
|---|---|
| every page | `header-logo-link`, `header-logo-inc`, `header-holonet-link`, `header-shipyard-link`, `header-order-button`, `header-status-button`, `header-status-form`, `header-status-input`, `header-status-go-button`, `header-account-link`, `<page>-page` on `<main>`, `<page>-title` on `<h1>` |
| `/` | `home-pitch`, `home-faq-title`, `home-faq`, `home-faq-question-N`, `home-faq-answer-N` (N = 0…7), `home-order-button`, `home-cookie-banner`, `home-cookie-text`, `home-cookie-accept-button` |
| `/holonet` | `holonet-intro`, `holonet-news`, `holonet-news-item-N` |
| `/shipyard` catalog | `shipyard-tabs`, `shipyard-tab-hulls`, `shipyard-tab-engines`, `shipyard-tab-modules`, `shipyard-catalog`, `shipyard-section-<hulls\|engines\|modules>`, `shipyard-section-<…>-title`, `shipyard-part-<id>` (also `data-part-id`, `data-category`), `shipyard-part-<id>-name`, `shipyard-part-<id>-price`, `shipyard-part-<id>-count`, `shipyard-part-<id>-add-button` |
| `/shipyard` part modal | `shipyard-part-modal` (also `data-part-id`), `shipyard-part-modal-close-button`, `shipyard-part-modal-name`, `shipyard-part-modal-description`, `shipyard-part-modal-mass`, `shipyard-part-modal-power`, `shipyard-part-modal-cargo`, `shipyard-part-modal-comfort` |
| `/shipyard` build | `shipyard-build` (the drop area), `shipyard-build-title`, `shipyard-build-empty`, `shipyard-build-hull-top`, `shipyard-build-hull-top-name`, `shipyard-build-hull-top-price`, `shipyard-build-hull-bottom`, `shipyard-build-hull-bottom-name`, `shipyard-build-hull-bottom-price`, `shipyard-build-items`, `shipyard-build-item-<index>` (also `data-part-id`, `data-index`), `shipyard-build-item-<index>-name`, `shipyard-build-item-<index>-price`, `shipyard-build-item-<index>-remove-button`, `shipyard-total`, `shipyard-order-error`, `shipyard-sign-in-button`, `shipyard-order-button` |
| `/shipyard` order modal | `shipyard-order-modal` (also `data-number`), `shipyard-order-modal-text`, `shipyard-order-modal-total`, `shipyard-order-modal-close-button` |
| `/order` step 1 | `order-form`, `order-step-1`, `order-name-input`, `order-last-name-input`, `order-address-input`, `order-station-input`, `order-station-list`, `order-station-option-<number>`, `order-phone-input`, `order-next-button`; errors `order-name-error`, `order-last-name-error`, `order-address-error`, `order-station-error`, `order-phone-error` |
| `/order` step 2 | `order-step-2`, `order-date-input`, `order-datepicker`, `order-datepicker-prev-button`, `order-datepicker-month`, `order-datepicker-next-button`, `order-datepicker-days`, `order-datepicker-day-<YYYY-MM-DD>`, `order-period-dropdown`, `order-period-value`, `order-period-list`, `order-period-option-<1…7>`, `order-color-group`, `order-color-pinky-swear-checkbox`, `order-color-gray-rainbow-checkbox`, `order-comment-input`, `order-back-button`, `order-submit-button`; errors `order-date-error`, `order-period-error`, `order-comment-error`, `order-form-error` |
| `/order` modals | `order-confirm-modal`, `order-confirm-text`, `order-confirm-yes-button`, `order-confirm-no-button`, `order-success-modal`, `order-success-text` (also `data-track`), `order-view-status-button` |
| `/track` | `track-search-form`, `track-number-input`, `track-view-button`, `track-not-found-message`, `track-order` (also `data-track`), `track-group-1`, `track-group-2`, `track-group-3`, `track-name-value`, `track-last-name-value`, `track-address-value`, `track-station-dot` (also `data-color`), `track-station-value`, `track-phone-value`, `track-date-value`, `track-period-value`, `track-color-value`, `track-comment-value`, `track-statuses`, `track-status-<1…5>`, `track-status-delayed`, each with `-title` and `-caption` (status 5 has a caption only while current) |
| `/track` cancel | `track-cancel-button`, `track-cancel-modal`, `track-cancel-text`, `track-cancel-error`, `track-cancel-back-button`, `track-cancel-confirm-button`, `track-canceled-modal`, `track-canceled-text`, `track-canceled-ok-button` |
| 404 | `not-found-message`, `not-found-home-link` |
| `/register` | `register-form`, `register-name-input`, `register-name-error`, `register-email-input`, `register-email-error`, `register-password-input`, `register-password-error`, `register-submit-button`, `register-login-link` |
| `/login` | `login-form`, `login-form-error`, `login-email-input`, `login-email-error`, `login-password-input`, `login-password-error`, `login-submit-button`, `login-register-link`, `login-forgot-password-link` |
| `/forgot-password` | `forgot-password-form`, `forgot-password-email-input`, `forgot-password-email-error`, `forgot-password-submit-button`, `forgot-password-success-message`, `forgot-password-login-link` |
| `/account` | `account-name`, `account-email`, `account-logout-form`, `account-logout-button` |

`<index>` of a build item is its position among the engines and modules, from 0; it changes when
items are reordered or removed. `<id>` of a part is its `id` in `GET /api/v1/shipyard/parts`.

Error elements are always in the DOM and `hidden` while empty: check visibility, not presence.
The same goes for the header search form, the FAQ answers, the second step of the order form,
its lists and date picker, and the modals. `order-title` is one `<h1>` whose text is the current step's title.

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
  data/             story data as JSON (FAQ, stations, fleet, shipyard parts): edit names and texts here, not in code
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

| Flag | Area | What it breaks (with the flag) | Expected behaviour (without) |
|---|---|---|---|
| `BUG_AUTOPILOT_LOGIN_RULES` | API | `POST /autopilot` creates an autopilot whose `login` breaks the rules: Cyrillic, 1 or 11 characters, spaces, digits, a JSON number | `400` "Insufficient data to create an account" |
| `BUG_AUTOPILOT_PASSWORD_RULES` | API | `POST /autopilot` accepts the passwords `"123"`, `"12345"`, `"lttr"` and a JSON number (`1234`) | `400` |
| `BUG_AUTOPILOT_NAME_RULES` | API | `POST /autopilot` accepts the first names `"K"`, 11 characters, `"1234"`, names with spaces | `400` |
| `BUG_MISSING_NAME_409` | API | `POST /autopilot` without `firstName` → `409` "This login is already in use. Please try another one" | `400` "Insufficient data to create an account" |
| `BUG_LOGIN_NO_PASSWORD_504` | API | `POST /autopilot/login` without `password` → `504` "Service unavailable" | `400` "Insufficient data to log in" |
| `BUG_TRACK_DELETED_AUTOPILOT` | API, UI | an order accepted by a since-deleted autopilot is still found by track: `GET /orders/track` → `200`, `/track` shows it | `404` "Order not found"; "There is no such order…" |
| `BUG_CANCELED_ORDER_VISIBLE` | UI, API | a canceled order is still shown on `/track` (as "Shuttle in the hangar") and returned by `GET /orders/track` | "There is no such order. Are you sure you entered the correct number?"; `404` |
| `BUG_STATUS_SEARCH_ENTER` | UI | Enter in the header **Order Number** field does nothing (the **Go!** button still works) | Enter opens `/track?t=<number>` |
| `BUG_ADD_BUTTON_STALE_TOTAL` | UI | on `/shipyard` the **Add** button adds the part, but the total keeps its old value until the next other change | the total is recalculated at once |

Notes:

- With a `*_RULES` flag the field accepts any non-empty string or a number; a missing, `null` or
  empty value is still `400`. A number is stored as its text, so an autopilot created with the
  password `1234` logs in with `"1234"`. Each flag relaxes its own field only.
- `BUG_MISSING_NAME_409` answers `409` whenever `firstName` is absent or `null`, whatever the other fields are.
- `BUG_LOGIN_NO_PASSWORD_504` covers a missing, `null` or empty `password`; a missing `login` is still `400`.
- The two "still found" flags affect the search by track number only: such orders are not
  listed by `GET /orders` and cannot be accepted or finished.
- The enabled flags are logged when the stand starts: `Seeded defects enabled: ...`.
