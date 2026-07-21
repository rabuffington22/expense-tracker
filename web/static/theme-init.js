/* Apply the stored theme before the main stylesheet paints. */
(function () {
    "use strict";

    var theme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", theme);

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
        meta.content = theme === "light" ? "#F7F9FC" : "#000000";
    }
})();
