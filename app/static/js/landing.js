// Landing page: FAQ accordion (one panel open at a time) and the cookie banner.
(function () {
  "use strict";

  var buttons = Array.prototype.slice.call(document.querySelectorAll(".accordion__button"));

  function setOpen(button, open) {
    button.setAttribute("aria-expanded", String(open));
    document.getElementById(button.getAttribute("aria-controls")).hidden = !open;
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var open = button.getAttribute("aria-expanded") !== "true";
      buttons.forEach(function (other) {
        setOpen(other, false);
      });
      setOpen(button, open);
    });
  });

  var banner = document.getElementById("home-cookie-banner");
  var accept = document.getElementById("home-cookie-accept-button");
  if (banner && accept) {
    accept.addEventListener("click", function () {
      // Remembered for a year; the server stops rendering the banner.
      document.cookie = "cookies_accepted=1; path=/; max-age=31536000; samesite=lax";
      banner.hidden = true;
    });
  }
})();
