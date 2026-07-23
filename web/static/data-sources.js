/* Data Sources page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    function controllerRoot() {
        return document.querySelector("[data-data-sources-controller]");
    }

    function element(id) {
        return document.getElementById(id);
    }

    function resetConnectButton() {
        var button = element("ds-connect-btn");
        if (button) {
            button.disabled = false;
            button.textContent = "Connect Payment Account";
        }
    }

    function updateVendorLabel(select) {
        var label = element("fileLabel");
        if (!label) {
            return;
        }
        label.textContent = select.value === "Amazon"
            ? "Amazon Order History CSV"
            : "Henry Schein Items Purchased XLSX";
    }

    function orderDates() {
        var carrier = element("ds-order-dates-data");
        if (!carrier) {
            return [];
        }
        try {
            return JSON.parse(carrier.content.textContent);
        } catch (error) {
            console.error("Data Sources order-date parse error:", error);
            return [];
        }
    }

    function updateSaveCount() {
        var fromElement = element("filterFrom");
        var toElement = element("filterTo");
        var button = element("saveBtn");
        if (!fromElement || !toElement || !button) {
            return;
        }

        var from = fromElement.value;
        var to = toElement.value;
        var count = orderDates().filter(function (dateValue) {
            var date = String(dateValue).slice(0, 10);
            return date >= from && date <= to;
        }).length;
        button.textContent = "Save " + count + " orders";
    }

    function connectAccount() {
        var root = controllerRoot();
        var button = element("ds-connect-btn");
        if (!root || !button) {
            return;
        }

        button.disabled = true;
        button.textContent = "Loading\u2026";

        fetch(root.dataset.linkTokenUrl, {method: "POST"})
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.error) {
                    window.alert("Error: " + data.error);
                    resetConnectButton();
                    return;
                }

                var handler = window.Plaid.create({
                    token: data.link_token,
                    onSuccess: function (publicToken, metadata) {
                        var institution = metadata.institution || {};
                        var form = new FormData();
                        form.append("public_token", publicToken);
                        form.append("institution_name", institution.name || "");
                        form.append(
                            "institution_id",
                            institution.institution_id || ""
                        );

                        fetch(root.dataset.exchangeTokenUrl, {
                            method: "POST",
                            body: form,
                        })
                            .then(function (response) {
                                return response.json();
                            })
                            .then(function (result) {
                                if (result.error) {
                                    window.alert("Error: " + result.error);
                                }
                                window.location.reload();
                            });
                    },
                    onExit: function () {
                        resetConnectButton();
                    },
                });
                handler.open();
            })
            .catch(function (error) {
                window.alert("Failed to start Plaid Link: " + error);
                resetConnectButton();
            });
    }

    document.addEventListener("change", function (event) {
        if (!(event.target instanceof Element) || !controllerRoot()) {
            return;
        }
        if (event.target.matches('[data-data-sources-action="select-vendor"]')) {
            updateVendorLabel(event.target);
        } else if (
            event.target.matches('[data-data-sources-action="filter-date"]')
        ) {
            updateSaveCount();
        }
    });

    document.addEventListener("click", function (event) {
        if (!(event.target instanceof Element) || !controllerRoot()) {
            return;
        }
        var control = event.target.closest("[data-data-sources-action]");
        if (
            control
            && control.dataset.dataSourcesAction === "connect-account"
        ) {
            connectAccount();
        }
    });

    document.addEventListener("submit", function (event) {
        if (
            !(event.target instanceof HTMLFormElement)
            || !controllerRoot()
            || !event.target.dataset.dataSourcesConfirm
        ) {
            return;
        }
        if (!window.confirm(event.target.dataset.dataSourcesConfirm)) {
            event.preventDefault();
        }
    });

    if (controllerRoot()) {
        controllerRoot().dataset.initialized = "true";
    }
})();
