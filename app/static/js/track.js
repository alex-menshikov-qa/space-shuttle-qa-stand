// Order status page: "Cancel order" -> confirmation -> PUT /api/v1/orders/cancel.
(function () {
  "use strict";

  var configNode = document.getElementById("track-config");
  var cancelButton = document.getElementById("track-cancel-button");
  if (!configNode || !cancelButton) return;
  var config = JSON.parse(configNode.textContent);
  var errorNode = document.getElementById("track-cancel-error");
  var yesButton = document.getElementById("track-cancel-yes-button");

  function showError(message) {
    errorNode.textContent = message || "";
    errorNode.hidden = !message;
  }

  cancelButton.addEventListener("click", function () {
    showError(null);
    window.Modal.open("track-cancel-modal");
  });

  document.getElementById("track-cancel-no-button").addEventListener("click", function () {
    window.Modal.close("track-cancel-modal");
  });

  yesButton.addEventListener("click", function () {
    yesButton.disabled = true;
    fetch("/api/v1/orders/cancel", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ track: config.track }),
    })
      .then(function (response) {
        return response.json().then(function (body) {
          if (!response.ok) throw new Error(body.message || config.cancelFailed);
        });
      })
      .then(function () {
        window.Modal.close("track-cancel-modal");
        window.Modal.open("track-canceled-modal");
      })
      .catch(function (error) {
        showError(error.message || config.cancelFailed);
      })
      .then(function () {
        yesButton.disabled = false;
      });
  });
})();
