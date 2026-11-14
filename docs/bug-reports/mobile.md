# Space Shuttle Inc bug reports. Mobile app for autopilots

Found with the Test Cases Mobile: the push notification two hours before the end of an order and the "No HoloNet access" window.

| ID | Priority | Summary |
|---|---|---|
| SSI-96 | Medium | Push notification arrives when more than 2 hours are left until the end of the order |
| SSI-97 | Medium | Push notification arrives when less than 2 hours are left until the end of the order |
| SSI-98 | Blocker | Tapping the push notification crashes the app |
| SSI-99 | Low | "No HoloNet access" window can be closed by tapping outside it |
| SSI-100 | Trivial | Push notification text: no time, no line break |
| SSI-101 | Trivial | Button in the "No HoloNet access" window is labeled "Ok" instead of "OK" |
| SSI-102 | Low | Push notification has no logo |

---

<a id="ssi-96"></a>

## SSI-96: Push notification arrives when more than 2 hours are left until the end of the order

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Mobile app for autopilots, notifications |
| **Environment** | Uteenee Holo 10 Pro, OWUI Global 19.1.3 / Droid 54, app version 1.01 |

**Description.** The push notification arrives earlier than it should: when more than 2 hours are left until the end of the order.

**Preconditions**

1. A shuttle order is created with a completion time set for tomorrow.
2. The autopilot is logged in.
3. The main screen of the app is open.

**Steps to reproduce**

1. Accept the order.
2. Set the date and time on the device to tomorrow, 20:59.

**Actual result.** The push notification arrives when more than 2 hours are left.

**Expected result.** The push notification arrives exactly 2 hours before the end of the order.

**Attachments.** Screenshot.

---

<a id="ssi-97"></a>

## SSI-97: Push notification arrives when less than 2 hours are left until the end of the order

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Mobile app for autopilots, notifications |
| **Environment** | Uteenee Holo 10 Pro, OWUI Global 19.1.3 / Droid 54, app version 1.01 |

**Description.** The push notification arrives later than it should: when less than 2 hours are left until the end of the order.

**Preconditions**

1. A shuttle order is created with a completion time set for tomorrow.
2. The autopilot is logged in.
3. The main screen of the app is open.

**Steps to reproduce**

1. Accept the order.
2. Set the date and time on the device to tomorrow, 22:59.

**Actual result.** The push notification arrives when less than 2 hours are left.

**Expected result.** The push notification arrives exactly 2 hours before the end of the order.

**Attachments.** Screenshot.

---

<a id="ssi-98"></a>

## SSI-98: Tapping the push notification crashes the app

| | |
|---|---|
| **Priority** | Blocker |
| **Area** | Mobile app for autopilots, notifications |
| **Environment** | Uteenee Holo 10 Pro, OWUI Global 19.1.3 / Droid 54, app version 1.01 |

**Description.** Tapping the "2 hours until the end of the order" push notification opens an error window instead of the app.

**Preconditions**

1. A shuttle order is created with a completion time set for tomorrow.
2. The autopilot is logged in.
3. The main screen of the app is open.

**Steps to reproduce**

1. Accept the order.
2. Set the date and time on the device to tomorrow, 21:59.
3. Tap the push notification.

**Actual result.** An application error window appears.

**Expected result.** The app opens on the "My" tab.

**Attachments.** Screenshot, `logs.txt`, `stack.txt`.

---

<a id="ssi-99"></a>

## SSI-99: "No HoloNet access" window can be closed by tapping outside it

| | |
|---|---|
| **Priority** | Low |
| **Area** | Mobile app for autopilots, "No HoloNet access" window |
| **Environment** | Uteenee Holo 10 Pro, OWUI Global 19.1.3 / Droid 54, app version 1.01 |

**Description.** Tapping anywhere outside the "No HoloNet access" window closes it.

**Preconditions**

1. The autopilot is logged in.
2. The main screen of the app is open.

**Steps to reproduce**

1. Disable the HoloNet connection.
2. Tap "My" while on the "All" tab.
3. Tap the area outside the pop-up window.

**Actual result.** The window closes on a tap outside it.

**Expected result.** The window closes only on a tap on the "OK" button.

**Attachments.** Screen recording.

---

<a id="ssi-100"></a>

## SSI-100: Push notification text: no time, no line break

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Mobile app for autopilots, notifications |
| **Environment** | Uteenee Holo 10 Pro, OWUI Global 19.1.3 / Droid 54, app version 1.01 |

**Description.** In the push notification, the first sentence lacks "by time N", and the second sentence is not moved to a new line.

**Preconditions**

1. A shuttle order is created with a completion time set for tomorrow.
2. The autopilot is logged in.
3. The main screen of the app is open.

**Steps to reproduce**

1. Accept the order.
2. Set the date and time on the device to tomorrow, 21:59.
3. Expand the push notification.

**Actual result.** Notification text:

> 2 hours until the end of the order. The order to "<address>" must be completed. If you can't make it on time, please contact support: 0101

**Expected result.** Notification text:

> 2 hours until the end of the order. The order to "<address>" must be completed by time N.
> If you can't make it on time, please contact support: 0101

**Attachments.** Screenshot.

---

<a id="ssi-101"></a>

## SSI-101: Button in the "No HoloNet access" window is labeled "Ok" instead of "OK"

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Mobile app for autopilots, "No HoloNet access" window |
| **Environment** | Uteenee Holo 10 Pro, OWUI Global 19.1.3 / Droid 54, app version 1.01 |

**Description.** The button in the "No HoloNet access" window is labeled "Ok" instead of "OK".

**Preconditions**

1. The autopilot is logged in.
2. The main screen of the app is open.

**Steps to reproduce**

1. Disable the HoloNet connection.
2. Tap "My" while on the "All" tab.

**Actual result.** Button text: "Ok".

**Expected result.** Button text: "OK".

**Attachments.** Screenshot.

---

<a id="ssi-102"></a>

## SSI-102: Push notification has no logo

| | |
|---|---|
| **Priority** | Low |
| **Area** | Mobile app for autopilots, notifications |
| **Environment** | Uteenee Holo 10 Pro, OWUI Global 19.1.3 / Droid 54, app version 1.01 |

**Description.** The header of the push notification shows a gray square instead of the Space Shuttle Inc logo.

**Preconditions**

1. A shuttle order is created with a completion time set for tomorrow.
2. The autopilot is logged in.
3. The main screen of the app is open.

**Steps to reproduce**

1. Accept the order.
2. Set the date and time on the device to tomorrow, 21:59.
3. Expand the push notification.

**Actual result.** The notification header shows a gray square.

**Expected result.** The notification header shows the Space Shuttle Inc logo.

**Attachments.** Screenshot.
