// Order form: two steps on one page, a station search, a date picker, a
// rental-period dropdown and the confirmation modals.
//
// Rules and messages come from the server (#validation-rules, built by
// app/validation.py); "today" and the earliest delivery date come from
// #order-config. The API validates everything again on submit.
(function () {
  "use strict";

  var form = document.getElementById("order-form");
  if (!form) return;
  var rules = JSON.parse(document.getElementById("validation-rules").textContent).order;
  var config = JSON.parse(document.getElementById("order-config").textContent);
  var msg = rules.messages;

  function $(id) {
    return document.getElementById(id);
  }

  var title = $("order-title");
  var step1 = $("order-step-1");
  var step2 = $("order-step-2");
  var inputs = {
    firstName: $("order-name-input"),
    lastName: $("order-last-name-input"),
    address: $("order-address-input"),
    station: $("order-station-input"),
    phone: $("order-phone-input"),
    deliveryDate: $("order-date-input"),
    comment: $("order-comment-input"),
  };
  var periodButton = $("order-period-dropdown");
  var periodValue = $("order-period-value");
  var periodList = $("order-period-list");
  var stationList = $("order-station-list");
  var formError = $("order-form-error");

  var state = { station: null, rentTime: null };

  // --- errors ---------------------------------------------------------------

  // Border: red with an error, black for a checked non-empty value, gray otherwise.
  function showError(control, message, checked) {
    var errorNode = $(control.getAttribute("aria-describedby"));
    control.classList.toggle("field__input--invalid", Boolean(message));
    control.classList.toggle("field__input--valid", !message && Boolean(checked));
    if (message) control.setAttribute("aria-invalid", "true");
    else control.removeAttribute("aria-invalid");
    errorNode.textContent = message || "";
    errorNode.hidden = !message;
  }

  function showFormError(message) {
    formError.textContent = message || "";
    formError.hidden = !message;
  }

  // --- dates ----------------------------------------------------------------
  // Dates are handled as ISO strings (YYYY-MM-DD), which compare correctly as
  // text, and are shown / typed as DD.MM.YYYY.

  function pad(number) {
    return (number < 10 ? "0" : "") + number;
  }

  function iso(year, month, day) {
    return year + "-" + pad(month) + "-" + pad(day);
  }

  function display(isoDate) {
    var parts = isoDate.split("-");
    return parts[2] + "." + parts[1] + "." + parts[0];
  }

  // "DD.MM.YYYY" of a real calendar date -> ISO string, otherwise null.
  function parseTyped(text) {
    var match = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(text.trim());
    if (!match) return null;
    var day = Number(match[1]);
    var month = Number(match[2]);
    var year = Number(match[3]);
    var date = new Date(Date.UTC(year, month - 1, day));
    var real =
      date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
    return real && year >= 1000 ? iso(year, month, day) : null;
  }

  // --- validation -------------------------------------------------------------

  function matches(pattern, value) {
    return new RegExp(pattern).test(value);
  }

  var checks = {
    firstName: function () {
      return matches(rules.namePattern, inputs.firstName.value) ? null : msg.firstName;
    },
    lastName: function () {
      return matches(rules.lastNamePattern, inputs.lastName.value) ? null : msg.lastName;
    },
    address: function () {
      return matches(rules.addressPattern, inputs.address.value.trim()) ? null : msg.address;
    },
    station: function () {
      return state.station === null ? msg.station : null;
    },
    phone: function () {
      return matches(rules.phonePattern, inputs.phone.value) ? null : msg.phone;
    },
    deliveryDate: function () {
      var date = parseTyped(inputs.deliveryDate.value);
      return date !== null && date >= config.minDate ? null : msg.deliveryDate;
    },
    rentTime: function () {
      return state.rentTime === null ? msg.rentTime : null;
    },
    comment: function () {
      return matches(rules.commentPattern, inputs.comment.value) ? null : msg.comment;
    },
  };

  function control(field) {
    return field === "rentTime" ? periodButton : inputs[field];
  }

  function filled(field) {
    return field === "rentTime" ? state.rentTime !== null : inputs[field].value !== "";
  }

  function validate(fields) {
    var valid = true;
    fields.forEach(function (field) {
      var message = checks[field]();
      showError(control(field), message, filled(field));
      if (message) valid = false;
    });
    return valid;
  }

  var STEP_1 = ["firstName", "lastName", "address", "station", "phone"];
  var STEP_2 = ["deliveryDate", "rentTime", "comment"];

  // Text fields: check on leaving the field, clear the error while typing.
  ["firstName", "lastName", "address", "phone", "comment"].forEach(function (field) {
    inputs[field].addEventListener("blur", function () {
      if (field === "address") inputs.address.value = inputs.address.value.trim();
      validate([field]);
    });
    inputs[field].addEventListener("input", function () {
      showError(inputs[field], null);
    });
  });

  // --- steps ------------------------------------------------------------------

  function showStep(number) {
    step1.hidden = number !== 1;
    step2.hidden = number !== 2;
    title.textContent = title.getAttribute("data-step-" + number);
    window.scrollTo(0, 0);
  }

  $("order-next-button").addEventListener("click", function () {
    inputs.address.value = inputs.address.value.trim();
    if (validate(STEP_1)) showStep(2);
  });

  $("order-back-button").addEventListener("click", function () {
    showStep(1);
  });

  // Enter in a text field must not submit the form natively.
  form.addEventListener("submit", function (event) {
    event.preventDefault();
  });

  // --- station search -----------------------------------------------------------

  var stationRequest = 0;

  function hideStations() {
    stationList.hidden = true;
  }

  function renderStations(stations) {
    stationList.textContent = "";
    stations.forEach(function (station) {
      var item = document.createElement("li");
      item.className = "options__item";
      item.setAttribute("role", "option");
      item.id = "order-station-option-" + station.number;
      item.setAttribute("data-testid", item.id);
      item.setAttribute("data-number", station.number);
      var dot = document.createElement("span");
      dot.className = "station-dot";
      dot.style.background = station.color;
      dot.setAttribute("data-color", station.color);
      var name = document.createElement("span");
      name.textContent = station.name;
      item.appendChild(dot);
      item.appendChild(name);
      stationList.appendChild(item);
    });
    stationList.hidden = stations.length === 0;
  }

  function searchStations() {
    var request = ++stationRequest;
    fetch("/api/v1/stations/search?s=" + encodeURIComponent(inputs.station.value.trim()))
      .then(function (response) {
        return response.json();
      })
      .then(function (body) {
        // Ignore answers that arrive after a newer request or after the field lost focus.
        if (request === stationRequest && document.activeElement === inputs.station) {
          renderStations(body.stations);
        }
      })
      .catch(hideStations);
  }

  inputs.station.addEventListener("focus", searchStations);
  inputs.station.addEventListener("input", function () {
    state.station = null; // typing after a pick un-picks the station
    showError(inputs.station, null);
    searchStations();
  });
  inputs.station.addEventListener("blur", function () {
    stationRequest++;
    hideStations();
    validate(["station"]);
  });
  // Keep the focus in the input while an option is being clicked.
  stationList.addEventListener("mousedown", function (event) {
    event.preventDefault();
  });
  stationList.addEventListener("click", function (event) {
    var item = event.target.closest(".options__item");
    if (!item) return;
    state.station = Number(item.getAttribute("data-number"));
    inputs.station.value = item.textContent;
    showError(inputs.station, null, true);
    hideStations();
  });

  // --- date picker --------------------------------------------------------------

  var picker = $("order-datepicker");
  var pickerDays = $("order-datepicker-days");
  var pickerMonth = $("order-datepicker-month");
  // Monday first; the last two are the weekend.
  // #if FORM_CALENDAR_LOWERCASE
  var WEEKDAYS = ["mo", "tu", "we", "th", "fr", "sa", "su"];
  var MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
  ];
  // #else
  var WEEKDAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"];
  var MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  // #endif
  var shown = { year: Number(config.today.slice(0, 4)), month: Number(config.today.slice(5, 7)) };

  function renderPicker() {
    var selected = parseTyped(inputs.deliveryDate.value);
    pickerMonth.textContent = MONTHS[shown.month - 1] + " " + shown.year;
    pickerDays.textContent = "";
    WEEKDAYS.forEach(function (name, index) {
      var cell = document.createElement("span");
      cell.className = "datepicker__weekday" + (index > 4 ? " datepicker__weekday--weekend" : "");
      cell.textContent = name;
      pickerDays.appendChild(cell);
    });
    var first = new Date(Date.UTC(shown.year, shown.month - 1, 1));
    var offset = (first.getUTCDay() + 6) % 7; // Monday first
    var days = new Date(Date.UTC(shown.year, shown.month, 0)).getUTCDate();
    for (var blank = 0; blank < offset; blank++) {
      pickerDays.appendChild(document.createElement("span"));
    }
    for (var day = 1; day <= days; day++) {
      var date = iso(shown.year, shown.month, day);
      var button = document.createElement("button");
      button.type = "button";
      button.className = "datepicker__day";
      if ((offset + day - 1) % 7 > 4) button.classList.add("datepicker__day--weekend");
      button.textContent = day;
      button.id = "order-datepicker-day-" + date;
      button.setAttribute("data-testid", button.id);
      button.setAttribute("data-date", date);
      button.disabled = date < config.minDate;
      if (date === config.today) button.classList.add("datepicker__day--today");
      if (date === selected) {
        button.classList.add("datepicker__day--selected");
        button.setAttribute("aria-selected", "true");
      }
      pickerDays.appendChild(button);
    }
  }

  function openPicker() {
    // Opens on the month of the typed date if there is one, else the current month.
    var typed = parseTyped(inputs.deliveryDate.value);
    var base = typed || config.today;
    shown = { year: Number(base.slice(0, 4)), month: Number(base.slice(5, 7)) };
    renderPicker();
    picker.hidden = false;
  }

  function closePicker() {
    picker.hidden = true;
  }

  function moveMonth(step) {
    shown.month += step;
    if (shown.month < 1) {
      shown.month = 12;
      shown.year--;
    } else if (shown.month > 12) {
      shown.month = 1;
      shown.year++;
    }
    renderPicker();
  }

  inputs.deliveryDate.addEventListener("focus", openPicker);
  inputs.deliveryDate.addEventListener("click", function () {
    if (picker.hidden) openPicker();
  });
  inputs.deliveryDate.addEventListener("input", function () {
    showError(inputs.deliveryDate, null);
    var typed = parseTyped(inputs.deliveryDate.value);
    if (typed) {
      // A complete date leaves the calendar nothing to offer: close it, so it
      // does not cover the fields below. A click on the field opens it again.
      closePicker();
      return;
    }
    if (!picker.hidden) renderPicker();
  });
  inputs.deliveryDate.addEventListener("keydown", function (event) {
    if (event.key === "Enter" || event.key === "Escape") closePicker();
  });
  inputs.deliveryDate.addEventListener("blur", function () {
    closePicker();
    validate(["deliveryDate"]);
  });
  // Clicks inside the picker must not take the focus from the input.
  picker.addEventListener("mousedown", function (event) {
    event.preventDefault();
  });
  $("order-datepicker-prev-button").addEventListener("click", function () {
    moveMonth(-1);
  });
  $("order-datepicker-next-button").addEventListener("click", function () {
    moveMonth(1);
  });
  pickerDays.addEventListener("click", function (event) {
    var button = event.target.closest(".datepicker__day");
    if (!button || button.disabled) return;
    inputs.deliveryDate.value = display(button.getAttribute("data-date"));
    showError(inputs.deliveryDate, null, true);
    closePicker();
    // #if FORM_DATE_PICK_NO_HIGHLIGHT
    inputs.deliveryDate.blur();
    // #endif
  });

  // --- rental period dropdown -----------------------------------------------------

  function setPeriodOpen(open) {
    periodList.hidden = !open;
    periodButton.setAttribute("aria-expanded", String(open));
  }

  periodButton.addEventListener("click", function () {
    setPeriodOpen(periodList.hidden);
  });
  periodList.addEventListener("click", function (event) {
    var item = event.target.closest(".options__item");
    if (!item) return;
    state.rentTime = Number(item.getAttribute("data-value"));
    periodValue.textContent = item.textContent;
    periodValue.classList.remove("dropdown__value--empty");
    periodList.querySelectorAll(".options__item").forEach(function (other) {
      other.setAttribute("aria-selected", String(other === item));
    });
    showError(periodButton, null, true);
    setPeriodOpen(false);
  });
  document.addEventListener("click", function (event) {
    if (!event.target.closest("#order-period-dropdown, #order-period-list")) setPeriodOpen(false);
  });

  // --- submit -------------------------------------------------------------------

  var yesButton = $("order-confirm-yes-button");
  var successText = $("order-success-text");
  var successTitle = $("order-success-title");

  $("order-submit-button").addEventListener("click", function () {
    showFormError(null);
    if (validate(STEP_2)) window.Modal.open("order-confirm-modal");
  });

  $("order-confirm-no-button").addEventListener("click", function () {
    window.Modal.close("order-confirm-modal");
  });

  function payload() {
    var colors = [];
    form.querySelectorAll('input[name="color"]:checked').forEach(function (box) {
      colors.push(box.value);
    });
    return {
      firstName: inputs.firstName.value,
      lastName: inputs.lastName.value,
      address: inputs.address.value.trim(),
      station: state.station,
      phone: inputs.phone.value,
      rentTime: state.rentTime,
      deliveryDate: parseTyped(inputs.deliveryDate.value),
      comment: inputs.comment.value,
      color: colors,
    };
  }

  // #if FORM_CONFIRM_YES_DEAD
  // #else
  yesButton.addEventListener("click", function () {
    yesButton.disabled = true;
    fetch("/api/v1/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload()),
    })
      .then(function (response) {
        return response.json().then(function (body) {
          if (!response.ok) throw new Error(body.message || msg.submitFailed);
          return body.track;
        });
      })
      .then(function (track) {
        window.Modal.close("order-confirm-modal");
        successTitle.textContent = successTitle.getAttribute("data-template").replace("{track}", track);
        successText.setAttribute("data-track", track);
        $("order-view-status-button").href = "/track?t=" + track;
        window.Modal.open("order-success-modal");
      })
      .catch(function (error) {
        window.Modal.close("order-confirm-modal");
        showFormError(error.message || msg.submitFailed);
      })
      .then(function () {
        yesButton.disabled = false;
      });
  });
  // #endif
})();
