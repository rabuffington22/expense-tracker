/* Waterfall page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    var activeRow = null;
    var targetMode = "revenue";

    function replaceAnimation(element, propertyName, keyframes, options) {
        if (element[propertyName]) {
            element[propertyName].cancel();
        }
        element[propertyName] = element.animate(keyframes, options);
        return element[propertyName];
    }

    function applyBarGeometry(bar) {
        var left = Number.parseFloat(bar.dataset.barLeft || "");
        var width = Number.parseFloat(bar.dataset.barWidth || "");
        if (!Number.isFinite(left) || !Number.isFinite(width)) {
            return;
        }
        var animation = replaceAnimation(
            bar,
            "_waterfallGeometryAnimation",
            [{left: left + "%", width: width + "%"}],
            {duration: 1, fill: "forwards"}
        );
        animation.finish();
    }

    function controllerRoot() {
        return document.querySelector("[data-waterfall-controller]");
    }

    function formatDollars(cents) {
        var dollars = Math.round(Math.abs(cents) / 100);
        return "$" + dollars.toLocaleString("en-US");
    }

    function hideTip() {
        var tip = document.getElementById("wf-tip");
        if (tip) {
            tip.setAttribute("hidden", "");
        }
        activeRow = null;
    }

    function showTip(row, event) {
        var tip = document.getElementById("wf-tip");
        if (!tip) {
            return;
        }

        var data;
        try {
            data = JSON.parse(row.getAttribute("data-tip"));
        } catch (error) {
            return;
        }
        if (!data || !data.length) {
            return;
        }
        if (activeRow === row) {
            hideTip();
            return;
        }

        activeRow = row;
        tip.replaceChildren();
        data.forEach(function (item) {
            var tipRow = document.createElement("div");
            var category = document.createElement("span");
            var value = document.createElement("span");
            tipRow.className = "wf-tip-row";
            category.className = "wf-tip-cat";
            value.className = "wf-tip-val";
            category.textContent = item.c;
            value.textContent = formatDollars(item.v);
            tipRow.append(category, value);
            tip.appendChild(tipRow);
        });

        tip.removeAttribute("hidden");
        var tipWidth = tip.offsetWidth;
        var tipHeight = tip.offsetHeight;
        var left = event.clientX + 12;
        if (left + tipWidth > window.innerWidth - 8) {
            left = event.clientX - tipWidth - 12;
        }
        if (left < 8) {
            left = 8;
        }

        var top = event.clientY + 8;
        if (top + tipHeight > window.innerHeight - 8) {
            top = event.clientY - tipHeight - 8;
        }
        if (top < 8) {
            top = 8;
        }
        var positionAnimation = replaceAnimation(
            tip,
            "_waterfallPositionAnimation",
            [{left: left + "px", top: top + "px"}],
            {duration: 1, fill: "forwards"}
        );
        positionAnimation.finish();
    }

    function animateBars(view) {
        if (!view) {
            return;
        }
        view.querySelectorAll(".wf-wf-bar-anim").forEach(function (bar) {
            applyBarGeometry(bar);
            var delay = parseInt(bar.dataset.delay || "0", 10);
            replaceAnimation(
                bar,
                "_waterfallEntranceAnimation",
                [
                    {clipPath: "inset(0 100% 0 0)", opacity: 0.2},
                    {clipPath: "inset(0 0 0 0)", opacity: 1},
                ],
                {
                    duration: 500,
                    delay: delay * 150,
                    easing: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
                    fill: "both",
                }
            );
        });
    }

    function switchView(mode) {
        var actualView = document.getElementById("wf-view-actual");
        var targetView = document.getElementById("wf-view-target");
        var actualButton = document.getElementById("wf-seg-actual");
        var targetButton = document.getElementById("wf-seg-target");
        if (!actualView || !targetView || !actualButton || !targetButton) {
            return;
        }

        var showTarget = mode === "target";
        actualView.hidden = showTarget;
        targetView.hidden = !showTarget;
        actualButton.classList.toggle("wf-seg-btn--active", !showTarget);
        targetButton.classList.toggle("wf-seg-btn--active", showTarget);
        animateBars(showTarget ? targetView : actualView);
    }

    function toggleBreakdown(section) {
        var detail = document.getElementById("wf-detail-" + section);
        var chevron = document.getElementById("wf-chevron-" + section);
        if (!detail || !chevron) {
            return;
        }
        detail.hidden = !detail.hidden;
        chevron.classList.toggle("wf-chevron--open", !detail.hidden);
    }

    function setMode(mode) {
        targetMode = mode;
        document.querySelectorAll(
            '[data-waterfall-action="set-mode"]'
        ).forEach(function (button) {
            button.classList.toggle(
                "wf-seg-btn--active",
                button.dataset.mode === mode
            );
        });
        var input = document.getElementById("wf-input-value");
        if (input) {
            input.value = "";
            input.focus();
        }
    }

    function applyTargets() {
        var input = document.getElementById("wf-input-value");
        if (!input) {
            return;
        }
        var value = input.value.replace(/[^0-9.]/g, "");
        if (!value) {
            return;
        }

        var url = new URL(window.location);
        url.searchParams.delete("target_revenue");
        url.searchParams.delete("take_home");
        if (targetMode === "takehome") {
            url.searchParams.set("take_home", value);
            url.searchParams.set("mode", "takehome");
        } else {
            url.searchParams.set("target_revenue", value);
            url.searchParams.set("mode", "revenue");
        }
        window.location = url.toString();
    }

    function applyTaxRate(input) {
        var value = input.value.trim();
        if (!value) {
            return;
        }
        var url = new URL(window.location);
        url.searchParams.set("tax_rate", value);
        window.location = url.toString();
    }

    function initialize() {
        var root = controllerRoot();
        if (!root || root.dataset.initialized === "true") {
            return;
        }
        root.dataset.initialized = "true";
        targetMode = root.dataset.targetMode || "revenue";

        var params = new URLSearchParams(window.location.search);
        var showTarget = params.has("target_revenue")
            || params.has("take_home")
            || params.has("mode");
        if (showTarget) {
            switchView("target");
        } else {
            animateBars(document.getElementById("wf-view-actual"));
        }
    }

    document.addEventListener("click", function (event) {
        var root = controllerRoot();
        if (!root || !(event.target instanceof Element)) {
            return;
        }

        var row = event.target.closest(".wf-wf-row[data-tip]");
        if (row) {
            showTip(row, event);
            return;
        }

        var control = event.target.closest("[data-waterfall-action]");
        if (control) {
            var action = control.dataset.waterfallAction;
            if (action === "switch-view") {
                switchView(control.dataset.view);
            } else if (action === "toggle-breakdown") {
                toggleBreakdown(control.dataset.section);
            } else if (action === "set-mode") {
                setMode(control.dataset.mode);
            }
        }

        if (!event.target.closest(".wf-tip")) {
            hideTip();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Enter" || !(event.target instanceof Element)) {
            return;
        }
        var action = event.target.dataset.waterfallEnter;
        if (!action || !controllerRoot()) {
            return;
        }
        event.preventDefault();
        if (action === "apply-targets") {
            applyTargets();
        } else if (action === "apply-tax-rate") {
            applyTaxRate(event.target);
        }
    });

    document.addEventListener("DOMContentLoaded", initialize);
}());
