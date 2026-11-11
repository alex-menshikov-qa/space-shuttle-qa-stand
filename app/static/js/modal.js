// Modal windows (see templates/partials/modal.html).
// Modal.open(id) / Modal.close(id). A modal marked data-dismissible also
// closes on Esc, on a click on the backdrop and on any [data-modal-close].
window.Modal = (function () {
  "use strict";

  function open(id) {
    document.getElementById(id).hidden = false;
  }

  function close(id) {
    document.getElementById(id).hidden = true;
  }

  document.addEventListener("click", function (event) {
    var modal = event.target.closest(".modal");
    if (!modal || !modal.hasAttribute("data-dismissible")) return;
    if (event.target === modal || event.target.closest("[data-modal-close]")) modal.hidden = true;
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    document.querySelectorAll(".modal[data-dismissible]:not([hidden])").forEach(function (modal) {
      modal.hidden = true;
    });
  });

  return { open: open, close: close };
})();
