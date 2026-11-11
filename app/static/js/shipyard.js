// Shipyard: tabs with scroll-spy, part cards with a details modal, and the
// build (add by drag or by "Add", one hull, reorder, remove, total, order).
//
// Dragging is built on mousedown / mousemove / mouseup, not on HTML5 Drag
// and Drop, so Selenium ActionChains (click_and_hold -> move_to_element ->
// release) drives it without any JavaScript workaround.
(function () {
  "use strict";

  var configNode = document.getElementById("shipyard-config");
  if (!configNode) return;
  var config = JSON.parse(configNode.textContent);
  var text = config.strings;
  var HULL = "hull";
  var STORAGE_KEY = "shipyard-build";
  var DRAG_THRESHOLD = 4; // px the pointer must travel before a press becomes a drag

  function $(id) {
    return document.getElementById(id);
  }

  function byTestId(root, testId) {
    return root.querySelector('[data-testid="' + testId + '"]');
  }

  var parts = {};
  config.parts.forEach(function (part) {
    parts[part.id] = part;
  });

  var catalog = $("shipyard-catalog");
  var buildNode = $("shipyard-build");
  var itemsNode = $("shipyard-build-items");
  var emptyNode = $("shipyard-build-empty");
  var hullTop = $("shipyard-build-hull-top");
  var hullBottom = $("shipyard-build-hull-bottom");
  var totalNode = $("shipyard-total");
  var errorNode = $("shipyard-order-error");

  // --- build state -------------------------------------------------------------
  // hull: part id or null; items: ids of engines and modules, in build order.
  // Kept in sessionStorage so a guest's build survives the trip to /login.

  var build = load();

  function load() {
    var state = { hull: null, items: [] };
    try {
      var saved = JSON.parse(window.sessionStorage.getItem(STORAGE_KEY));
      if (saved && parts[saved.hull] && parts[saved.hull].category === HULL) state.hull = saved.hull;
      if (saved && Array.isArray(saved.items)) {
        state.items = saved.items.filter(function (id) {
          return parts[id] && parts[id].category !== HULL;
        });
      }
    } catch (error) {
      // No storage or a broken value: start with an empty build.
    }
    return state;
  }

  function save() {
    try {
      window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(build));
    } catch (error) {
      // Storage is a convenience only.
    }
  }

  function total() {
    var sum = build.hull === null ? 0 : parts[build.hull].price * 2; // top and belly plating
    build.items.forEach(function (id) {
      sum += parts[id].price;
    });
    return sum;
  }

  // --- rendering ---------------------------------------------------------------

  function renderHull(node, prefix, template) {
    node.hidden = build.hull === null;
    if (build.hull === null) return;
    var hull = parts[build.hull];
    node.setAttribute("data-part-id", hull.id);
    byTestId(node, prefix + "-name").textContent = template.replace("{name}", hull.name);
    byTestId(node, prefix + "-price").textContent = hull.price;
  }

  function renderItems() {
    itemsNode.textContent = "";
    build.items.forEach(function (id, index) {
      var part = parts[id];
      var testId = "shipyard-build-item-" + index;
      var row = document.createElement("li");
      row.className = "build__item";
      row.id = testId;
      row.setAttribute("data-testid", testId);
      row.setAttribute("data-index", index);
      row.setAttribute("data-part-id", id);

      var name = document.createElement("span");
      name.className = "build__name";
      name.setAttribute("data-testid", testId + "-name");
      name.textContent = part.name;

      var price = document.createElement("span");
      price.className = "build__price";
      var priceValue = document.createElement("span");
      priceValue.setAttribute("data-testid", testId + "-price");
      priceValue.textContent = part.price;
      price.appendChild(priceValue);
      price.appendChild(document.createTextNode(" " + text.credits));

      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "build__remove";
      remove.id = testId + "-remove-button";
      remove.setAttribute("data-testid", remove.id);
      remove.setAttribute("aria-label", text.remove + " " + part.name);
      remove.textContent = "×";

      row.appendChild(name);
      row.appendChild(price);
      row.appendChild(remove);
      itemsNode.appendChild(row);
    });
  }

  function renderCounts() {
    var counts = {};
    if (build.hull !== null) counts[build.hull] = 2;
    build.items.forEach(function (id) {
      counts[id] = (counts[id] || 0) + 1;
    });
    catalog.querySelectorAll(".part").forEach(function (card) {
      var count = counts[card.getAttribute("data-part-id")] || 0;
      var badge = card.querySelector(".part__count");
      badge.textContent = count;
      badge.hidden = count === 0;
    });
  }

  function renderTotal() {
    totalNode.textContent = total();
  }

  // skipTotal is only used by the seeded defect ADD_BUTTON_STALE_TOTAL.
  function render(skipTotal) {
    emptyNode.hidden = build.hull !== null;
    renderHull(hullTop, "shipyard-build-hull-top", text.hullTop);
    renderHull(hullBottom, "shipyard-build-hull-bottom", text.hullBottom);
    renderItems();
    renderCounts();
    if (!skipTotal) renderTotal();
    save();
  }

  function showError(message) {
    errorNode.textContent = message || "";
    errorNode.hidden = !message;
  }

  // --- build commands ----------------------------------------------------------

  function addPart(id, viaButton) {
    var part = parts[id];
    if (!part) return;
    if (part.category === HULL) build.hull = part.id; // a new hull replaces the old one
    else build.items.push(part.id);
    showError(null);
    render(Boolean(viaButton && config.staleTotalOnAdd));
  }

  function removeItem(index) {
    build.items.splice(index, 1);
    render();
  }

  // The dragged item takes the place of the item it was dropped on.
  function moveItem(from, to) {
    if (from === to) return;
    var moved = build.items.splice(from, 1)[0];
    build.items.splice(to, 0, moved);
    render();
  }

  // --- part details modal ----------------------------------------------------------

  var partModal = $("shipyard-part-modal");

  function openPart(id) {
    var part = parts[id];
    partModal.setAttribute("data-part-id", id);
    ["name", "description", "mass", "power", "cargo", "comfort"].forEach(function (field) {
      byTestId(partModal, "shipyard-part-modal-" + field).textContent = part[field];
    });
    window.Modal.open("shipyard-part-modal");
  }

  // --- dragging (mouse events) -------------------------------------------------------

  var drag = null; // { kind: "part" | "item", id, index, x, y, source, ghost }
  var suppressClick = false; // a drag must not also count as a click on the card

  function distance(event) {
    return Math.max(Math.abs(event.clientX - drag.x), Math.abs(event.clientY - drag.y));
  }

  function startGhost(event) {
    var box = drag.source.getBoundingClientRect();
    var ghost = drag.source.cloneNode(true);
    ghost.removeAttribute("id");
    ghost.removeAttribute("data-testid");
    ghost.querySelectorAll("[id], [data-testid]").forEach(function (node) {
      node.removeAttribute("id");
      node.removeAttribute("data-testid");
    });
    ghost.classList.add("drag-ghost");
    ghost.style.width = box.width + "px";
    drag.offsetX = drag.x - box.left;
    drag.offsetY = drag.y - box.top;
    document.body.appendChild(ghost);
    document.body.classList.add("is-dragging");
    drag.source.classList.add("is-drag-source");
    drag.ghost = ghost;
    moveGhost(event);
  }

  function moveGhost(event) {
    drag.ghost.style.left = event.clientX - drag.offsetX + "px";
    drag.ghost.style.top = event.clientY - drag.offsetY + "px";
    var over = elementAt(event);
    buildNode.classList.toggle("build--drop", Boolean(over && over.closest("#shipyard-build")));
  }

  // The element under the pointer; the ghost itself ignores pointer events.
  function elementAt(event) {
    return document.elementFromPoint(event.clientX, event.clientY);
  }

  function endDrag() {
    if (drag.ghost) drag.ghost.remove();
    drag.source.classList.remove("is-drag-source");
    document.body.classList.remove("is-dragging");
    buildNode.classList.remove("build--drop");
    drag = null;
  }

  document.addEventListener("mousedown", function (event) {
    if (event.button !== 0 || event.target.closest("button, a")) return;
    var card = event.target.closest(".part");
    var row = event.target.closest(".build__item");
    if (!card && !row) return;
    drag = card
      ? { kind: "part", id: Number(card.getAttribute("data-part-id")), source: card }
      : { kind: "item", index: Number(row.getAttribute("data-index")), source: row };
    drag.x = event.clientX;
    drag.y = event.clientY;
    suppressClick = false;
    event.preventDefault(); // no text selection, no native image drag
  });

  document.addEventListener("mousemove", function (event) {
    if (!drag) return;
    if (!drag.ghost) {
      if (distance(event) <= DRAG_THRESHOLD) return;
      startGhost(event);
    } else {
      moveGhost(event);
    }
  });

  document.addEventListener("mouseup", function (event) {
    if (!drag) return;
    // Released away from where it was pressed = a drop, even if no mousemove arrived in between.
    var dropped = drag.ghost !== undefined || distance(event) > DRAG_THRESHOLD;
    var finished = drag;
    var target = dropped ? elementAt(event) : null;
    endDrag();
    if (!dropped) return; // a plain click: the click handler opens the details
    suppressClick = true;
    window.setTimeout(function () {
      suppressClick = false;
    }, 0);
    if (!target) return;
    if (finished.kind === "part") {
      if (target.closest("#shipyard-build")) addPart(finished.id);
    } else {
      var row = target.closest(".build__item");
      if (row) moveItem(finished.index, Number(row.getAttribute("data-index")));
    }
  });

  // --- clicks ----------------------------------------------------------------------

  catalog.addEventListener("click", function (event) {
    var card = event.target.closest(".part");
    if (!card) return;
    var id = Number(card.getAttribute("data-part-id"));
    if (event.target.closest("button")) addPart(id, true);
    else if (!suppressClick) openPart(id);
  });

  itemsNode.addEventListener("click", function (event) {
    var button = event.target.closest(".build__remove");
    if (button) removeItem(Number(button.closest(".build__item").getAttribute("data-index")));
  });

  // --- tabs --------------------------------------------------------------------------

  var tabs = Array.prototype.slice.call(document.querySelectorAll(".tab"));

  function sectionOf(tab) {
    return $(tab.getAttribute("data-section"));
  }

  function setActive(active) {
    tabs.forEach(function (tab) {
      var on = tab === active;
      tab.classList.toggle("tab--active", on);
      tab.setAttribute("data-active", String(on));
      tab.setAttribute("aria-selected", String(on));
    });
  }

  // Top of a section inside the scrolling catalog.
  function sectionTop(section) {
    return section.getBoundingClientRect().top - catalog.getBoundingClientRect().top + catalog.scrollTop;
  }

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      catalog.scrollTop = sectionTop(sectionOf(tab));
      setActive(tab);
    });
  });

  // Scroll-spy: the active tab is the last section whose title has reached the top.
  catalog.addEventListener("scroll", function () {
    var active = tabs[0];
    tabs.forEach(function (tab) {
      if (sectionTop(sectionOf(tab)) <= catalog.scrollTop + 8) active = tab;
    });
    setActive(active);
  });

  // --- order ---------------------------------------------------------------------------

  var orderButton = $("shipyard-order-button");
  if (orderButton) {
    orderButton.addEventListener("click", function () {
      if (build.hull === null) {
        showError(text.noHull);
        return;
      }
      showError(null);
      orderButton.disabled = true;
      fetch("/shipyard/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ parts: [build.hull].concat(build.items) }),
      })
        .then(function (response) {
          if (response.status === 401) {
            window.location.assign("/login"); // the session has expired
            return null;
          }
          return response.json().then(function (body) {
            if (!response.ok) throw new Error(body.message || text.orderFailed);
            return body;
          });
        })
        .then(function (order) {
          if (!order) return;
          var modal = $("shipyard-order-modal");
          modal.setAttribute("data-number", order.number);
          $("shipyard-order-modal-text").textContent = text.orderSuccess.replace("{number}", order.number);
          byTestId(modal, "shipyard-order-modal-total").textContent = order.total;
          build = { hull: null, items: [] }; // the ordered build is done; start a new one
          render();
          window.Modal.open("shipyard-order-modal");
        })
        .catch(function (error) {
          showError(error.message || text.orderFailed);
        })
        .then(function () {
          orderButton.disabled = false;
        });
    });
  }

  render();
})();
