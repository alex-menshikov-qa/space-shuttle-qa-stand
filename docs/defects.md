# Known defects

Part of the [space-shuttle-qa-stand](../README.md) documentation.

## Known defects

The stand can deliberately reproduce bugs ("seeded defects") so tests can catch them: 48 flags,
41 of which reproduce bugs from my 2023 bug reports. **Origin** says where each comes from:
`SSI-n` — a bug report (Web, order status: SSI-3…SSI-28 and SSI-95; API: SSI-29…SSI-62; Web, order
form: SSI-65…SSI-94; mobile app: SSI-96…SSI-102);
`training stand` — a bug of the training stand the first tests were written against;
`new` — a defect that first appeared on this stand;
`new (2026)` — a defect added in 2026 with the API features taken from the original training stand
(order count, paging).

For a seeded report, its **Expected result** is how the stand behaves by default and its **Actual
result** is what happens with the flag on. 78 of the 98 reports are seeded; the other 20 are
listed under [Not seeded](#not-seeded).

Each defect is off by default and is switched on with `BUG_<NAME>=1` in `.env`
(registry: `app/defects.py`). A misspelled `BUG_*` name or a value other than
`1/true/yes/on` or `0/false/no/off` stops the stand from starting, so a typo can never
silently switch a defect off.

The bug reports themselves are in [`docs/bug-reports/`](bug-reports/README.md); every `SSI-n`
below links to its report.

| Flag | Origin | Area | What it breaks (with the flag) | Expected behaviour (without) |
|---|---|---|---|---|
| `BUG_AUTOPILOT_LOGIN_RULES` | [SSI-29…SSI-40](bug-reports/api.md#ssi-29) | API | `POST /autopilot` creates an autopilot whose `login` breaks the rules: Cyrillic or Chinese, 1 or 11+ characters, spaces at the edges or inside, `"***"`, a JSON number (`1234`). `login: true` answers `500` with the body `{"code": 500, "message": "operator does not exist: character varying = boolean"}` and registers nobody ([SSI-39](bug-reports/api.md#ssi-39)) | `400` "Insufficient data to create an account" |
| `BUG_AUTOPILOT_PASSWORD_RULES` | [SSI-41…SSI-50](bug-reports/api.md#ssi-41) | API | `POST /autopilot` accepts the passwords `"123"`, `"12345"`, 41 digits, `"lttr"`, `"****"`, passwords with a space (`" 111"`, `"111 "`, `"11 1"`), a JSON number (`1111`) and `true` | `400` |
| `BUG_AUTOPILOT_NAME_RULES` | [SSI-51…SSI-61](bug-reports/api.md#ssi-51) | API | `POST /autopilot` accepts the first names `"K"`, 11+ characters, Chinese, `"1234"`, `"***"`, names with a space at the edges or inside, and `true` | `400` |
| `BUG_MISSING_NAME_409` | training stand | API | `POST /autopilot` without `firstName` → `409` "This login is already in use. Please try another one" | `400` "Insufficient data to create an account" |
| `BUG_LOGIN_NO_PASSWORD_504` | training stand | API | `POST /autopilot/login` without `password` → `504` "Service unavailable" | `400` "Insufficient data to log in" |
| `BUG_TRACK_DELETED_AUTOPILOT` | [SSI-62](bug-reports/api.md#ssi-62) | API, UI | an order accepted by a since-deleted autopilot is still found by track: `GET /orders/track` → `200`, `/track` shows it | `404` "Order not found"; "There is no such order…" |
| `BUG_CANCELED_ORDER_VISIBLE` | [SSI-25](bug-reports/web-order-status.md#ssi-25), [SSI-26](bug-reports/web-order-status.md#ssi-26) | UI, API | a canceled order is still shown on `/track` (as "Shuttle in the hangar") and returned by `GET /orders/track` | "There is no such order." / "Are you sure you entered the correct number?"; `404` |
| `BUG_STATUS_SEARCH_ENTER` | [SSI-5](bug-reports/web-order-status.md#ssi-5) | UI | Enter in the header **Order Number** field does nothing | Enter opens `/track?t=<number>` |
| `BUG_HEADER_SEARCH_PLACEHOLDER` | [SSI-3](bug-reports/web-order-status.md#ssi-3) | UI | the header order search has the placeholder "Enter order number" | "Order Number" |
| `BUG_HEADER_SEARCH_EXTRA_BUTTON` | [SSI-4](bug-reports/web-order-status.md#ssi-4) | UI | a **Go!** button (`header-status-go-button`) appears to the right of the header **Order Number** field; it starts the search | the field has no button |
| `BUG_TRACK_IMAGE_NO_RUNWAY` | [SSI-6](bug-reports/web-order-status.md#ssi-6) | UI | the "order not found" picture has no runway (`track-not-found-runway` is absent): the shuttle, its wings and the smoke lie on the plain background | the shuttle lies on the runway: tarmac, edge line, centre marking, skid marks |
| `BUG_ORDER_HOVER_VULPTEX` | [SSI-7](bug-reports/web-order-status.md#ssi-7) | UI | **in Firefox only**, the header **Order** button does not react to the pointer: it stays `#1a1a1a` | it lightens to `#333333` in every browser |
| `BUG_TRACK_WRONG_STATION` | [SSI-10](bug-reports/web-order-status.md#ssi-10) | UI | `/track` shows the next station by number instead of the ordered one (the first station after the last), name and dot colour; the API is right | the ordered station |
| `BUG_TRACK_DATE_LABEL` | [SSI-12](bug-reports/web-order-status.md#ssi-12) | UI | on `/track` the date row is captioned "Delivery Date" | "When to Bring the Shuttle" |
| `BUG_TRACK_DATE_PLUS_DAY` | [SSI-13](bug-reports/web-order-status.md#ssi-13) | UI | `/track` shows the delivery date one day late; the API is right | the ordered date |
| `BUG_TRACK_EMPTY_COLOR` | [SSI-14](bug-reports/web-order-status.md#ssi-14) | UI | an order without a colour shows `any` as its **Shuttle Color** | an empty value |
| `BUG_TRACK_EMPTY_COMMENT` | [SSI-15](bug-reports/web-order-status.md#ssi-15) | UI | an order without a comment has no **Comment for Autopilot** row at all: no caption, no `track-comment-value` | the caption with an empty value |
| `BUG_TRACK_NO_WRAP` | [SSI-16](bug-reports/web-order-status.md#ssi-16) | UI | values on `/track` never wrap: a 50-character address stays on one line and runs to the left, over the field names | long values wrap inside the block |
| `BUG_TRACK_AUTOPILOT_NAME_TRUNCATED` | [SSI-18](bug-reports/web-order-status.md#ssi-18) | UI | in "Autopilot `<firstName>` is heading towards you" a name of 10 or more characters is cut to its first two and an ellipsis ("Averyveryl" → "Av…"); the API is right | the name in full |
| `BUG_STATUS_ON_SITE_SKIPPED` | [SSI-19](bug-reports/web-order-status.md#ssi-19) | API, UI | after finish the order stays `heading` (status 2) until `PICKUP_MINUTES` pass, then goes straight to `flying` (status 4) | `on_site` (status 3) right after finish |
| `BUG_CANCELED_MODAL_SIZE` | [SSI-21](bug-reports/web-order-status.md#ssi-21), [SSI-22](bug-reports/web-order-status.md#ssi-22) | UI | the "Order canceled." window is full width in a window up to 1280 px wide; in a wider window it is about a third smaller than "Do you want to cancel the order?", centred | the same small centred window as "Do you want to cancel the order?" |
| `BUG_TRACK_CANCEL_HIDDEN_ON_ACCEPT` | [SSI-24](bug-reports/web-order-status.md#ssi-24) | UI | once an autopilot has accepted the order **Cancel order** is gone from the page (`track-cancel-button` is absent) | the button stays on the page, disabled |
| `BUG_DELAYED_ONE_DAY_EARLY` | [SSI-27](bug-reports/web-order-status.md#ssi-27) | API, UI | an undelivered order becomes `delayed` a day early: from 00:00 of the delivery day | after 23:59 of the delivery day |
| `BUG_ENDED_STATUS_4_AS_5` | [SSI-28](bug-reports/web-order-status.md#ssi-28) | UI | after the rental has ended status 4 takes the title and caption of status 5: "Rental time has ended" twice in a row; the highlighting is right | status 4 stays "Okay, let's fly now" with the caption "Rental ends on `<day>` at `<time>`" |
| `BUG_FORM_CONFIRM_YES_DEAD` | [SSI-65](bug-reports/web-order-form.md#ssi-65) | UI | **Yes** in "Do you want to place the order?" does not respond, so no order can be placed from the form; `POST /orders` works | **Yes** places the order |
| `BUG_FORM_NAME_DASH` | [SSI-66](bug-reports/web-order-form.md#ssi-66) | UI, API | the order **Name** rejects a hyphen: "Meetra-Koth" → "Enter the correct name" | accepted |
| `BUG_FORM_LAST_NAME_16` | [SSI-67](bug-reports/web-order-form.md#ssi-67) | UI, API | **Last Name** accepts 16 characters ("Grandmoffftarkin"); 17 are still rejected | "Enter the correct last name" from 16 characters |
| `BUG_FORM_ADDRESS_REQUIRED` | [SSI-68](bug-reports/web-order-form.md#ssi-68) | UI, API | an empty **Address** is accepted (1–4 characters are still rejected) | "Enter the correct address" |
| `BUG_FORM_ADDRESS_50` | [SSI-69](bug-reports/web-order-form.md#ssi-69) | UI, API | an **Address** of exactly 50 characters is rejected | accepted; 51 is rejected |
| `BUG_FORM_PHONE_10` | [SSI-70](bug-reports/web-order-form.md#ssi-70) | UI, API | a **Phone** of 10 characters is rejected ("1234567891"); 11 and 12 pass | accepted; 9 is rejected |
| `BUG_FORM_PHONE_13` | [SSI-71](bug-reports/web-order-form.md#ssi-71) | UI, API | a **Phone** of 13 characters is accepted ("1234567891011"); 14 is rejected | "Enter the correct phone number" from 13 characters |
| `BUG_FORM_COMMENT_CHARSET` | [SSI-72](bug-reports/web-order-form.md#ssi-72), [SSI-73](bug-reports/web-order-form.md#ssi-73), [SSI-74](bug-reports/web-order-form.md#ssi-74) | UI, API | **Comment** accepts any characters: Cyrillic ("Хочу"), other scripts ("我要"), quotes; still up to 24 | "Enter a valid comment" |
| `BUG_FORM_COMMENT_LENGTH` | [SSI-75](bug-reports/web-order-form.md#ssi-75) | UI, API | **Comment** has no upper limit: 25 and 90 allowed characters pass | "Enter a valid comment" from 25 characters |
| `BUG_FORM_DATE_PAST` | [SSI-76](bug-reports/web-order-form.md#ssi-76) | UI, API | today and any past date can be picked in the calendar, typed and sent as `deliveryDate` | the earliest date is tomorrow |
| `BUG_FORM_DATE_PICK_NO_HIGHLIGHT` | [SSI-80](bug-reports/web-order-form.md#ssi-80) | UI | after a day is picked in the calendar **When to Bring the Shuttle** loses the focus and its blue border | the field keeps the focus and stays blue |
| `BUG_FORM_STATION_HOVER` | [SSI-81](bug-reports/web-order-form.md#ssi-81) | UI | **Shuttle Station** gets a blue border under the pointer | blue only in focus |
| `BUG_FORM_TYPING_BORDER` | [SSI-82…SSI-85](bug-reports/web-order-form.md#ssi-82) | UI | in **Name**, **Last Name**, **Address** and **Phone** the border turns black as soon as anything is typed, valid or not ("1") | blue while typing; black once a valid value is left |
| `BUG_FORM_NEXT_LABEL` | [SSI-86](bug-reports/web-order-form.md#ssi-86) | UI | the step-1 button reads "Continue" | "Next" |
| `BUG_FORM_STATION_PLACEHOLDER_DARK` | [SSI-88](bug-reports/web-order-form.md#ssi-88) | UI | the **Shuttle Station** placeholder is dark gray, `#59636e` | light gray `#8c959f`, like the other placeholders |
| `BUG_FORM_COLOR_UNTICKED_BLACK` | [SSI-89](bug-reports/web-order-form.md#ssi-89) | UI | with one **Shuttle Color** ticked, the text of the other turns black | an unticked colour stays gray |
| `BUG_FORM_CALENDAR_LOWERCASE` | [SSI-91](bug-reports/web-order-form.md#ssi-91) | UI | the calendar shows month and weekday names in lowercase: "august", "mo" | "August", `MO` |
| `BUG_FORM_CALENDAR_BLACK` | [SSI-92](bug-reports/web-order-form.md#ssi-92) | UI | all calendar text is black: weekday names and weekends too | gray weekday names, red Saturdays and Sundays |
| `BUG_FORM_PERIOD_LIST_NARROW` | [SSI-94](bug-reports/web-order-form.md#ssi-94) | UI | the **Rental Period** list is half as wide as the field, at its right edge | as wide as the field |
| `BUG_FORM_ERROR_LAYOUT_SHIFT` | new | UI | on `/order` an error text that appears under a field pushes the rest of the form down by a line, so a click that leaves an invalid field for **Rental Period** misses and the list does not open | every field keeps an empty line for its error; nothing moves |
| `BUG_ADD_BUTTON_STALE_TOTAL` | new | UI | on `/shipyard` the **Add** button adds the part, but the total keeps its old value until the next other change | the total is recalculated at once |
| `BUG_ORDERS_COUNT_AS_STRING` | new (2026) | API | `GET /autopilot/{id}/ordersCount` returns both numbers as strings: `{"id": "7", "ordersCount": "2"}`, as in the example of the original's documentation | `{"id": 7, "ordersCount": 2}` |
| `BUG_ORDERS_PAGE_FROM_ONE` | new (2026) | API | `GET /orders` counts pages from one: `page=0` and `page=1` return the same first page, `page=2` the second; `pageInfo.page` is as requested | pages from zero: `page=1` is the second page |
| `BUG_ORDERS_LIMIT_OVER_30` | new (2026) | API | `GET /orders` accepts a `limit` above 30 and returns as many orders as asked; `pageInfo.limit` is as requested (`limit=0` is still a `400`) | `400` "Parameter 'limit' must be a number from 1 to 30" |

### Not seeded

These 20 bug reports are not reproduced by a flag.

| Bug | Report | Why not |
|---|---|---|
| [SSI-8](bug-reports/web-order-status.md#ssi-8) | the distance between **Order** and **View** is too small | pixel-level spacing: the stand has the correct layout |
| [SSI-9](bug-reports/web-order-status.md#ssi-9) | the order data block is aligned with the left border of the search field | pixel-level offset |
| [SSI-11](bug-reports/web-order-status.md#ssi-11) | the station's colour circle is too far from the station name | pixel-level spacing |
| [SSI-17](bug-reports/web-order-status.md#ssi-17) | the status chain is centred on the screen (1280×720 only) | pixel-level alignment |
| [SSI-20](bug-reports/web-order-status.md#ssi-20) | the buttons of "Do you want to cancel the order?" sit too high (1920×1080 only) | pixel-level alignment |
| [SSI-23](bug-reports/web-order-status.md#ssi-23) | **Okay** in "Order canceled" sits too high | pixel-level alignment |
| [SSI-95](bug-reports/web-order-status.md#ssi-95) | "There is no such order" flashes when the order page is refreshed | a race: a flag cannot reproduce it honestly |
| [SSI-77](bug-reports/web-order-form.md#ssi-77) | an unexpected "Do you want to place the order?" window | by design on the stand: the window was kept on purpose and added to the requirements and mockups |
| [SSI-78](bug-reports/web-order-form.md#ssi-78) | the delivery date can be typed in by hand | by design on the stand: typing `DD.MM.YYYY` is allowed |
| [SSI-79](bug-reports/web-order-form.md#ssi-79) | both shuttle colours can be selected | by design on the stand: two checkboxes, both may be ticked |
| [SSI-87](bug-reports/web-order-form.md#ssi-87) | the content of the two lower fields is shifted to the left | pixel-level alignment |
| [SSI-90](bug-reports/web-order-form.md#ssi-90) | the calendar opens in the middle of the field | pixel-level position |
| [SSI-93](bug-reports/web-order-form.md#ssi-93) | calendar arrows on both sides of a centred month label, an extra arrow at the top | three layout details in one report, checkable by geometry only |
| [SSI-96…SSI-102](bug-reports/mobile.md#ssi-96) | the autopilot mobile app: push notification, "No HoloNet access" window | there is no mobile app on the stand |

### Environments

The bug reports were filed in two environments. On this stand they map onto the browsers the
tests use: **"Beskar, 1920×1080" is Chrome** and **"Vulptex Browser, 1280×720" is Firefox**, each at
that window size. A bug reported in both, or in Beskar only, is seeded for every browser. Two bugs
reported in Vulptex Browser only are seeded. SSI-7 acts in that browser only:
`BUG_ORDER_HOVER_VULPTEX` works in Firefox and never in Chrome. SSI-21 acts in a window up to
1280 px wide: together with SSI-22 it is one flag, `BUG_CANCELED_MODAL_SIZE`, which depends on the
window width, not on the browser.

Notes:

- With a `*_RULES` flag the field accepts any string that is not blank, a number or a boolean; a
  missing, `null`, empty or whitespace-only value is still `400` (those checks passed in 2023).
  A number or boolean is stored as its JSON text, so an autopilot created with the password `1111`
  logs in with `"1111"` and one created with `true` logs in with `"true"`. Each flag relaxes its
  own field only. The one exception is `login: true` with `BUG_AUTOPILOT_LOGIN_RULES`: `500` and
  no autopilot, with the body SSI-39 was filed with, `{"code": 500, "message": "operator does not
  exist: character varying = boolean"}` — the only response that is not `{"ok": false, "message"}`.
- `BUG_MISSING_NAME_409` answers `409` whenever `firstName` is absent or `null`, whatever the other fields are.
- `BUG_LOGIN_NO_PASSWORD_504` covers a missing, `null` or empty `password`; a missing `login` is still `400`.
- The two "still found" flags affect the search by track number only: such orders are not
  listed by `GET /orders` and cannot be accepted or finished.
- The `BUG_FORM_*` flags bend the one set of field rules the form, the server and
  `POST /api/v1/orders` share, so each acts in the browser and in the API alike. Each changes its
  own rule only: with `BUG_FORM_COMMENT_LENGTH` alone a long comment must still consist of allowed
  characters.
- With `BUG_FORM_DATE_PAST` an order placed for a past date is `delayed` from the moment it is
  created (its delivery day is already over), and with `BUG_DELAYED_ONE_DAY_EARLY` as well so is
  an order for today.
- `BUG_FORM_PHONE_10` and `BUG_FORM_PHONE_13` move one end of the length rule each and combine.
- With `BUG_HEADER_SEARCH_EXTRA_BUTTON` off and `BUG_STATUS_SEARCH_ENTER` on, the header search
  cannot be started at all; the search row on `/track` still works.
- The enabled flags are logged when the stand starts: `Seeded defects enabled: ...`.
- An enabled UI defect leaves no marker in the page — no attribute, flag or comment. Page scripts
  and the stylesheet are served through a small preprocessor (`app/web/scripts.py`) that sends a
  different variant of the fragment, and page values are chosen on the server, so only the
  behaviour or the look differs.
