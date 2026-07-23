/* Initialize standalone error/offline documents before their inline styles paint. */
(function () {
    "use strict";

    var theme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", theme);

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
        meta.content = theme === "light" ? "#F7F9FC" : "#000000";
    }

    document.addEventListener("click", function (event) {
        var control = event.target.closest("[data-standalone-action]");
        if (!control) {
            return;
        }

        if (control.dataset.standaloneAction === "retry") {
            window.location.reload();
        }
    });
})();
