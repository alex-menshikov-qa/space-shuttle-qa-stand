// Client-side form checks. Rules, limits and messages come from the server
// (#validation-rules, built by app/validation.py), so the browser, the web
// forms and the API always apply exactly the same validation.
//
// A form opts in with `data-validate`; each input names its check in
// `data-rule`; the error goes into the element its aria-describedby points to.
(function () {
  "use strict";

  var rulesNode = document.getElementById("validation-rules");
  if (!rulesNode) return;
  var rules = JSON.parse(rulesNode.textContent);
  var msg = rules.messages;
  var emailRe = new RegExp(rules.emailPattern);

  // Count characters (code points), like Python's len().
  function length(value) {
    return Array.from(value).length;
  }

  var checks = {
    name: function (value) {
      value = value.trim();
      if (!value) return msg.nameRequired;
      if (length(value) > rules.nameMax) return msg.nameTooLong;
      return null;
    },
    email: function (value) {
      value = value.trim().toLowerCase();
      if (!value) return msg.emailRequired;
      if (length(value) > rules.emailMax) return msg.emailTooLong;
      if (!emailRe.test(value)) return msg.emailInvalid;
      return null;
    },
    password: function (value) {
      if (!value) return msg.passwordRequired;
      if (length(value) < rules.passwordMin) return msg.passwordInvalid;
      if (length(value) > rules.passwordMax) return msg.passwordTooLong;
      return null;
    },
    "email-required": function (value) {
      return value.trim() ? null : msg.emailRequired;
    },
    "password-required": function (value) {
      return value ? null : msg.passwordRequired;
    },
  };

  function showError(input, message) {
    var errorNode = document.getElementById(input.getAttribute("aria-describedby"));
    input.classList.toggle("field__input--invalid", Boolean(message));
    if (message) input.setAttribute("aria-invalid", "true");
    else input.removeAttribute("aria-invalid");
    if (errorNode) {
      errorNode.textContent = message || "";
      errorNode.hidden = !message;
    }
  }

  document.querySelectorAll("form[data-validate]").forEach(function (form) {
    var inputs = form.querySelectorAll("[data-rule]");

    form.addEventListener("submit", function (event) {
      var valid = true;
      inputs.forEach(function (input) {
        var check = checks[input.dataset.rule];
        var message = check ? check(input.value) : null;
        showError(input, message);
        if (message) valid = false;
      });
      if (!valid) event.preventDefault();
    });

    inputs.forEach(function (input) {
      input.addEventListener("input", function () {
        showError(input, null);
      });
    });
  });
})();
