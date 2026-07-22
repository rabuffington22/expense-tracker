(function () {
    "use strict";

    var splitSubcategoryCache = null;

    function matchingElements(root, selector) {
        var matches = [];
        if (root && root.nodeType === 1 && root.matches(selector)) {
            matches.push(root);
        }
        if (root && root.querySelectorAll) {
            root.querySelectorAll(selector).forEach(function (element) {
                matches.push(element);
            });
        }
        return matches;
    }

    function transactionPageRoot() {
        return document.querySelector("[data-transaction-page-controller]");
    }

    function allSubcategoriesUrl() {
        var root = transactionPageRoot();
        return root && root.dataset.allSubcategoriesUrl
            ? root.dataset.allSubcategoriesUrl
            : "/transactions/all-subcategories";
    }

    function ensureSubcategoryCache(callback) {
        if (splitSubcategoryCache) {
            callback();
            return;
        }
        window.fetch(allSubcategoriesUrl())
            .then(function (response) { return response.json(); })
            .then(function (data) {
                splitSubcategoryCache = data;
                callback();
            });
    }

    function buildEditableOptions(subcategories) {
        return subcategories.map(function (subcategory) {
            var escaped = escapeHtml(subcategory);
            return '<option value="' + escaped + '">' + escaped + "</option>";
        }).join("") + '<option value="__new__">+ New…</option>';
    }

    function copyTransactionList(button) {
        var rows = document.querySelectorAll("#txn-results tbody tr.txn-clickable");
        if (!rows.length) {
            return;
        }
        var lines = [];
        rows.forEach(function (row, index) {
            var cells = row.querySelectorAll("td");
            var date = cells[0].textContent.trim();
            var description = cells[1].textContent.replace(/\s+/g, " ").trim()
                .replace(/ NEW$/, "").replace(/ \d+%$/, "").trim();
            var rawAmount = cells[2].textContent.trim();
            var amount = rawAmount.replace(/[^$0-9.,]/g, "");
            var direction = rawAmount.indexOf("-") >= 0 ? "paid" : "received";
            lines.push((index + 1) + ".  " + date + "  -  " + description + "  -  " + amount + " " + direction);
        });
        window.navigator.clipboard.writeText(lines.join("\n")).then(function () {
            var original = button.textContent;
            button.textContent = "Copied!";
            window.setTimeout(function () {
                button.textContent = original;
            }, 1500);
        });
    }

    function sortTransactions(column) {
        var sortField = document.getElementById("sort-field");
        var directionField = document.getElementById("dir-field");
        var form = document.getElementById("txn-filter-form");
        if (!sortField || !directionField || !form) {
            return;
        }
        if (sortField.value === column) {
            directionField.value = directionField.value === "asc" ? "desc" : "asc";
        } else {
            sortField.value = column;
            directionField.value = column === "date" ? "desc" : "asc";
        }
        form.requestSubmit();
    }

    function filterSubcategories() {
        var categorySelect = document.getElementById("category_id");
        var subcategorySelect = document.getElementById("subcategory");
        if (!categorySelect || !subcategorySelect) {
            return;
        }
        if (!categorySelect.value) {
            subcategorySelect.innerHTML = '<option value="">All</option>';
            return;
        }
        var categoryName = categorySelect.options[categorySelect.selectedIndex].text;
        ensureSubcategoryCache(function () {
            var current = subcategorySelect.dataset.current || "";
            subcategorySelect.innerHTML = '<option value="">All</option>'
                + (splitSubcategoryCache[categoryName] || []).map(function (subcategory) {
                    var escaped = escapeHtml(subcategory);
                    var selected = subcategory === current ? " selected" : "";
                    return '<option value="' + escaped + '"' + selected + ">" + escaped + "</option>";
                }).join("");
        });
    }

    function loadEditSubcategories(categorySelect, transactionId) {
        var subcategorySelect = document.getElementById("txn-subcat-" + transactionId);
        if (!subcategorySelect) {
            return;
        }
        subcategorySelect.dataset.current = "";
        var input = document.getElementById("txn-subcat-input-" + transactionId);
        if (input) {
            input.hidden = true;
        }
        ensureSubcategoryCache(function () {
            var subcategories = splitSubcategoryCache[categorySelect.value];
            subcategorySelect.innerHTML = subcategories
                ? buildEditableOptions(subcategories)
                : '<option value="Unknown">Unknown</option><option value="__new__">+ Add New…</option>';
        });
    }

    function changeEditSubcategory(select, transactionId) {
        var input = document.getElementById("txn-subcat-input-" + transactionId);
        if (!input) {
            return;
        }
        input.hidden = select.value !== "__new__";
        if (!input.hidden) {
            input.value = "";
            input.focus();
        }
    }

    function addEditSubcategory(transactionId) {
        var input = document.getElementById("txn-subcat-input-" + transactionId);
        var select = document.getElementById("txn-subcat-" + transactionId);
        if (!input || !select || !input.value.trim()) {
            return;
        }
        var option = document.createElement("option");
        option.value = input.value.trim();
        option.textContent = input.value.trim();
        select.insertBefore(option, select.querySelector('option[value="__new__"]'));
        select.value = option.value;
        input.hidden = true;
        input.value = "";
    }

    function suggestCategory(transactionId) {
        var button = document.getElementById("txn-suggest-" + transactionId);
        var root = transactionPageRoot();
        if (!button || !root || !root.dataset.suggestUrlTemplate) {
            return;
        }
        var originalText = button.textContent;
        var reason = document.getElementById("txn-ai-reason-" + transactionId);
        button.textContent = "Thinking…";
        button.disabled = true;
        window.fetch(root.dataset.suggestUrlTemplate.replace("__TXN__", transactionId), { method: "POST" })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.error) {
                    button.textContent = "No idea";
                    button.disabled = false;
                    window.setTimeout(function () { button.textContent = originalText; }, 1500);
                    return;
                }
                var modal = button.closest(".txn-modal-card");
                var categorySelect = modal ? modal.querySelector('select[name="category"]') : null;
                if (categorySelect && data.category) {
                    categorySelect.value = data.category;
                }
                var input = document.getElementById("txn-subcat-input-" + transactionId);
                if (input) {
                    input.hidden = true;
                    input.value = "";
                }
                var subcategorySelect = document.getElementById("txn-subcat-" + transactionId);
                ensureSubcategoryCache(function () {
                    if (subcategorySelect && data.category && splitSubcategoryCache[data.category]) {
                        subcategorySelect.innerHTML = buildEditableOptions(splitSubcategoryCache[data.category]);
                        if (data.subcategory) {
                            subcategorySelect.value = data.subcategory;
                        }
                    }
                    if (reason && data.reason) {
                        reason.textContent = data.reason;
                        reason.hidden = false;
                    }
                    button.textContent = originalText;
                    button.disabled = false;
                });
            })
            .catch(function () {
                button.textContent = "Error";
                button.disabled = false;
                window.setTimeout(function () { button.textContent = originalText; }, 1500);
            });
    }

    function closeTransactionModal() {
        var modal = document.getElementById("txn-modal");
        if (modal) {
            modal.innerHTML = "";
        }
    }

    function closeSubcategoryPopup() {
        var scrim = document.getElementById("dcat-popup-scrim");
        var body = document.getElementById("dcat-popup-body");
        if (scrim) {
            scrim.hidden = true;
        }
        if (body) {
            body.innerHTML = "";
        }
    }

    function closeTodoQueue() {
        var scrim = document.getElementById("tq-modal-scrim");
        var body = document.getElementById("tq-modal-body");
        if (scrim) {
            scrim.hidden = true;
        }
        if (body) {
            body.innerHTML = "";
        }
    }

    function openTodoQueue() {
        var scrim = document.getElementById("tq-modal-scrim");
        var body = document.getElementById("tq-modal-body");
        if (scrim) {
            scrim.hidden = false;
        }
        if (body) {
            body.innerHTML = '<div class="tq-loading">Loading…</div>';
        }
    }

    function splitRoot(element) {
        return element && element.closest
            ? element.closest('[data-transaction-fragment-controller="split-editor"]')
            : null;
    }

    function readJsonElement(id, fallback) {
        var element = document.getElementById(id);
        if (!element) {
            return fallback;
        }
        try {
            var dataSource = element.content || element;
            return JSON.parse(dataSource.textContent);
        } catch (error) {
            return fallback;
        }
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async function loadSplitSubcategories(category) {
        if (splitSubcategoryCache && splitSubcategoryCache[category]) {
            return splitSubcategoryCache[category];
        }
        try {
            var response = await window.fetch(allSubcategoriesUrl());
            var data = await response.json();
            splitSubcategoryCache = data;
            return data[category] || ["General"];
        } catch (error) {
            return ["General"];
        }
    }

    function replaceSubcategoryOptions(select, subcategories, selectedValue) {
        select.innerHTML = "";
        subcategories.forEach(function (subcategory) {
            var option = document.createElement("option");
            option.value = subcategory;
            option.textContent = subcategory;
            option.selected = subcategory === selectedValue;
            select.appendChild(option);
        });
    }

    function updateSplitTotal(root) {
        if (!root) {
            return;
        }
        var total = 0;
        root.querySelectorAll("#split-lines .split-line").forEach(function (line) {
            var amount = line.querySelector(".split-amount");
            total += amount ? parseInt(amount.value, 10) || 0 : 0;
        });
        var display = root.querySelector("#split-total-display");
        var bar = root.querySelector("#split-total-bar");
        if (!display || !bar) {
            return;
        }
        var absoluteCents = Math.abs(total);
        var sign = total < 0 ? "\u2212" : "";
        display.textContent = sign + "$" + (absoluteCents / 100).toFixed(2)
            .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        var parentCents = parseInt(root.dataset.parentCents, 10) || 0;
        if (total === parentCents) {
            bar.style.background = "rgba(48,209,88,0.12)";
            bar.style.color = "var(--green)";
        } else {
            bar.style.background = "rgba(255,69,58,0.10)";
            bar.style.color = "var(--red)";
        }
    }

    async function changeSplitCategory(select) {
        var line = select.closest(".split-line");
        var subcategorySelect = line ? line.querySelector(".split-subcat") : null;
        if (!subcategorySelect) {
            return;
        }
        var subcategories = await loadSplitSubcategories(select.value);
        replaceSubcategoryOptions(subcategorySelect, subcategories, "");
    }

    function addSplitLine(root) {
        var container = root ? root.querySelector("#split-lines") : null;
        if (!container) {
            return;
        }
        var state = root.__transactionSplitState || { categories: [] };
        var index = container.querySelectorAll(".split-line").length;
        var options = state.categories.map(function (category) {
            var escaped = escapeHtml(category);
            return '<option value="' + escaped + '">' + escaped + "</option>";
        }).join("");
        var html = '<div class="split-line" data-idx="' + index + '">'
            + '<div style="display:flex; gap:0.3rem; align-items:center;">'
            + '<input type="number" class="input-sm split-amount" placeholder="Amount (cents)" '
            + 'step="1" style="width:90px; text-align:right;">'
            + '<select class="input-sm split-cat" data-transaction-fragment-change="split-category" '
            + 'style="flex:1;">' + options + "</select>"
            + '<button type="button" class="btn-icon" '
            + 'data-transaction-fragment-action="split-remove-line" title="Remove" '
            + 'style="font-size:0.8rem; opacity:0.6;">&#10005;</button>'
            + "</div>"
            + '<div style="display:flex; gap:0.3rem; margin-top:0.2rem;">'
            + '<input type="text" class="input-sm split-desc" placeholder="Description..." style="flex:1;">'
            + '<select class="input-sm split-subcat" style="width:120px;">'
            + '<option value="General">General</option></select>'
            + "</div></div>";
        container.insertAdjacentHTML("beforeend", html);
    }

    function removeSplitLine(control) {
        var root = splitRoot(control);
        var line = control.closest(".split-line");
        if (line) {
            line.remove();
            updateSplitTotal(root);
        }
    }

    function collectSplits(root) {
        return Array.from(root.querySelectorAll("#split-lines .split-line")).map(function (line) {
            return {
                amount_cents: parseInt(line.querySelector(".split-amount").value, 10) || 0,
                category: line.querySelector(".split-cat").value,
                subcategory: line.querySelector(".split-subcat").value || "General",
                description: line.querySelector(".split-desc").value || "",
            };
        });
    }

    async function saveSplits(root) {
        var transactionId = root.dataset.transactionId;
        try {
            var response = await window.fetch("/transactions/splits/" + transactionId + "/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ splits: collectSplits(root) }),
            });
            var data = await response.json();
            if (!response.ok || data.error) {
                window.alert(data.error || "Failed to save splits");
                return;
            }
            closeTransactionModal();
            var results = document.getElementById("txn-results");
            if (results && window.htmx) {
                window.htmx.trigger(results, "refresh");
            }
            var form = document.querySelector(".txn-filter-bar form");
            if (form) {
                form.requestSubmit();
            }
        } catch (error) {
            window.alert("Error saving splits: " + error.message);
        }
    }

    async function deleteAllSplits(root) {
        if (!window.confirm("Remove all splits and revert to single-category?")) {
            return;
        }
        var transactionId = root.dataset.transactionId;
        try {
            var response = await window.fetch("/transactions/splits/" + transactionId + "/delete", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });
            var data = await response.json();
            if (!response.ok || data.error) {
                window.alert(data.error || "Failed to delete splits");
                return;
            }
            closeTransactionModal();
            var form = document.querySelector(".txn-filter-bar form");
            if (form) {
                form.requestSubmit();
            }
        } catch (error) {
            window.alert("Error: " + error.message);
        }
    }

    async function autoSplit(root) {
        var transactionId = root.dataset.transactionId;
        var button = root.querySelector("#split-auto-btn");
        if (button) {
            button.disabled = true;
            button.textContent = "Generating...";
        }
        try {
            var response = await window.fetch("/transactions/splits/" + transactionId + "/auto", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });
            var data = await response.json();
            if (!response.ok || data.error) {
                window.alert(data.error || "Auto-split failed");
                if (button) {
                    button.disabled = false;
                    button.textContent = "Auto-split from Line Items";
                }
                return;
            }
            if (window.htmx) {
                window.htmx.ajax("GET", "/transactions/splits/" + transactionId, {
                    target: "#txn-modal",
                    swap: "innerHTML",
                });
            }
        } catch (error) {
            window.alert("Error: " + error.message);
            if (button) {
                button.disabled = false;
                button.textContent = "Auto-split from Line Items";
            }
        }
    }

    async function initializeSplitEditor(root) {
        if (root.dataset.transactionFragmentInitialized === "true") {
            return;
        }
        root.dataset.transactionFragmentInitialized = "true";
        root.__transactionSplitState = {
            categories: readJsonElement("split-categories-data", []),
        };
        var lines = Array.from(root.querySelectorAll("#split-lines .split-line"));
        for (var index = 0; index < lines.length; index += 1) {
            var line = lines[index];
            var categorySelect = line.querySelector(".split-cat");
            var subcategorySelect = line.querySelector(".split-subcat");
            if (!categorySelect || !subcategorySelect || !categorySelect.value) {
                continue;
            }
            var currentValue = subcategorySelect.dataset.initial || subcategorySelect.value || "General";
            var subcategories = await loadSplitSubcategories(categorySelect.value);
            replaceSubcategoryOptions(subcategorySelect, subcategories, currentValue);
        }
        updateSplitTotal(root);
    }

    function onClick(event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        var control = event.target.closest("[data-transaction-fragment-action]");
        if (!control) {
            return;
        }
        var action = control.dataset.transactionFragmentAction;
        if (action === "copy-list") {
            copyTransactionList(control);
        } else if (action === "sort") {
            sortTransactions(control.dataset.sortColumn);
        } else if (action === "close-transaction-modal") {
            closeTransactionModal();
        } else if (action === "close-transaction-modal-on-backdrop") {
            if (event.target === control) {
                closeTransactionModal();
            }
        } else if (action === "suggest-category") {
            suggestCategory(control.dataset.transactionId);
        } else if (action === "close-subcategory-popup") {
            closeSubcategoryPopup();
        } else if (action === "close-todo-queue") {
            closeTodoQueue();
        } else if (action === "open-todo-queue") {
            openTodoQueue();
        } else if (action === "close-todo-queue-on-backdrop") {
            if (event.target === control) {
                closeTodoQueue();
            }
        } else if (action === "split-add-line") {
            addSplitLine(splitRoot(control));
        } else if (action === "split-remove-line") {
            removeSplitLine(control);
        } else if (action === "split-save") {
            saveSplits(splitRoot(control));
        } else if (action === "split-delete-all") {
            deleteAllSplits(splitRoot(control));
        } else if (action === "split-auto") {
            autoSplit(splitRoot(control));
        }
    }

    function onChange(event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        var pageControl = event.target.closest("[data-transaction-page-change]");
        if (pageControl && pageControl.dataset.transactionPageChange === "filter-subcategories") {
            filterSubcategories();
            return;
        }
        var control = event.target.closest("[data-transaction-fragment-change]");
        if (!control) {
            return;
        }
        var action = control.dataset.transactionFragmentChange;
        if (action === "edit-category") {
            loadEditSubcategories(control, control.dataset.transactionId);
        } else if (action === "edit-subcategory") {
            changeEditSubcategory(control, control.dataset.transactionId);
        } else if (action === "split-category") {
            changeSplitCategory(control);
        }
    }

    function onKeydown(event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        var control = event.target.closest("[data-transaction-fragment-keydown]");
        if (!control) {
            return;
        }
        if (control.dataset.transactionFragmentKeydown === "add-subcategory" && event.key === "Enter") {
            event.preventDefault();
            addEditSubcategory(control.dataset.transactionId);
        } else if (
            control.dataset.transactionFragmentKeydown === "activate"
            && (event.key === "Enter" || event.key === " ")
        ) {
            event.preventDefault();
            control.click();
        }
    }

    function onInput(event) {
        if (!(event.target instanceof Element) || !event.target.classList.contains("split-amount")) {
            return;
        }
        updateSplitTotal(splitRoot(event.target));
    }

    function onAfterRequest(event) {
        var requestElement = event.detail && event.detail.elt ? event.detail.elt : event.target;
        if (!(requestElement instanceof Element)) {
            return;
        }
        var closeControl = requestElement.closest("[data-close-transaction-modal-after-request]");
        if (closeControl) {
            closeTransactionModal();
        }
    }

    function onConfigRequest(event) {
        var requestElement = event.detail && event.detail.elt;
        var form = requestElement && requestElement.closest ? requestElement.closest("form") : null;
        if (!form) {
            return;
        }
        var select = form.querySelector('select[name="subcategory"]');
        if (!select || select.value !== "__new__") {
            return;
        }
        var input = form.querySelector(".txn-subcat-add");
        if (input && input.value.trim()) {
            var option = document.createElement("option");
            option.value = input.value.trim();
            option.textContent = input.value.trim();
            select.insertBefore(option, select.querySelector('option[value="__new__"]'));
            select.value = option.value;
            input.hidden = true;
            input.value = "";
        } else {
            select.value = "General";
        }
    }

    function initialize(root) {
        matchingElements(root, '[data-transaction-fragment-controller="split-editor"]')
            .forEach(initializeSplitEditor);
        matchingElements(root, "[data-transaction-page-controller]").forEach(function (pageRoot) {
            if (pageRoot.dataset.transactionPageInitialized !== "true") {
                pageRoot.dataset.transactionPageInitialized = "true";
                var categorySelect = document.getElementById("category_id");
                if (categorySelect && categorySelect.value) {
                    filterSubcategories();
                }
            }
        });
    }

    document.addEventListener("click", onClick);
    document.addEventListener("change", onChange);
    document.addEventListener("keydown", onKeydown);
    document.addEventListener("input", onInput);
    document.addEventListener("htmx:afterRequest", onAfterRequest);
    document.addEventListener("htmx:configRequest", onConfigRequest);
    document.body.addEventListener("subcatCacheInvalidate", function () {
        splitSubcategoryCache = null;
    });
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            var scrim = document.getElementById("tq-modal-scrim");
            if (scrim && !scrim.hidden) {
                closeTodoQueue();
            }
        }
    });
    document.addEventListener("htmx:load", function (event) {
        initialize(event.detail && event.detail.elt ? event.detail.elt : event.target);
    });
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            initialize(document);
        });
    } else {
        initialize(document);
    }
})();
