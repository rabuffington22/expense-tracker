(function () {
    "use strict";

    var subcategoryCache = null;

    function replaceOptions(select, values, fallback) {
        var options = values && values.length ? values : [fallback];
        select.replaceChildren();
        options.forEach(function (value) {
            var option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
        });
    }

    function populateSubcategory(select, category) {
        if (!subcategoryCache || !category || category === "Uncategorized") {
            replaceOptions(select, null, "Unknown");
            return;
        }

        replaceOptions(select, subcategoryCache[category], "Unknown");
        var current = select.dataset.current;
        if (current && Array.from(select.options).some(function (option) {
            return option.value === current;
        })) {
            select.value = current;
        }
    }

    function initializeCategorization(root) {
        var controller = root.matches && root.matches("[data-categorization-controller]")
            ? root
            : root.querySelector && root.querySelector("[data-categorization-controller]");
        if (!controller || controller.dataset.initialized === "true") {
            return;
        }
        controller.dataset.initialized = "true";

        var categorySelects = document.querySelectorAll('[data-categorization-change="category"]');
        if (!categorySelects.length) {
            return;
        }

        fetch(controller.dataset.allSubcategoriesUrl)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Unable to load subcategories");
                }
                return response.json();
            })
            .then(function (data) {
                subcategoryCache = data;
                categorySelects.forEach(function (select) {
                    var subcategory = document.getElementById("subcat_" + select.dataset.transactionId);
                    if (subcategory) {
                        populateSubcategory(subcategory, select.value);
                    }
                });
            });
    }

    function prefillAlias(control) {
        var pattern = control.dataset.description.replace(
            /^(paypal\s*\*|venmo\s*\*|zelle\s*\*|sq\s*\*|tst\s*\*|sp\s*\*)\s*/i,
            ""
        );
        pattern = pattern.replace(/\s+\w{2}\s*$/, "").trim();

        document.getElementById("alias-pattern").value = pattern;
        document.getElementById("alias-canonical").value = pattern;
        var details = document.getElementById("alias-details");
        details.open = true;
        details.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    document.addEventListener("click", function (event) {
        var action = event.target.closest('[data-categorization-action="prefill-alias"]');
        if (action) {
            event.preventDefault();
            prefillAlias(action);
            return;
        }

        var confirmControl = event.target.closest("[data-confirm-message]");
        if (confirmControl && !window.confirm(confirmControl.dataset.confirmMessage)) {
            event.preventDefault();
        }
    });

    document.addEventListener("change", function (event) {
        var control = event.target.closest("[data-categorization-change], [data-upload-change]");
        if (!control) {
            return;
        }

        if (control.dataset.categorizationChange === "category") {
            var subcategory = document.getElementById("subcat_" + control.dataset.transactionId);
            if (subcategory) {
                subcategory.dataset.current = "";
                populateSubcategory(subcategory, control.value);
            }
            return;
        }

        if (control.dataset.categorizationChange === "orphan-category") {
            var orphanController = document.querySelector("[data-categorization-orphans-controller]");
            var orphanSubcategory = control.closest("form").querySelector(".orphan-sub");
            if (!control.value) {
                replaceOptions(orphanSubcategory, null, "General");
                return;
            }
            fetch(orphanController.dataset.subcategoriesUrl + "?category=" + encodeURIComponent(control.value))
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("Unable to load orphan subcategories");
                    }
                    return response.text();
                })
                .then(function (html) {
                    orphanSubcategory.innerHTML = html;
                });
            return;
        }

        if (control.dataset.uploadChange === "month") {
            var uploadController = document.querySelector("[data-upload-controller]");
            window.location.href = uploadController.dataset.uploadIndexUrl
                + "?month=" + encodeURIComponent(control.value);
        }
    });

    document.addEventListener("DOMContentLoaded", function () {
        initializeCategorization(document);
    });
    document.addEventListener("htmx:load", function (event) {
        initializeCategorization(event.detail.elt || document);
    });
}());
