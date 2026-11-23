# UI

Part of the [space-shuttle-qa-stand](../README.md) documentation.

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
- **Order Status** reveals the **Order Number** field; Enter → `/track?t=<number>` (the field has no button);
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
field rules and messages listed under [Order fields](api.md#autopilot-station-and-order-api).
Placeholders are the field names; required fields start with `*`. An invalid field gets its
message under it and a red border. Every field keeps an empty line for that message, so the form
does not move when one appears. Field borders: gray `#8c959f` untouched, blue `#0969da` in
focus, black `#1a1a1a` once the value has passed its check, red `#cf222e` on an error.

**Step 1, "For Whom is the Shuttle":** Name, Last Name, Address, Shuttle Station, Phone, **Next**.
Fields are checked when they lose focus and on **Next**; with errors the form stays on step 1.
The address is trimmed when it loses focus. Shuttle Station is a search: focusing it lists all
stations, typing filters them from the first character (`GET /api/v1/stations/search`), each with a
dot in its line color; a station counts only when picked from the list by click.

**Step 2, "About Rent":**

- **When to Bring the Shuttle** — a date picker that opens on the current month with days before
  tomorrow disabled. The date can also be typed, as `DD.MM.YYYY`; a malformed, non-existent or too
  early date gives "Enter a valid date". "Today" is the stand's (`STAND_TZ`), not the browser's.
  Once a complete date is typed the calendar closes (a click on the field opens it again).
  The calendar drops down under the field, flush with its right edge: month and year in bold with
  the month arrows to their right, weekdays as `MO` … `SU`, Saturdays and Sundays in red. Picking
  a day puts it into the field at once and the field keeps the focus (blue border).
- **Rental Period** — a custom dropdown (a `<button>` and a list, not a `<select>`): "one day" … "seven days".
- **Shuttle Color** — checkboxes "pinky swear" and "gray rainbow": both, one or none. A colour that
  is not ticked stays gray.
- **Comment for Autopilot** — optional.
- **Back** returns to step 1 with all data kept; **Order** validates step 2.

With no errors **Order** opens the modal "Do you want to place the order?" (**Yes** / **No**).
**Yes** places the order and shows "Order number NNNNN." (large) and, below it, "Write it down: it
will come in handy to track the status" (smaller) with **View Status** → `/track?t=NNNNN`.

The station list and the period list open in the page flow: they push the rest of the form down
and never cover another field. The calendar is a drop-down over the form: opening or closing it
moves nothing.

### Order status

`/track?t=<number>` has three variants: no number (search row only), found, not found. The search
row — the **Order Number** field and **View**, by click or Enter — is present in all of them.

Not found (HTTP 404): under the search row a picture in a black frame — a shuttle lying on the
runway (`track-not-found-runway`: tarmac, edge line, centre marking, skid marks), both wings off — and, centred over its top, "There is no such order." (large) with "Are you
sure you entered the correct number?" (smaller) below.

A found order shows its data in three groups (Name, Last Name, Address, Shuttle Station with its
colored dot, Phone · When to Bring the Shuttle, Rental Period · Shuttle Color, Comment for
Autopilot; an empty comment or color keeps its caption with an empty value) and the status chain:

| # | Title | Caption while current | Caption while not current |
|---|---|---|---|
| 1 | Shuttle in the hangar | Your autopilot is warming up for departure | same |
| 2 | Autopilot <firstName> is heading towards you ("Autopilot is heading towards you" before accept) | Contact number: 0101 | same |
| 3 | Autopilot is on site | Pick up the shuttle and pay the rental fee | same |
| 4 | Okay, let's fly now | Rental ends on <day> at <time> | before the flight: Until the rental is over; once passed: still Rental ends on <day> at <time> (gray) |
| 5 | Rental time has ended | <firstName> is heading home to recharge. Thanks for flying with us. | no caption |
| — | Autopilot delayed (red, takes the place of status 2) | We won't be able to deliver the shuttle on time. To check the status of your order, please call support at: 0101 | — |

Every status is an element with `data-state` = `done` / `current` / `upcoming` and
`data-current` = `true` / `false`. Its circle (`-marker`) holds the status number, or `✓` once the
status is behind. The current status is black, the others gray, "Autopilot delayed" red. The page
is rendered on the server: reload it to see a new status.

**Cancel order** works until an autopilot accepts the order; after that the button stays on the
page, disabled. It opens the modal "Do you want to cancel the order?" with **Back** (closes the
modal, the order stays) and **Cancel** → a modal of the same size: "Order canceled." (large), "Come
back, we are always waiting for you :)" (smaller) and **Okay** → `/`. A canceled order is no
longer found.

**Colours.** Black is `#1a1a1a`. Primary buttons (Order, Next, View, View Status, Okay, Back in the
cancel modal, …) are black with white text; Back on step 2, Cancel order and Cancel in the modal
are white with a black border and black text; Order Status in the header is transparent and does
not react to the pointer. Under the pointer **Order** becomes `#333333` in the header and on the
landing, and `#444444` on step 2 of the form.

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
| every page | `header-logo-link`, `header-logo-inc`, `header-holonet-link`, `header-shipyard-link`, `header-order-button`, `header-status-button`, `header-status-form`, `header-status-input`, `header-account-link`, `<page>-page` on `<main>`, `<page>-title` on `<h1>` |
| `/` | `home-pitch`, `home-faq-title`, `home-faq`, `home-faq-question-N`, `home-faq-answer-N` (N = 0…7), `home-order-button`, `home-cookie-banner`, `home-cookie-text`, `home-cookie-accept-button` |
| `/holonet` | `holonet-intro`, `holonet-news`, `holonet-news-item-N` |
| `/shipyard` catalog | `shipyard-tabs`, `shipyard-tab-hulls`, `shipyard-tab-engines`, `shipyard-tab-modules`, `shipyard-catalog`, `shipyard-section-<hulls\|engines\|modules>`, `shipyard-section-<…>-title`, `shipyard-part-<id>` (also `data-part-id`, `data-category`), `shipyard-part-<id>-name`, `shipyard-part-<id>-price`, `shipyard-part-<id>-count`, `shipyard-part-<id>-add-button` |
| `/shipyard` part modal | `shipyard-part-modal` (also `data-part-id`), `shipyard-part-modal-close-button`, `shipyard-part-modal-name`, `shipyard-part-modal-description`, `shipyard-part-modal-mass`, `shipyard-part-modal-power`, `shipyard-part-modal-cargo`, `shipyard-part-modal-comfort` |
| `/shipyard` build | `shipyard-build` (the drop area), `shipyard-build-title`, `shipyard-build-empty`, `shipyard-build-hull-top`, `shipyard-build-hull-top-name`, `shipyard-build-hull-top-price`, `shipyard-build-hull-bottom`, `shipyard-build-hull-bottom-name`, `shipyard-build-hull-bottom-price`, `shipyard-build-items`, `shipyard-build-item-<index>` (also `data-part-id`, `data-index`), `shipyard-build-item-<index>-name`, `shipyard-build-item-<index>-price`, `shipyard-build-item-<index>-remove-button`, `shipyard-total`, `shipyard-order-error`, `shipyard-sign-in-button`, `shipyard-order-button` |
| `/shipyard` order modal | `shipyard-order-modal` (also `data-number`), `shipyard-order-modal-text`, `shipyard-order-modal-total`, `shipyard-order-modal-close-button` |
| `/order` step 1 | `order-form`, `order-step-1`, `order-name-input`, `order-last-name-input`, `order-address-input`, `order-station-input`, `order-station-list`, `order-station-option-<number>`, `order-phone-input`, `order-next-button`; errors `order-name-error`, `order-last-name-error`, `order-address-error`, `order-station-error`, `order-phone-error` |
| `/order` step 2 | `order-step-2`, `order-date-input`, `order-datepicker`, `order-datepicker-prev-button`, `order-datepicker-month`, `order-datepicker-next-button`, `order-datepicker-days`, `order-datepicker-day-<YYYY-MM-DD>`, `order-period-dropdown`, `order-period-value`, `order-period-list`, `order-period-option-<1…7>`, `order-color-group`, `order-color-pinky-swear-checkbox`, `order-color-gray-rainbow-checkbox`, `order-comment-input`, `order-back-button`, `order-submit-button`; errors `order-date-error`, `order-period-error`, `order-comment-error`, `order-form-error` |
| `/order` modals | `order-confirm-modal`, `order-confirm-text`, `order-confirm-yes-button`, `order-confirm-no-button`, `order-success-modal`, `order-success-text` (also `data-track`; wraps `order-success-title`, `order-success-note`), `order-view-status-button` |
| `/track` | `track-search-form`, `track-number-input`, `track-view-button`, `track-not-found-message` (wraps `track-not-found-image` with `track-not-found-runway` inside it, `track-not-found-title`, `track-not-found-hint`), `track-order` (also `data-track`), `track-group-1`, `track-group-2`, `track-group-3`, `track-name-value`, `track-last-name-value`, `track-address-value`, `track-station-dot` (also `data-color`), `track-station-value`, `track-phone-value`, `track-date-value`, `track-period-value`, `track-color-value`, `track-comment-value`, `track-statuses`, `track-status-<1…5>`, `track-status-delayed`, each with `-marker`, `-title` and `-caption` (status 5 has a caption only while current) |
| `/track` cancel | `track-cancel-button`, `track-cancel-modal`, `track-cancel-text`, `track-cancel-error`, `track-cancel-back-button`, `track-cancel-confirm-button`, `track-canceled-modal`, `track-canceled-text` (wraps `track-canceled-title`, `track-canceled-note`), `track-canceled-ok-button` |
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
