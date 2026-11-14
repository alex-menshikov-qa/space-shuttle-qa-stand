// Header: the "Order Status" button reveals the order-number search.
// The search itself is a plain GET form to /track?t=<number> with a single
// text field, so Enter submits it; it has no button.
(function () {
  "use strict";

  var button = document.getElementById("header-status-button");
  var form = document.getElementById("header-status-form");
  if (!button || !form) return;

  // #if STATUS_SEARCH_ENTER
  form.querySelector("input").addEventListener("keydown", function (event) {
    if (event.key === "Enter") event.preventDefault();
  });
  // #endif

  button.addEventListener("click", function () {
    var open = form.hidden;
    form.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    if (open) form.querySelector("input").focus();
  });
})();
