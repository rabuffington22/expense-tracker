/* Connected Accounts page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    function controllerRoot() {
        return document.querySelector("[data-plaid-controller]");
    }

    function primaryButton() {
        return document.getElementById("connect-btn");
    }

    function resetConnectButton() {
        var button = primaryButton();
        if (button) {
            button.disabled = false;
            button.textContent = "Connect a Bank";
        }
    }

    function connectAccount() {
        var root = controllerRoot();
        var button = primaryButton();
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
                        return fetch(root.dataset.exchangeTokenUrl, {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify({
                                public_token: publicToken,
                                institution_name: metadata.institution
                                    ? metadata.institution.name
                                    : "",
                                institution_id: metadata.institution
                                    ? metadata.institution.institution_id
                                    : "",
                            }),
                        })
                            .then(function (response) {
                                return response.json();
                            })
                            .then(function (result) {
                                if (result.error) {
                                    window.alert(
                                        "Error connecting: " + result.error
                                    );
                                } else {
                                    window.location.reload();
                                }
                            });
                    },
                    onExit: function (error) {
                        resetConnectButton();
                        if (error) {
                            console.error("Plaid Link exit error:", error);
                        }
                    },
                });
                handler.open();
            })
            .catch(function (error) {
                window.alert(
                    "Failed to start Plaid Link: " + error.message
                );
                resetConnectButton();
            });
    }

    document.addEventListener("click", function (event) {
        if (!(event.target instanceof Element) || !controllerRoot()) {
            return;
        }
        var control = event.target.closest('[data-plaid-action="connect"]');
        if (control) {
            connectAccount();
        }
    });

    document.addEventListener("submit", function (event) {
        if (
            !(event.target instanceof HTMLFormElement)
            || !controllerRoot()
            || !event.target.dataset.plaidConfirm
        ) {
            return;
        }
        if (!window.confirm(event.target.dataset.plaidConfirm)) {
            event.preventDefault();
        }
    });

    if (controllerRoot()) {
        controllerRoot().dataset.initialized = "true";
    }
})();
