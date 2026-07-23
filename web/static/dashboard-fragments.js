(function () {
    "use strict";

    var loadingMarkup = '<p class="text-sm text-muted fragment-loading-state">Loading\u2026</p>';

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

    function setBoundedPercentClass(element, value) {
        var percent = Math.max(0, Math.min(100, Math.round(value)));
        Array.from(element.classList).forEach(function (className) {
            if (/^u-pct-\d+$/.test(className)) {
                element.classList.remove(className);
            }
        });
        element.classList.add("u-pct-" + percent);
    }

    function toggleAiDetail(row) {
        var detail = row.nextElementSibling;
        if (!detail) {
            return;
        }
        var show = detail.hidden;
        detail.hidden = !show;
        var chevron = row.querySelector(".iu-chevron");
        if (chevron) {
            chevron.classList.toggle("iu-chevron--open", show);
        }
    }

    function toggleCategoryGroup(row) {
        var subs = row.nextElementSibling;
        var subsClass = row.dataset.fragmentSubsClass;
        if (!subs || !subsClass || !subs.classList.contains(subsClass)) {
            return;
        }
        var open = !subs.hidden;
        subs.hidden = open;
        row.classList.toggle(row.dataset.fragmentOpenClass, !open);
    }

    function modalElements(kind) {
        var prefix = kind === "detail" ? "detail-iu" : "iu";
        return {
            scrim: document.getElementById(prefix + "-modal-scrim"),
            body: document.getElementById(prefix + "-modal-body"),
        };
    }

    function openInsightModal(kind) {
        var elements = modalElements(kind);
        if (!elements.scrim || !elements.body) {
            return;
        }
        elements.scrim.hidden = false;
        elements.body.innerHTML = loadingMarkup;
    }

    function closeInsightModal(kind) {
        var elements = modalElements(kind);
        if (!elements.scrim || !elements.body) {
            return;
        }
        elements.scrim.hidden = true;
        elements.body.innerHTML = "";
    }

    function dismissInsight(key) {
        var row = null;
        document.querySelectorAll("[data-insight-key]").forEach(function (candidate) {
            if (!row && candidate.dataset.insightKey === key) {
                row = candidate;
            }
        });
        if (row) {
            row.hidden = true;
            var section = row.closest(".iu-section");
            if (section) {
                var visible = Array.from(section.querySelectorAll(".iu-row")).some(function (candidate) {
                    return !candidate.hidden;
                });
                var message = section.querySelector(".iu-caught-up");
                if (message && !visible) {
                    message.hidden = false;
                }
            }
        }
        closeInsightModal("compare");
        closeInsightModal("detail");
    }

    function toggleReportGroup(row) {
        var target = document.getElementById(row.dataset.target || "");
        if (!target) {
            return;
        }
        target.hidden = !target.hidden;
        var chevron = row.querySelector(".rpt-tax-chevron");
        if (chevron) {
            chevron.textContent = target.hidden ? "\u203A" : "\u2304";
        }
    }

    function showMoreReportRows(button) {
        var target = document.getElementById(button.dataset.target || "rpt-more-merchants");
        if (target) {
            target.hidden = false;
        }
        button.remove();
    }

    function loadDashboardCompare() {
        if (!window.htmx) {
            return;
        }
        document.querySelectorAll('#dash-compare [hx-trigger="compare-load"]').forEach(function (panel) {
            window.htmx.trigger(panel, "compare-load");
        });
    }

    function setDashboardView(view) {
        var compare = document.getElementById("dash-compare");
        var details = document.getElementById("dash-details");
        if (!compare || !details) {
            return;
        }
        compare.hidden = view !== "compare";
        details.hidden = view !== "details";
        document.querySelectorAll(".dash-view-toggle .seg-item").forEach(function (button) {
            button.classList.toggle("active", button.dataset.view === view);
        });
        window.localStorage.setItem("dash_view", view);
        if (view === "compare" && !document.getElementById("kpi-left")) {
            loadDashboardCompare();
        }
    }

    function openSubcategoryPopup() {
        var scrim = document.getElementById("dcat-popup-scrim");
        var body = document.getElementById("dcat-popup-body");
        if (scrim) {
            scrim.hidden = false;
        }
        if (body) {
            body.innerHTML = '<div class="tq-loading">Loading…</div>';
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

    function updateReportPage(form) {
        var select = form ? form.querySelector("#report_type") : null;
        if (!select) {
            return;
        }
        document.querySelectorAll(".rpt-desc").forEach(function (description) {
            description.hidden = description.dataset.report !== select.value;
        });
        var qboButton = form.querySelector(".rpt-export-qbo");
        if (qboButton) {
            qboButton.hidden = select.value !== "transactions";
        }
    }

    function closeReportExportMenu() {
        var menu = document.querySelector(".rpt-export-menu");
        if (menu) {
            menu.hidden = true;
        }
    }

    function toggleReportExport(button) {
        var wrap = button.closest(".rpt-export-wrap");
        var menu = wrap ? wrap.querySelector(".rpt-export-menu") : null;
        if (menu) {
            menu.hidden = !menu.hidden;
        }
    }

    function exportReport(button) {
        var form = button.closest("[data-report-page-controller]");
        if (!form || !form.dataset.exportUrl) {
            return;
        }
        var params = new URLSearchParams(new FormData(form));
        params.set("format", button.dataset.exportFormat || "csv");
        closeReportExportMenu();
        window.location.href = form.dataset.exportUrl + "?" + params.toString();
    }

    function onClick(event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        var pageControl = event.target.closest("[data-dashboard-page-action]");
        if (pageControl) {
            var pageAction = pageControl.dataset.dashboardPageAction;
            if (pageAction === "set-view") {
                setDashboardView(pageControl.dataset.view || "details");
            } else if (pageAction === "close-subcategory-popup") {
                closeSubcategoryPopup();
            } else if (pageAction === "close-subcategory-popup-on-backdrop") {
                if (event.target === pageControl) {
                    closeSubcategoryPopup();
                }
            } else if (pageAction === "toggle-export") {
                toggleReportExport(pageControl);
            } else if (pageAction === "export") {
                exportReport(pageControl);
            }
            return;
        }
        var reportWrap = document.querySelector(".rpt-export-wrap");
        if (reportWrap && !reportWrap.contains(event.target)) {
            closeReportExportMenu();
        }
        var control = event.target.closest("[data-fragment-action]");
        if (!control) {
            return;
        }
        var action = control.dataset.fragmentAction;
        if (action === "toggle-ai") {
            toggleAiDetail(control);
        } else if (action === "toggle-category") {
            toggleCategoryGroup(control);
        } else if (action === "open-subcategory-popup") {
            openSubcategoryPopup();
        } else if (action === "open-insight-modal") {
            openInsightModal(control.dataset.fragmentModal || "compare");
        } else if (action === "close-insight-modal") {
            if (control.classList.contains("tq-modal-scrim") && event.target !== control) {
                return;
            }
            closeInsightModal(control.dataset.fragmentModal || "compare");
        } else if (action === "dismiss-insight") {
            dismissInsight(control.dataset.insightKey || "");
        } else if (action === "toggle-report-group") {
            toggleReportGroup(control);
        } else if (action === "show-more-report-rows") {
            showMoreReportRows(control);
        }
    }

    function onChange(event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        var control = event.target.closest("[data-dashboard-page-change]");
        if (control && control.dataset.dashboardPageChange === "report-type") {
            updateReportPage(control.closest("[data-report-page-controller]"));
        }
    }

    function updateReportLoading(event, loading) {
        var target = event.detail && event.detail.target;
        if (target && target.id === "rpt-results") {
            target.classList.toggle("rpt-loading-state", loading);
        }
    }

    function niceTicks(maxCents) {
        var maxDollars = maxCents / 100;
        var rough = Math.max(maxDollars / 4, 1);
        var magnitude = Math.pow(10, Math.floor(Math.log10(rough)));
        var ratio = rough / magnitude;
        var step = ratio <= 1.5 ? magnitude : ratio <= 3.5 ? 2 * magnitude : 5 * magnitude;
        step = Math.max(step, 1);
        var axisMax = Math.ceil(maxDollars / step) * step;
        var ticks = [];
        for (var value = axisMax; value >= 0; value = Math.round((value - step) * 100) / 100) {
            var label;
            if (value >= 1000) {
                label = "$" + (value / 1000).toFixed(value % 1000 ? 1 : 0) + "K";
            } else if (value >= 1) {
                label = "$" + value.toLocaleString("en-US", { maximumFractionDigits: 0 });
            } else {
                label = "$0";
            }
            ticks.push({ label: label, value: value });
            if (value <= 0) {
                break;
            }
        }
        return { ticks: ticks, axisMaxCents: Math.round(axisMax * 100) };
    }

    function initializeIncomeExpenseChart(chart) {
        if (chart.dataset.fragmentInitialized === "true") {
            return;
        }
        var dataElement = document.getElementById(chart.dataset.pointsId || "");
        if (!dataElement) {
            return;
        }
        var points;
        try {
            var dataSource = dataElement.content || dataElement;
            points = JSON.parse(dataSource.textContent);
        } catch (error) {
            chart.innerHTML = '<div class="ie-empty">No data</div>';
            return;
        }
        var rawMax = parseInt(chart.dataset.max, 10);
        if (!rawMax || !points.length) {
            chart.innerHTML = '<div class="ie-empty">No data</div>';
            return;
        }
        chart.dataset.fragmentInitialized = "true";

        var tickResult = niceTicks(rawMax);
        var ticks = tickResult.ticks;
        var axisMax = tickResult.axisMaxCents;
        var width = 700;
        var height = 148;
        var padLeft = 52;
        var padRight = 16;
        var padTop = 14;
        var padBottom = 24;
        var contentWidth = width - padLeft - padRight;
        var contentHeight = height - padTop - padBottom;
        var count = points.length;

        function xPosition(index) {
            return padLeft + (count > 1 ? index / (count - 1) * contentWidth : contentWidth / 2);
        }

        function yPosition(cents) {
            return padTop + contentHeight - (axisMax ? cents / axisMax * contentHeight : 0);
        }

        function smoothPath(coordinates) {
            if (coordinates.length < 2) {
                return "M" + coordinates[0][0] + "," + coordinates[0][1];
            }
            var path = "M" + coordinates[0][0].toFixed(1) + "," + coordinates[0][1].toFixed(1);
            for (var index = 0; index < coordinates.length - 1; index += 1) {
                var x0 = coordinates[index][0];
                var y0 = coordinates[index][1];
                var x1 = coordinates[index + 1][0];
                var y1 = coordinates[index + 1][1];
                var delta = (x1 - x0) * 0.3;
                path += " C" + (x0 + delta).toFixed(1) + "," + y0.toFixed(1)
                    + " " + (x1 - delta).toFixed(1) + "," + y1.toFixed(1)
                    + " " + x1.toFixed(1) + "," + y1.toFixed(1);
            }
            return path;
        }

        var incomeCoordinates = [];
        var expenseCoordinates = [];
        points.forEach(function (point, index) {
            incomeCoordinates.push([xPosition(index), yPosition(point.income_cents)]);
            expenseCoordinates.push([xPosition(index), yPosition(point.expense_cents)]);
        });
        var baseline = yPosition(0);
        var incomePath = smoothPath(incomeCoordinates);
        var expensePath = smoothPath(expenseCoordinates);

        function areaPath(coordinates, linePath) {
            return linePath
                + " L" + coordinates[coordinates.length - 1][0].toFixed(1) + "," + baseline.toFixed(1)
                + " L" + coordinates[0][0].toFixed(1) + "," + baseline.toFixed(1) + " Z";
        }

        var svg = '<svg class="ie-svg" viewBox="0 0 ' + width + " " + height + '" preserveAspectRatio="xMidYMid meet">';
        svg += '<defs><linearGradient id="ie-grad-income" x1="0" x2="0" y1="0" y2="1">';
        svg += '<stop offset="0%" stop-color="#2EC5A7" stop-opacity="0.18"/>';
        svg += '<stop offset="100%" stop-color="#2EC5A7" stop-opacity="0"/></linearGradient>';
        svg += '<linearGradient id="ie-grad-expense" x1="0" x2="0" y1="0" y2="1">';
        svg += '<stop offset="0%" stop-color="var(--series-left)" stop-opacity="0.14"/>';
        svg += '<stop offset="100%" stop-color="var(--series-left)" stop-opacity="0"/></linearGradient></defs>';
        ticks.forEach(function (tick) {
            var gridY = yPosition(tick.value * 100);
            svg += '<line class="ie-grid" x1="' + padLeft + '" x2="' + (width - padRight)
                + '" y1="' + gridY + '" y2="' + gridY + '"/>';
            svg += '<text class="ie-ytick" x="' + (padLeft - 8) + '" y="' + (gridY + 3.5) + '">'
                + tick.label + "</text>";
        });
        points.forEach(function (point, index) {
            svg += '<text class="ie-xtick" x="' + xPosition(index).toFixed(1) + '" y="' + (height - 8) + '">'
                + point.label + "</text>";
        });
        svg += '<path class="ie-area" d="' + areaPath(incomeCoordinates, incomePath) + '" fill="url(#ie-grad-income)"/>';
        svg += '<path class="ie-area" d="' + areaPath(expenseCoordinates, expensePath) + '" fill="url(#ie-grad-expense)"/>';
        svg += '<path class="ie-line ie-line--income" d="' + incomePath + '"/>';
        svg += '<path class="ie-line ie-line--expense" d="' + expensePath + '"/>';
        points.forEach(function (point, index) {
            svg += '<circle class="ie-dot ie-dot--income" data-idx="' + index + '" cx="'
                + incomeCoordinates[index][0].toFixed(1) + '" cy="' + incomeCoordinates[index][1].toFixed(1) + '" r="4"/>';
            svg += '<circle class="ie-dot ie-dot--expense" data-idx="' + index + '" cx="'
                + expenseCoordinates[index][0].toFixed(1) + '" cy="' + expenseCoordinates[index][1].toFixed(1) + '" r="4"/>';
        });
        var columnWidth = contentWidth / count;
        points.forEach(function (point, index) {
            svg += '<rect class="ie-hover-col" data-idx="' + index + '" x="'
                + (xPosition(index) - columnWidth / 2).toFixed(1) + '" y="' + padTop + '" width="'
                + columnWidth.toFixed(1) + '" height="' + contentHeight + '" fill="transparent"/>';
        });
        svg += '<line class="ie-guide" data-ie-guide x1="0" x2="0" y1="' + padTop
            + '" y2="' + (padTop + contentHeight) + '"/></svg>';
        svg += '<div class="ie-tip u-left-pct u-pct-0" data-ie-tip hidden></div>';
        chart.innerHTML = svg;

        var guide = chart.querySelector("[data-ie-guide]");
        var tip = chart.querySelector("[data-ie-tip]");
        var dots = chart.querySelectorAll(".ie-dot");
        var activeIndex = -1;

        function formatDollars(cents) {
            return "$" + Math.round(Math.abs(cents) / 100).toLocaleString("en-US");
        }

        function showTooltip(index) {
            if (index === activeIndex) {
                return;
            }
            activeIndex = index;
            var point = points[index];
            var guideX = xPosition(index);
            guide.setAttribute("x1", guideX);
            guide.setAttribute("x2", guideX);
            guide.classList.add("ie-guide--visible");
            dots.forEach(function (dot) {
                dot.classList.toggle("ie-dot--active", parseInt(dot.dataset.idx, 10) === index);
            });
            tip.innerHTML = '<div class="ie-tip-month">' + point.label + " " + point.ym.split("-")[0] + "</div>"
                + '<div class="ie-tip-row"><span class="ie-tip-dot ie-tip-dot--income"></span>Income'
                + '<span class="ie-tip-val">' + formatDollars(point.income_cents) + "</span></div>"
                + '<div class="ie-tip-row"><span class="ie-tip-dot ie-tip-dot--expense"></span>Expenses'
                + '<span class="ie-tip-val">' + formatDollars(point.expense_cents) + "</span></div>";
            tip.hidden = false;
            var chartRect = chart.getBoundingClientRect();
            var left = chartRect.width * (guideX / width);
            tip.classList.toggle("ie-tip--before", left + tip.offsetWidth + 8 > chartRect.width);
            setBoundedPercentClass(tip, guideX / width * 100);
        }

        function hideTooltip() {
            guide.classList.remove("ie-guide--visible");
            tip.hidden = true;
            dots.forEach(function (dot) {
                dot.classList.remove("ie-dot--active");
            });
            activeIndex = -1;
        }

        chart.querySelectorAll(".ie-hover-col").forEach(function (column) {
            column.addEventListener("mouseenter", function () {
                showTooltip(parseInt(column.dataset.idx, 10));
            });
            column.addEventListener("mouseleave", hideTooltip);
        });
        chart.addEventListener("touchstart", function (event) {
            var chartRect = chart.getBoundingClientRect();
            var relativeX = event.touches[0].clientX - chartRect.left;
            var index = Math.round(relativeX / chartRect.width * (count - 1));
            showTooltip(Math.max(0, Math.min(count - 1, index)));
        }, { passive: true });
        chart.addEventListener("touchend", function () {
            window.setTimeout(hideTooltip, 1500);
        }, { passive: true });
    }

    function initializeKpiPanel(panel) {
        if (panel.dataset.fragmentInitialized === "true" || !window.htmx) {
            return;
        }
        panel.dataset.fragmentInitialized = "true";
        if (panel.dataset.panel === "detail") {
            window.setTimeout(function () {
                var detailSelect = document.querySelector("#kpi-detail .kpi-period-select");
                if (!detailSelect) {
                    return;
                }
                var period = encodeURIComponent(detailSelect.value);
                window.htmx.ajax("GET", panel.dataset.detailCategoriesUrl + "?period=" + period, {
                    target: "#detail-categories",
                    swap: "innerHTML",
                });
                window.setTimeout(function () {
                    window.htmx.ajax("GET", panel.dataset.detailInsightsUrl + "?period=" + period, {
                        target: "#detail-insights",
                        swap: "innerHTML",
                    });
                }, 50);
                window.setTimeout(function () {
                    window.htmx.ajax("GET", panel.dataset.ieInsightsUrl + "?period=" + period, {
                        target: "#ie-insights",
                        swap: "innerHTML",
                    });
                }, 100);
            }, 0);
            return;
        }

        var leftSelect = document.querySelector("#kpi-left .kpi-period-select");
        var rightSelect = document.querySelector("#kpi-right .kpi-period-select");
        if (!leftSelect || !rightSelect) {
            return;
        }
        var leftPeriod = encodeURIComponent(leftSelect.value);
        var rightPeriod = encodeURIComponent(rightSelect.value);
        var query = "?left_period=" + leftPeriod + "&right_period=" + rightPeriod;
        window.htmx.ajax("GET", panel.dataset.categoriesCompareUrl + query, {
            target: "#categories-compare",
            swap: "innerHTML",
        });
        window.setTimeout(function () {
            if (document.getElementById("insights-upcoming")) {
                window.htmx.ajax("GET", panel.dataset.insightsUpcomingUrl + query, {
                    target: "#insights-upcoming",
                    swap: "innerHTML",
                });
            }
        }, 50);
        window.setTimeout(function () {
            if (document.getElementById("ie-insights")) {
                window.htmx.ajax("GET", panel.dataset.ieInsightsUrl + query, {
                    target: "#ie-insights",
                    swap: "innerHTML",
                });
            }
        }, 100);
    }

    function initialize(root) {
        matchingElements(root, '[data-fragment-controller="income-expense-chart"]').forEach(initializeIncomeExpenseChart);
        matchingElements(root, '[data-fragment-controller="kpi-panel"]').forEach(initializeKpiPanel);
        matchingElements(root, "[data-report-page-controller]").forEach(function (form) {
            if (form.dataset.dashboardPageInitialized !== "true") {
                form.dataset.dashboardPageInitialized = "true";
                updateReportPage(form);
            }
        });
        if (document.querySelector(".dash-view-toggle") && window.localStorage.getItem("dash_view") === "compare") {
            setDashboardView("compare");
        }
    }

    document.addEventListener("click", onClick);
    document.addEventListener("change", onChange);
    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") {
            return;
        }
        ["compare", "detail"].forEach(function (kind) {
            var elements = modalElements(kind);
            if (elements.scrim && !elements.scrim.hidden) {
                closeInsightModal(kind);
            }
        });
        var subcategoryScrim = document.getElementById("dcat-popup-scrim");
        if (subcategoryScrim && !subcategoryScrim.hidden) {
            closeSubcategoryPopup();
        }
        closeReportExportMenu();
    });
    document.addEventListener("htmx:beforeRequest", function (event) {
        updateReportLoading(event, true);
    });
    document.addEventListener("htmx:afterRequest", function (event) {
        updateReportLoading(event, false);
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
    window.dashToggleView = setDashboardView;
})();
