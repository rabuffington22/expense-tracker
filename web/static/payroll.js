/* Payroll page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    var currentEmployeeId = null;
    var roleColors = {};

    function root() {
        return document.querySelector("[data-payroll-controller]");
    }

    function element(id) {
        return document.getElementById(id);
    }

    function parseRoleColors() {
        var carrier = element("pr-role-colors-data");
        if (!carrier) {
            return {};
        }
        try {
            return JSON.parse(carrier.content.textContent);
        } catch (_error) {
            return {};
        }
    }

    function showAddForm() {
        var form = element("pr-add-form");
        form.hidden = false;
        form.querySelector('input[name="name"]').focus();
    }

    function hideAddForm() {
        element("pr-add-form").hidden = true;
    }

    function closeDetail() {
        element("pr-detail-scrim").hidden = true;
        currentEmployeeId = null;
    }

    function formatRate(cents, payType, suffix) {
        var options = payType === "salary"
            ? {maximumFractionDigits: 0}
            : {minimumFractionDigits: 2, maximumFractionDigits: 2};
        return "$" + (cents / 100).toLocaleString("en-US", options) + suffix;
    }

    function formatHistoryAmount(cents) {
        return "$" + (cents / 100).toLocaleString(
            "en-US",
            {maximumFractionDigits: 2}
        );
    }

    function renderPayHistory(changes) {
        var historyBox = element("pr-detail-history-box");
        var timeline = element("pr-detail-timeline");
        timeline.replaceChildren();
        if (!changes || !changes.length) {
            historyBox.hidden = true;
            return;
        }

        changes.forEach(function (change) {
            var row = document.createElement("div");
            var date = document.createElement("span");
            var summary = document.createElement("span");
            var percentage = change.pct_change !== null
                ? " (" + (change.pct_change > 0 ? "+" : "") + change.pct_change + "%)"
                : "";
            row.className = "pr-timeline-item";
            date.className = "pr-timeline-date";
            summary.className = "pr-timeline-change";
            date.textContent = change.effective_date;
            summary.textContent =
                formatHistoryAmount(change.old_rate_cents)
                + " \u2192 "
                + formatHistoryAmount(change.new_rate_cents)
                + percentage;
            row.append(date, summary);
            if (change.notes) {
                var notes = document.createElement("span");
                notes.className = "pr-timeline-notes";
                notes.textContent = change.notes;
                row.appendChild(notes);
            }
            timeline.appendChild(row);
        });
        historyBox.hidden = false;
    }

    function renderPaychecks(paycheckRows) {
        var paycheckBox = element("pr-detail-paychecks-box");
        var paychecks = element("pr-detail-paychecks");
        paychecks.replaceChildren();
        if (!paycheckRows || !paycheckRows.length) {
            paycheckBox.hidden = true;
            return;
        }

        paycheckRows.forEach(function (paycheck) {
            var row = document.createElement("div");
            var date = document.createElement("span");
            var amount = document.createElement("span");
            row.className = "pr-paycheck-item";
            date.className = "pr-paycheck-date";
            amount.className = "pr-paycheck-amount";
            date.textContent = paycheck.paycheck_date;
            amount.textContent = formatRate(paycheck.amount_cents, "salary", "");
            row.append(date, amount);
            paychecks.appendChild(row);
        });
        paycheckBox.hidden = false;
    }

    function populateDetail(data) {
        element("pr-detail-name").textContent = data.name;

        var roleBadge = element("pr-detail-role-badge");
        roleBadge.textContent = data.role;
        roleBadge.style.background = roleColors[data.role] || "#98989d";

        var statusBadge = element("pr-detail-status-badge");
        statusBadge.textContent = data.status;
        statusBadge.className = "pr-status-badge pr-status-" + data.status;

        var rateSuffix = data.pay_type === "salary" ? "/yr" : "/hr";
        element("pr-detail-rate").textContent =
            formatRate(data.pay_rate_cents, data.pay_type, rateSuffix);
        element("pr-detail-hire").textContent = data.hire_date || "\u2014";

        var days = element("pr-detail-days-raise");
        if (data.days_since_raise !== null) {
            days.textContent = data.days_since_raise + " days";
            days.className = "pr-detail-stat-value"
                + (data.days_since_raise > 365 ? " pr-raise-flag--stale" : "");
        } else {
            days.textContent = "No raises on file";
            days.className = "pr-detail-stat-value pr-raise-flag--none";
        }

        var peer = "No comparable peers";
        if (data.peer_avg_cents !== null) {
            peer = formatRate(data.peer_avg_cents, data.pay_type, rateSuffix);
        }
        element("pr-detail-peer-avg").textContent = peer;

        renderPayHistory(data.pay_changes);
        renderPaychecks(data.recent_paychecks);

        element("pr-edit-form").action = "/payroll/employees/update/" + data.id;
        element("pr-edit-name").value = data.name;
        element("pr-edit-role").value = data.role;
        element("pr-edit-pay-type").value = data.pay_type;
        element("pr-edit-pay-rate").value =
            (data.pay_rate_cents / 100).toLocaleString("en-US", {
                minimumFractionDigits: data.pay_type === "salary" ? 0 : 2,
                maximumFractionDigits: data.pay_type === "salary" ? 0 : 2,
                useGrouping: true,
            });
        element("pr-edit-hire-date").value = data.hire_date || "";
        element("pr-edit-status").value = data.status;
        element("pr-edit-notes").value = data.notes || "";
        element("pr-delete-form").action = "/payroll/employees/delete/" + data.id;
    }

    function openDetail(employeeId) {
        currentEmployeeId = employeeId;
        element("pr-detail-scrim").hidden = false;
        fetch("/payroll/employees/detail/" + employeeId)
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (currentEmployeeId === employeeId) {
                    populateDetail(data);
                }
            })
            .catch(function (error) {
                console.error("Detail fetch error:", error);
            });
    }

    function loadSpending(period) {
        fetch("/payroll/spending?spending_period=" + encodeURIComponent(period))
            .then(function (response) {
                return response.text();
            })
            .then(function (html) {
                element("pr-spending-body").innerHTML = html;
            });
    }

    function toggleNewRole(control) {
        var roleSelect = control.parentElement.querySelector(".pr-select--role");
        if (roleSelect) {
            roleSelect.style.display = control.value === "new" ? "" : "none";
        }
    }

    function runAction(control) {
        var action = control.dataset.payrollAction;
        if (action === "show-add") {
            showAddForm();
        } else if (action === "hide-add") {
            hideAddForm();
        } else if (action === "open-detail") {
            openDetail(control.dataset.employeeId);
        } else if (action === "close-detail") {
            closeDetail();
        } else if (action === "load-spending") {
            loadSpending(control.value);
        } else if (action === "toggle-new-role") {
            toggleNewRole(control);
        }
    }

    function initialize() {
        var controller = root();
        if (!controller || controller.dataset.initialized === "true") {
            return;
        }
        roleColors = parseRoleColors();
        controller.dataset.initialized = "true";
    }

    document.addEventListener("click", function (event) {
        if (!(event.target instanceof Element) || !root()) {
            return;
        }
        var control = event.target.closest("[data-payroll-action]");
        if (control && root().contains(control)) {
            runAction(control);
            return;
        }
        if (event.target === element("pr-detail-scrim")) {
            closeDetail();
        }
    });

    document.addEventListener("change", function (event) {
        if (
            event.target instanceof Element
            && root()
            && root().contains(event.target)
            && event.target.matches(
                '[data-payroll-action="load-spending"], '
                + '[data-payroll-action="toggle-new-role"]'
            )
        ) {
            runAction(event.target);
        }
    });

    document.addEventListener("keydown", function (event) {
        if (!root() || !(event.target instanceof Element)) {
            return;
        }
        if (event.key === "Escape" && !element("pr-detail-scrim").hidden) {
            closeDetail();
            return;
        }
        var row = event.target.closest(
            '[data-payroll-action="open-detail"]'
        );
        if (
            row
            && event.target === row
            && (event.key === "Enter" || event.key === " ")
        ) {
            event.preventDefault();
            openDetail(row.dataset.employeeId);
        }
    });

    document.addEventListener("submit", function (event) {
        if (!(event.target instanceof HTMLFormElement) || !root()) {
            return;
        }
        if (event.target.id === "pr-edit-form") {
            var rateInput = element("pr-edit-pay-rate");
            rateInput.value = rateInput.value.replace(/,/g, "");
        }
        if (
            event.target.dataset.payrollConfirm
            && !window.confirm(event.target.dataset.payrollConfirm)
        ) {
            event.preventDefault();
        }
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
}());
