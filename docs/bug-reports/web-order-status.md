# Space Shuttle Inc bug reports. Web: order status page

Found with the Check List Web: finding an order by its number, its details, delivery statuses, cancellation.

| ID | Priority | Summary |
|---|---|---|
| SSI-3 | Trivial | Placeholder text "Enter order number" instead of "Order Number" |
| SSI-4 | Medium | Extra button in the order number input field |
| SSI-5 | Medium | Pressing Enter does not initiate the search |
| SSI-6 | Trivial | The error message image is missing a runway |
| SSI-7 | Trivial | The "Order" button doesn't change color on hover |
| SSI-8 | Trivial | Distance between "Order" and "View" buttons is too small |
| SSI-9 | Trivial | Order data block is aligned with the left border of the search field |
| SSI-10 | Medium | Displayed shuttle station is not the one selected |
| SSI-11 | Medium | Color circle of the station runway is too far from the station name |
| SSI-12 | Low | Field name "Delivery Date" is displayed instead of "When to Bring the Shuttle" |
| SSI-13 | Medium | Displayed delivery date is one day later than selected |
| SSI-14 | Medium | "Shuttle Color" field contains text if no color was selected |
| SSI-15 | Low | "Comment for Autopilot" field is missing if no comment was entered |
| SSI-16 | Medium | Long text does not transfer to the second line |
| SSI-17 | Low | Order status chain is centered on the screen |
| SSI-18 | Medium | Long autopilot name gets truncated |
| SSI-19 | Critical | "Autopilot is on site" status does not become active |
| SSI-20 | Trivial | Buttons in the "Do you want to cancel the order?" window are positioned too high |
| SSI-21 | Low | "Order canceled" window stretches across the entire screen |
| SSI-22 | Low | "Order canceled" window is smaller than the previous window |
| SSI-23 | Trivial | "Okay" button in the "Order canceled" window is positioned too high |
| SSI-24 | Medium | "Cancel order" button disappears when the autopilot accepts the order |
| SSI-25 | Critical | Canceled order is not removed from the system |
| SSI-26 | Critical | User can view a canceled order |
| SSI-27 | Critical | Order is considered overdue too early |
| SSI-28 | Medium | Caption of the "Okay, let's fly now" status changes after the rental period expires |
| SSI-95 | Medium | "There is no such order" window flashes when the order page is refreshed |

---

<a id="ssi-3"></a>

## SSI-3: Placeholder text "Enter order number" instead of "Order Number"

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Web, header, order search |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The placeholder of the order number field says "Enter order number" instead of "Order Number".

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.

**Actual result.** Placeholder text: "Enter order number".

**Expected result.** Placeholder text: "Order Number".

**Attachments.** Screenshot.

---

<a id="ssi-4"></a>

## SSI-4: Extra button in the order number input field

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, header, order search |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** There is an extra button to the right of the order number field.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.

**Actual result.** A "Go!" button is shown to the right of the order number field.

**Expected result.** The order number field has no buttons.

**Attachments.** Screenshot.

---

<a id="ssi-5"></a>

## SSI-5: Pressing Enter does not initiate the search

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, header, order search |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** If an order number is typed into the search field and Enter is pressed, nothing happens: the search does not start.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `347171`.
4. Press Enter.

**Actual result.** The search does not start.

**Expected result.** The search starts.

**Attachments.** Screen recording.

---

<a id="ssi-6"></a>

## SSI-6: The error message image is missing a runway

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Web, "There is no such order" message |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The image under the error message has no runway: the shuttle and its wings lie on an empty background.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the number of an order that does not exist: `34`.
4. Submit the number.

**Actual result.** The image has no runway.

**Expected result.** The image shows the shuttle on a runway, as in the mockup.

**Attachments.** Screenshot.

---

<a id="ssi-7"></a>

## SSI-7: The "Order" button doesn't change color on hover

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Web, order status page |
| **Environment** | Vulptex Browser (1280×720) |

**Description.** When the cursor is over the "Order" button, the button does not react: its color stays the same.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `362345`.
4. Submit the number.
5. Hover over the "Order" button in the header.

**Actual result.** The button does not change color on hover.

**Expected result.** The button becomes slightly lighter on hover.

**Attachments.** Screen recording.

---

<a id="ssi-8"></a>

## SSI-8: Distance between "Order" and "View" buttons is too small

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The "Order" and "View" buttons are too close to each other: one blank line between them is missing.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `222870`.
4. Submit the number.

**Actual result.** The distance between the "Order" and "View" buttons is too small.

**Expected result.** There is a blank line between the buttons, as in the mockup; the search field is moved down together with the "View" button.

**Attachments.** Screenshot.

---

<a id="ssi-9"></a>

## SSI-9: Order data block is aligned with the left border of the search field

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The block with the order data is aligned with the left border of the search field, although it should be shifted slightly to the right of it.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `222870`.
4. Submit the number.

**Actual result.** The order data block is aligned with the left border of the search field.

**Expected result.** The order data block is shifted slightly to the right of the left border of the search field, as in the mockup.

**Attachments.** Screenshot.

---

<a id="ssi-10"></a>

## SSI-10: Displayed shuttle station is not the one selected

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The order status page shows the station that follows the selected one in the station list. For example, an order placed for "Alderaanian" is shown with "Senate District".

**Precondition.** An order has been placed with the shuttle station "Alderaanian".

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `830435`.
4. Submit the number.

**Actual result.** The page shows the station "Senate District".

**Expected result.** The page shows the station "Alderaanian".

**Attachments.** Two screenshots (order form, order status page).

---

<a id="ssi-11"></a>

## SSI-11: Color circle of the station runway is too far from the station name

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The color circle of the station is placed too low and too far from the station name "Senate District".

**Precondition.** An order has been placed with the shuttle station "Senate District".

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `964918`.
4. Submit the number.

**Actual result.** The color circle is not vertically aligned with the station name and is too far from it.

**Expected result.** The color circle is vertically aligned with the station name and separated from it by two spaces.

**Attachments.** Two screenshots (one per browser).

---

<a id="ssi-12"></a>

## SSI-12: Field name "Delivery Date" is displayed instead of "When to Bring the Shuttle"

| | |
|---|---|
| **Priority** | Low |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The field with the delivery date is called "Delivery Date" instead of "When to Bring the Shuttle".

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `968044`.
4. Submit the number.

**Actual result.** The field is called "Delivery Date".

**Expected result.** The field is called "When to Bring the Shuttle".

**Attachments.** Screenshot.

---

<a id="ssi-13"></a>

## SSI-13: Displayed delivery date is one day later than selected

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The "When to Bring the Shuttle" field shows a date one day later than the one selected in the order form. For example, an order placed for 07.08.2025 is shown with August 8.

**Precondition.** An order has been placed with the delivery date 07.08.2025.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `203609`.
4. Submit the number.

**Actual result.** The "When to Bring the Shuttle" field shows August 8.

**Expected result.** The "When to Bring the Shuttle" field shows August 7.

**Attachments.** Two screenshots (order form, order status page).

---

<a id="ssi-14"></a>

## SSI-14: "Shuttle Color" field contains text if no color was selected

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** If no color was selected in the order form, the "Shuttle Color" field on the order status page still contains text.

**Precondition.** An order has been placed with no color selected.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `203609`.
4. Submit the number.

**Actual result.** The "Shuttle Color" field contains the text "any".

**Expected result.** The "Shuttle Color" field is empty.

**Attachments.** Screenshot.

---

<a id="ssi-15"></a>

## SSI-15: "Comment for Autopilot" field is missing if no comment was entered

| | |
|---|---|
| **Priority** | Low |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** If no comment was entered in the order form, the "Comment for Autopilot" field is absent from the order status page.

**Precondition.** An order has been placed with an empty comment.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `203609`.
4. Submit the number.

**Actual result.** The "Comment for Autopilot" field is missing.

**Expected result.** The "Comment for Autopilot" field is shown and has no content.

**Attachments.** Screenshot.

---

<a id="ssi-16"></a>

## SSI-16: Long text does not transfer to the second line

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** If a value does not fit on one line, it is not wrapped and runs past the border of the order data block.

**Precondition.** An order has been placed with a 50-character address: `Pharmaceuticals Company Royal Promenade Avenue, 56`.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `252240`.
4. Submit the number.

**Actual result.** The address is not wrapped onto a second line and runs past the border of the block.

**Expected result.** Long values are wrapped onto a second line.

**Attachments.** Screenshot.

---

<a id="ssi-17"></a>

## SSI-17: Order status chain is centered on the screen

| | |
|---|---|
| **Priority** | Low |
| **Area** | Web, order status page |
| **Environment** | Vulptex Browser (1280×720) |

**Description.** The chain of order statuses is centered on the screen, below the block with the order data.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `347171`.
4. Submit the number.

**Actual result.** The status chain is centered and placed below the order data block.

**Expected result.** The status chain is aligned to the right edge of the screen, to the right of the order data block.

**Attachments.** Screenshot.

---

<a id="ssi-18"></a>

## SSI-18: Long autopilot name gets truncated

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** If the autopilot has a very long name, the name is cut down to two characters.

**Preconditions**

1. An order has been placed.
2. An autopilot with a 10-character name, `Averyveryl`, is registered.
3. The autopilot has accepted the order.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `968044`.
4. Submit the number.

**Actual result.** The autopilot name is truncated to two characters followed by an ellipsis.

**Expected result.** The autopilot name is shown in full.

**Attachments.** Screenshot.

---

<a id="ssi-19"></a>

## SSI-19: "Autopilot is on site" status does not become active

| | |
|---|---|
| **Priority** | Critical |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** After the autopilot presses "Finish" in its app, nothing changes in the web app: the active status does not switch to "Autopilot is on site".

**Preconditions**

1. An order has been placed.
2. The autopilot has accepted the order.
3. The autopilot has pressed "Finish".

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `968044`.
4. Submit the number.

**Actual result.** The "Autopilot is on site" status does not become active.

**Expected result.** The "Autopilot is on site" status becomes active.

**Attachments.** Screen recording.

---

<a id="ssi-20"></a>

## SSI-20: Buttons in the "Do you want to cancel the order?" window are positioned too high

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080) |

**Description.** The "Back" and "Cancel" buttons are in the middle of the window, although they should be in its lower part.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `965756`.
4. Submit the number.
5. Click "Cancel order".

**Actual result.** The "Back" and "Cancel" buttons are in the middle of the window.

**Expected result.** The "Back" and "Cancel" buttons are in the lower part of the window.

**Attachments.** Screenshot.

---

<a id="ssi-21"></a>

## SSI-21: "Order canceled" window stretches across the entire screen

| | |
|---|---|
| **Priority** | Low |
| **Area** | Web, order status page |
| **Environment** | Vulptex Browser (1280×720) |

**Description.** The "Order canceled" window is too wide: it takes up the whole width of the screen and differs in size from the previous window, "Do you want to cancel the order?".

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `903132`.
4. Submit the number.
5. Click "Cancel order".
6. Click "Cancel".

**Actual result.** The window is as wide as the screen and differs in size from the "Do you want to cancel the order?" window.

**Expected result.** The window does not take up the whole width of the screen and is the same size as the "Do you want to cancel the order?" window.

**Attachments.** Screenshot.

---

<a id="ssi-22"></a>

## SSI-22: "Order canceled" window is smaller than the previous window

| | |
|---|---|
| **Priority** | Low |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080) |

**Description.** The "Order canceled" window is too small: smaller than the previous window, "Do you want to cancel the order?".

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `965756`.
4. Submit the number.
5. Click "Cancel order".
6. Click "Cancel".

**Actual result.** The "Order canceled" window is smaller than the "Do you want to cancel the order?" window.

**Expected result.** Both windows are the same size.

**Attachments.** Two screenshots (first window, second window).

---

<a id="ssi-23"></a>

## SSI-23: "Okay" button in the "Order canceled" window is positioned too high

| | |
|---|---|
| **Priority** | Trivial |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** The "Okay" button sits right under the cancellation text, although it should be in the lower part of the window.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `965756`.
4. Submit the number.
5. Click "Cancel order".
6. Click "Cancel".

**Actual result.** The "Okay" button is in the middle of the window, right under the text.

**Expected result.** The "Okay" button is in the lower part of the window.

**Attachments.** Screenshot.

---

<a id="ssi-24"></a>

## SSI-24: "Cancel order" button disappears when the autopilot accepts the order

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** Once the autopilot has accepted the order in its app, the "Cancel order" button disappears from the web app.

**Preconditions**

1. An order has been placed.
2. The autopilot has accepted the order.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `968044`.
4. Submit the number.

**Actual result.** The "Cancel order" button is gone.

**Expected result.** The "Cancel order" button is still shown after the autopilot has accepted the order.

**Attachments.** Screenshot.

---

<a id="ssi-25"></a>

## SSI-25: Canceled order is not removed from the system

| | |
|---|---|
| **Priority** | Critical |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** If the customer cancels an order, the order stays in the system.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `965756`.
4. Submit the number.
5. Cancel the order.
6. Check whether the order still exists in the system.

**Actual result.** The canceled order is still in the system.

**Expected result.** The canceled order is removed from the system.

**Attachments.** Screen recording.

---

<a id="ssi-26"></a>

## SSI-26: User can view a canceled order

| | |
|---|---|
| **Priority** | Critical |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** After canceling an order, the customer can find and open it again, and cancel it one more time.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `965756`.
4. Submit the number.
5. Cancel the order.
6. Enter the number of the canceled order in the search field again: `965756`.

**Actual result.** The canceled order opens and can be canceled again.

**Expected result.** The canceled order cannot be opened.

**Attachments.** Screen recording.

---

<a id="ssi-27"></a>

## SSI-27: Order is considered overdue too early

| | |
|---|---|
| **Priority** | Critical |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** An order is shown as overdue a day too early: already on its delivery date, while the autopilot still has time until 23:59.

**Preconditions**

1. An order has been placed with the delivery date 07.08.2025.
2. The autopilot accepted the order on 07.08.2025 at 14:00.
3. The time on the customer's device is 07.08.2025 14:00.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `619301`.
4. Submit the number.

**Actual result.** The order is shown as overdue although the autopilot still has time until 07.08.2025 23:59.

**Expected result.** The order is shown as overdue only if the autopilot has not completed it by 07.08.2025 23:59.

**Attachments.** Two screenshots (order form, order status page).

---

<a id="ssi-28"></a>

## SSI-28: Caption of the "Okay, let's fly now" status changes after the rental period expires

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** When the rental period ends, the caption of the "Okay, let's fly now" status changes from "Rental ends on…" to the text of the next status, "Rental time has ended".

**Preconditions**

1. An order has been placed with the delivery date 07.08.2025 and the rental period "one day".
2. The autopilot has accepted the order.
3. The autopilot has finished the order.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `203609`.
4. Submit the number.
5. Set the date on the device to 08.08.2025.

**Actual result.** The caption of "Okay, let's fly now" changes to "Rental time has ended".

**Expected result.** The caption stays the same: "Rental ends on <day and month> at <time>".

**Attachments.** Screenshot.

---

<a id="ssi-95"></a>

## SSI-95: "There is no such order" window flashes when the order page is refreshed

| | |
|---|---|
| **Priority** | Medium |
| **Area** | Web, order status page |
| **Environment** | Beskar (1920×1080), Vulptex Browser (1280×720) |

**Description.** When the page with the order data is refreshed, or when switching between windows, the "There is no such order" message flashes for a split second.

**Precondition.** An order has been placed.

**Steps to reproduce**

1. Open the home page.
2. Click "Order Status" in the header.
3. Enter the order number in the search field: `203609`.
4. Submit the number.
5. Refresh the page.

**Actual result.** The "There is no such order" message flashes on refresh and when switching between windows.

**Expected result.** No unrelated messages appear.

**Attachments.** Screen recording.
