/* Preserve the standalone /k/ category drill-down interaction without inline handlers. */
(function () {
    "use strict";

    document.addEventListener("click", function (event) {
        var control = event.target.closest('[data-kristine-action="toggle-category"]');
        if (!control) {
            return;
        }

        var drill = control.querySelector(".kd-drill");
        if (!drill) {
            return;
        }

        var open = !drill.hidden;
        drill.hidden = open;
        control.classList.toggle("kd-cat-row--open", !open);
    });
})();
