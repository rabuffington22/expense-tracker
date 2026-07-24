/* Subscription page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    var suggestions = [];
    var currentSubscriptionId = null;
    var currentMerchant = "";

    function controllerRoot() {
        return document.querySelector("[data-subscriptions-controller]");
    }

    function element(id) {
        return document.getElementById(id);
    }

    function endpoint(name, id) {
        var root = controllerRoot();
        if (!root) {
            return "";
        }
        var template = root.dataset[name + "Url"] || "";
        return template.replace(/0$/, String(id));
    }

    function formatDollars(cents) {
        return "$" + (cents / 100).toFixed(2).replace(/\.00$/, "");
    }

    function frequencySuffix(frequency) {
        var suffixes = {
            weekly: "/wk",
            biweekly: "/2wk",
            monthly: "/mo",
            quarterly: "/qtr",
            annual: "/yr",
        };
        return suffixes[frequency] || "";
    }

    function setEmpty(container, message) {
        var empty = document.createElement("div");
        empty.className = "sub-detail-empty";
        empty.textContent = message;
        container.replaceChildren(empty);
    }

    function populateCharges(data) {
        element("sub-detail-count").textContent = data.occurrence_count || "\u2014";
        element("sub-detail-period").textContent =
            data.first_date_display && data.last_date_display
                ? data.first_date_display + " \u2013 " + data.last_date_display
                : "\u2014";

        var range = element("sub-detail-amount-range");
        if (data.min_amount_cents != null && data.max_amount_cents != null) {
            if (data.min_amount_cents === data.max_amount_cents) {
                range.textContent = formatDollars(data.amount_cents) + " (consistent)";
            } else {
                range.textContent =
                    formatDollars(data.min_amount_cents)
                    + " \u2013 "
                    + formatDollars(data.max_amount_cents);
            }
        } else {
            range.textContent = data.amount_cents
                ? formatDollars(data.amount_cents)
                : "\u2014";
        }

        var chargesContainer = element("sub-detail-charges");
        var charges = data.recent_charges || [];
        if (!charges.length) {
            setEmpty(chargesContainer, "No charge data available");
            return;
        }

        chargesContainer.replaceChildren();
        charges.forEach(function (charge) {
            var row = document.createElement("div");
            var date = document.createElement("span");
            var amount = document.createElement("span");
            row.className = "sub-detail-charge";
            date.className = "sub-detail-charge-date";
            amount.className = "sub-detail-charge-amount";
            date.textContent = charge.date;
            amount.textContent = formatDollars(charge.amount_cents);
            row.append(date, amount);
            chargesContainer.appendChild(row);
        });
    }

    function openSuggestion(index) {
        var suggestion = suggestions[index];
        if (!suggestion) {
            return;
        }

        element("sub-detail-title").textContent = suggestion.merchant_canonical;
        element("sub-detail-meta").textContent =
            formatDollars(suggestion.amount_cents)
            + frequencySuffix(suggestion.frequency)
            + "  \u00b7  "
            + suggestion.cadence_label;
        populateCharges(suggestion);

        element("sub-detail-tips-section").hidden = true;
        element("sub-detail-timeline-section").hidden = true;
        element("sub-detail-edit-footer").hidden = true;

        var footer = element("sub-detail-footer");
        footer.hidden = false;
        footer.replaceChildren();
        var sourceRow = controllerRoot().querySelector(
            '[data-suggestion-index="' + index + '"]'
        );
        if (sourceRow) {
            sourceRow.querySelectorAll(".sub-suggest-form").forEach(function (form) {
                var clone = form.cloneNode(true);
                var button = clone.querySelector("button");
                clone.className = "sub-detail-form";
                if (button && button.classList.contains("sub-suggest-btn--accept")) {
                    button.className = "btn btn-sm btn-primary";
                    button.textContent = "Add to Watchlist";
                } else if (button) {
                    button.className = "btn btn-sm btn-secondary";
                    button.textContent = "Dismiss";
                }
                footer.appendChild(clone);
            });
        }

        element("sub-detail-scrim").hidden = false;
    }

    function renderAccountInfoField(container, field) {
        var row = document.createElement("div");
        var type = document.createElement("span");
        var value = document.createElement("span");
        var remove = document.createElement("button");

        row.className = "sub-acctinfo-field";
        row.dataset.fieldId = field.id;
        type.className = "sub-acctinfo-field-type";
        value.className = "sub-acctinfo-field-value";
        remove.type = "button";
        remove.className = "sub-acctinfo-delete-btn";
        remove.dataset.subscriptionsAction = "delete-account-info";
        remove.dataset.fieldId = field.id;
        remove.title = "Remove";
        remove.setAttribute("aria-label", "Remove field");
        remove.textContent = "\u00d7";
        type.textContent = field.field_type;
        value.textContent = field.field_value;
        row.append(type, value, remove);
        container.appendChild(row);
    }

    function renderTimeline(entries) {
        var section = element("sub-detail-timeline-section");
        var container = element("sub-detail-timeline");
        container.replaceChildren();
        if (!entries || !entries.length) {
            section.hidden = true;
            return;
        }

        entries.forEach(function (entry) {
            var row = document.createElement("div");
            var date = document.createElement("span");
            var action = document.createElement("span");
            var label = entry.action;

            if (entry.action === "created") {
                label = "Added to watchlist";
            } else if (entry.action === "status_changed") {
                label = "Status: " + (entry.detail || "");
            } else if (entry.action === "note_added") {
                label = "Note: " + (entry.detail || "");
            } else if (entry.action === "tips_generated") {
                label = "Cancellation tips generated";
            }

            row.className = "sub-detail-timeline-entry";
            date.className = "sub-timeline-date";
            action.className = "sub-timeline-action";
            date.textContent = entry.date_display;
            action.textContent = label;
            row.append(date, action);
            container.appendChild(row);
        });
        section.hidden = false;
    }

    function openWatchlist(subscriptionId) {
        element("sub-detail-title").textContent = "Loading\u2026";
        element("sub-detail-meta").textContent = "";
        element("sub-detail-count").textContent = "";
        element("sub-detail-period").textContent = "";
        element("sub-detail-amount-range").textContent = "";
        element("sub-detail-charges").replaceChildren();
        element("sub-detail-tips-section").hidden = true;
        element("sub-detail-timeline-section").hidden = true;
        element("sub-detail-payment-row").hidden = true;
        element("sub-detail-acctinfo-section").hidden = true;
        element("sub-detail-footer").hidden = true;
        element("sub-detail-edit-footer").hidden = true;
        element("sub-detail-scrim").hidden = false;

        fetch(endpoint("detail", subscriptionId))
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.error) {
                    closeDetail();
                    return;
                }

                currentSubscriptionId = data.id;
                currentMerchant = data.merchant;
                element("sub-detail-title").textContent = data.merchant;
                var meta = [];
                if (data.amount_cents) {
                    meta.push(
                        formatDollars(data.amount_cents)
                        + frequencySuffix(data.frequency)
                    );
                }
                if (data.cadence_label) {
                    meta.push(data.cadence_label);
                }
                element("sub-detail-meta").textContent = meta.join("  \u00b7  ");

                if (data.charges) {
                    populateCharges(data.charges);
                } else {
                    element("sub-detail-count").textContent = "\u2014";
                    element("sub-detail-period").textContent = "\u2014";
                    element("sub-detail-amount-range").textContent = "\u2014";
                    setEmpty(
                        element("sub-detail-charges"),
                        "No matching transactions found"
                    );
                }

                var paymentRow = element("sub-detail-payment-row");
                if (data.payment_method) {
                    element("sub-detail-payment").textContent = data.payment_method;
                    paymentRow.hidden = false;
                } else {
                    paymentRow.hidden = true;
                }

                var accountContainer = element("sub-detail-acctinfo-fields");
                accountContainer.replaceChildren();
                (data.account_info || []).forEach(function (field) {
                    renderAccountInfoField(accountContainer, field);
                });
                element("sub-detail-acctinfo-section").hidden = false;
                element("sub-acctinfo-value").value = "";
                element("sub-acctinfo-type").selectedIndex = 0;

                var tips = element("sub-detail-tips");
                var tipsButton = element("sub-tips-fetch-btn");
                if (data.cancellation_tips) {
                    tips.textContent = data.cancellation_tips;
                    tipsButton.hidden = true;
                } else {
                    tips.textContent = "";
                    tipsButton.hidden = false;
                }
                element("sub-detail-tips-section").hidden = false;
                renderTimeline(data.timeline);

                element("sub-detail-footer").hidden = true;
                element("sub-detail-edit-footer").hidden = false;
                element("sub-detail-edit-form").action = endpoint("update", data.id);
                element("sub-detail-status").value = data.status || "watching";
                element("sub-detail-notes").value = data.notes || "";
                element("sub-detail-delete-form").action = endpoint("delete", data.id);
            })
            .catch(closeDetail);
    }

    function fetchTips() {
        if (!currentSubscriptionId) {
            return;
        }
        var button = element("sub-tips-fetch-btn");
        button.textContent = "Loading\u2026";
        button.disabled = true;
        fetch(endpoint("tips", currentSubscriptionId), {method: "POST"})
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.tips) {
                    element("sub-detail-tips").textContent = data.tips;
                    button.hidden = true;
                } else {
                    button.textContent = "Tips unavailable";
                }
            })
            .catch(function () {
                button.textContent = "Tips unavailable";
            });
    }

    function addAccountInfo() {
        if (!currentSubscriptionId) {
            return;
        }
        var type = element("sub-acctinfo-type");
        var value = element("sub-acctinfo-value");
        var fieldValue = value.value.trim();
        if (!fieldValue) {
            value.focus();
            return;
        }

        var button = element("sub-acctinfo-add-btn");
        button.disabled = true;
        fetch(endpoint("accountAdd", currentSubscriptionId), {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                field_type: type.value,
                field_value: fieldValue,
            }),
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                button.disabled = false;
                if (data.error) {
                    return;
                }
                renderAccountInfoField(element("sub-detail-acctinfo-fields"), data);
                value.value = "";
                value.focus();
            })
            .catch(function () {
                button.disabled = false;
            });
    }

    function deleteAccountInfo(fieldId, row) {
        fetch(endpoint("accountDelete", fieldId), {method: "POST"})
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.ok) {
                    row.remove();
                }
            });
    }

    function copyShareText() {
        if (!currentSubscriptionId) {
            return;
        }
        var button = element("sub-phone-btn");
        var originalText = button.innerHTML;
        button.textContent = "Building\u2026";
        button.disabled = true;

        function restoreCopiedState() {
            button.textContent = "\u2705 Copied!";
            window.setTimeout(function () {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 2000);
        }

        function restoreButton() {
            button.innerHTML = originalText;
            button.disabled = false;
        }

        fetch(endpoint("share", currentSubscriptionId))
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (!data.text) {
                    restoreButton();
                    return;
                }
                navigator.clipboard.writeText(data.text)
                    .then(restoreCopiedState)
                    .catch(function () {
                        var textarea = document.createElement("textarea");
                        textarea.value = data.text;
                        textarea.className = "u-clipboard-proxy";
                        document.body.appendChild(textarea);
                        textarea.select();
                        document.execCommand("copy");
                        textarea.remove();
                        restoreCopiedState();
                    });
            })
            .catch(restoreButton);
    }

    function removeWatchlistItem() {
        if (!currentSubscriptionId) {
            return;
        }
        if (window.confirm("Remove " + currentMerchant + " from watchlist?")) {
            element("sub-detail-delete-form").submit();
        }
    }

    function closeDetail() {
        element("sub-detail-scrim").hidden = true;
    }

    function showAdd() {
        element("sub-add-trigger").hidden = true;
        element("sub-add-panel").hidden = false;
        var input = document.querySelector(
            '#sub-add-panel input[name="merchant"]'
        );
        if (input) {
            input.focus();
        }
    }

    function hideAdd() {
        element("sub-add-trigger").hidden = false;
        element("sub-add-panel").hidden = true;
        document.querySelector("#sub-add-panel form").reset();
    }

    function toggleDismissed(control) {
        var list = element("sub-dismissed-list");
        list.hidden = !list.hidden;
        control.setAttribute("aria-expanded", String(!list.hidden));
    }

    function runAction(control) {
        var action = control.dataset.subscriptionsAction;
        if (action === "open-suggestion") {
            openSuggestion(Number(control.dataset.suggestionIndex));
        } else if (action === "open-watchlist") {
            openWatchlist(Number(control.dataset.subId));
        } else if (action === "show-add") {
            showAdd();
        } else if (action === "hide-add") {
            hideAdd();
        } else if (action === "toggle-dismissed") {
            toggleDismissed(control);
        } else if (action === "close-detail") {
            closeDetail();
        } else if (action === "add-account-info") {
            addAccountInfo();
        } else if (action === "delete-account-info") {
            deleteAccountInfo(
                Number(control.dataset.fieldId),
                control.closest(".sub-acctinfo-field")
            );
        } else if (action === "fetch-tips") {
            fetchTips();
        } else if (action === "copy-share") {
            copyShareText();
        } else if (action === "remove-watchlist") {
            removeWatchlistItem();
        }
    }

    function initialize() {
        var root = controllerRoot();
        if (!root || root.dataset.initialized === "true") {
            return;
        }
        root.dataset.initialized = "true";
        var dataSource = element("sub-suggestions-data");
        if (dataSource) {
            try {
                suggestions = JSON.parse(
                    (dataSource.content || dataSource).textContent
                );
            } catch (error) {
                suggestions = [];
            }
        }
    }

    document.addEventListener("click", function (event) {
        var root = controllerRoot();
        if (!root || !(event.target instanceof Element)) {
            return;
        }
        var control = event.target.closest("[data-subscriptions-action]");
        if (!control || !root.contains(control)) {
            return;
        }
        if (
            control.dataset.subscriptionsAction === "open-suggestion"
            && event.target.closest(".sub-suggest-form")
        ) {
            return;
        }
        if (
            control.dataset.subscriptionsAction === "close-on-scrim"
            && event.target !== control
        ) {
            return;
        }
        if (control.dataset.subscriptionsAction === "close-on-scrim") {
            closeDetail();
            return;
        }
        runAction(control);
    });

    document.addEventListener("keydown", function (event) {
        var root = controllerRoot();
        if (!root || !(event.target instanceof Element)) {
            return;
        }
        if (event.key === "Escape" && !element("sub-detail-scrim").hidden) {
            closeDetail();
            return;
        }
        var row = event.target.closest("[data-subscriptions-row]");
        if (
            row
            && event.target === row
            && (event.key === "Enter" || event.key === " ")
        ) {
            event.preventDefault();
            runAction(row);
            return;
        }
        if (
            event.key === "Enter"
            && event.target.dataset.subscriptionsEnterAction === "add-account-info"
        ) {
            event.preventDefault();
            addAccountInfo();
        }
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
}());
