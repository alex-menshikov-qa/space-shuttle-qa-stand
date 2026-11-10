// Header: the "Order Status" button reveals the order-number search.
// The search itself is a plain GET form to /track?t=<number>, so both the
// "Go!" button and Enter submit it.
(function () {
  "use strict";

  var button = document.getElementById("header-status-button");
  var form = document.getElementById("header-status-form");
  if (!button || !form) return;

  button.addEventListener("click", function () {
    var open = form.hidden;
    form.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
    if (open) form.querySelector("input").focus();
  });
})();
