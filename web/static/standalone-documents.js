/* Initialize standalone error/offline documents before their inline styles paint. */
(function () {
    "use strict";

    var theme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", theme);

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
        meta.content = theme === "light" ? "#F7F9FC" : "#000000";
    }

    function setRetryState(control, status, message, busy) {
        status.textContent = message;
        control.disabled = busy;
        if (busy) {
            control.setAttribute("aria-busy", "true");
        } else {
            control.removeAttribute("aria-busy");
        }
    }

    async function retryConnection(control) {
        var status = document.querySelector("[data-offline-retry-status]");
        var retryUrl = control.dataset.retryUrl;
        if (!status || !retryUrl) {
            return;
        }

        setRetryState(control, status, "Checking your connection\u2026", true);

        try {
            var response = await fetch(retryUrl, {
                cache: "no-store",
                headers: {"Accept": "application/json"}
            });
            if (!response.ok) {
                throw new Error("Health check failed");
            }
            setRetryState(
                control,
                status,
                "Connection restored. Reloading\u2026",
                true
            );
            window.requestAnimationFrame(function () {
                window.location.reload();
            });
        } catch (_error) {
            setRetryState(
                control,
                status,
                "Still offline. Check your connection and try again.",
                false
            );
        }
    }

    document.addEventListener("click", function (event) {
        var control = event.target.closest("[data-standalone-action]");
        if (!control) {
            return;
        }

        if (control.dataset.standaloneAction === "retry") {
            event.preventDefault();
            retryConnection(control);
        }
    });
})();
