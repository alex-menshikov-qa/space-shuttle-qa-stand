# API

Part of the [space-shuttle-qa-stand](../README.md) documentation.

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
| `GET /autopilot/{id}/ordersCount` | `200 {"id": <int>, "ordersCount": <int>}` — orders the autopilot has accepted, in progress and finished; canceled orders do not count | `400` "Insufficient data to perform the search" (empty id: `/autopilot//ordersCount`) · `404` "There is no autopilot with such id" (also for a non-numeric id) |
| `GET /stations/search?s=` | `200 {"stations": [{number, name, color}]}` — names containing `s`, case-insensitive, from 1 character; without `s` all stations | — |
| `POST /orders` | `201 {"track": <int>}` | `400` with the message of the first invalid field |
| `GET /orders[?autopilotId=&limit=&page=&nearestStation=]` | `200 {"orders": [...], "pageInfo": {page, total, limit}, "availableStations": [{number, name, color}]}` — one page of orders, see [Order list](#order-list) | `400` "Parameter 'limit' must be a number from 1 to 30" · "Parameter 'page' must be a number, 0 or greater" · "Parameter 'nearestStation' must be a JSON array of station numbers as strings" · "Station {number} not found" · `404` "Autopilot with identifier {autopilotId} not found" |
| `GET /orders/track?t=` | `200 {"order": {...}}` | `400` "Insufficient data to perform the search" (no `t`) · `404` "Order not found" |
| `PUT /orders/accept/{id}?autopilotId=` | `200 {"ok": true}` | `400` "Insufficient data to perform the search" · `404` "There is no order with such id" / "There is no autopilot with such id" · `409` "This order is already in progress" |
| `PUT /orders/finish/{id}` | `200 {"ok": true}` | `404` "There is no order with such id" · `409` "This order cannot be finished" (not accepted yet, or already finished) |
| `PUT /orders/cancel` `{track}` | `200 {"ok": true}` | `400` "Insufficient data to perform the search" · `404` "Order not found" · `409` "This order is already in progress" |
| `GET /ping` | `200`, `text/plain`, body `pong` — the API is up; no database involved (that is `/health`) | — |

`{id}` in accept / finish is the order's `id` (from `GET /orders/track`), not its track number.
`ordersCount` always equals `pageInfo.total` of `GET /orders?autopilotId=<id>`. `GET /autopilot/ordersCount`
(no id segment at all) is a `405`: that path belongs to `DELETE /autopilot/{id}`.

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
| `comment` | optional; Latin letters, digits, space, hyphen, dot, comma; up to 24 | Enter a valid comment |

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

### Order list

`GET /orders` lists orders page by page, **oldest first (by order `id`)**. Canceled orders and orders of
deleted autopilots are not listed. All parameters are optional and combine:

| Parameter | Meaning |
|---|---|
| `autopilotId` | only the orders accepted by this autopilot |
| `limit` | orders per page, 1–30; default **30** |
| `page` | page number, **from 0**; default 0 |
| `nearestStation` | only the orders at these stations: a JSON array of station numbers **as strings**, `?nearestStation=["1","2"]` (URL-encoded: `%5B%221%22%2C%222%22%5D`) |

- `pageInfo.total` counts every order that matches the filters, whatever the page; `pageInfo.page`
  and `pageInfo.limit` are the page and limit used.
- A page past the end is `200` with an empty `orders` and the real `total`.
- `availableStations` lists the stations of `nearestStation` (by number, no duplicates); without the
  filter, every station. `nearestStation=[]` gives an empty page and no stations.
- Numbers are plain digits, up to 9 of them; `[1]` (numbers, not strings) is a `400`.
- Checks run in this order: `limit`, `page`, `nearestStation`, then `autopilotId`; the first problem is reported.
- Without parameters the response is the first page of 30: with more than 30 orders, the newest are on later pages.

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
