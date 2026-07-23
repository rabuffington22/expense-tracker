/* Long-Term Planning page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    var flippedCard = null;

    function controllerRoot() {
        return document.querySelector("[data-planning-controller]");
    }

    function setGenieOrigin(card) {
        var rect = card.getBoundingClientRect();
        var centerX = rect.left + rect.width / 2;
        var centerY = rect.top + rect.height / 2;
        var popup = document.querySelector(".pl-modal-popup");
        if (popup) {
            popup.style.setProperty("--genie-x", (centerX - window.innerWidth / 2) + "px");
            popup.style.setProperty("--genie-y", (centerY - window.innerHeight / 2) + "px");
        }
    }

    function hideAllForms() {
        document.querySelectorAll(".pl-modal-form").forEach(function (form) {
            form.hidden = true;
        });
    }

    function showForm(form) {
        if (!form) {
            return;
        }
        form.hidden = false;
        document.getElementById("pl-modal-scrim").hidden = false;
        var nameInput = form.querySelector('input[name="name"]');
        if (nameInput) {
            nameInput.focus();
        }
    }

    function openEdit(itemId) {
        hideAllForms();
        showForm(document.getElementById("pl-edit-" + itemId));
    }

    function openAdd(entityKey, itemType) {
        hideAllForms();
        showForm(document.getElementById("pl-add-form-" + entityKey + "-" + itemType));
    }

    function flipAndOpen(card) {
        card.classList.add("card-flipped");
        flippedCard = card;
        setGenieOrigin(card);
        window.setTimeout(function () {
            openEdit(card.dataset.itemId);
        }, 250);
    }

    function closeModal() {
        var scrim = document.getElementById("pl-modal-scrim");
        if (!scrim || scrim.hidden) {
            return;
        }
        var popup = document.querySelector(".pl-modal-popup");
        if (flippedCard) {
            setGenieOrigin(flippedCard);
        }
        scrim.classList.add("cf-modal-scrim--closing");
        if (popup) {
            popup.classList.add("pl-modal-popup--closing");
        }
        window.setTimeout(function () {
            scrim.hidden = true;
            scrim.classList.remove("cf-modal-scrim--closing");
            if (popup) {
                popup.classList.remove("pl-modal-popup--closing");
            }
            hideAllForms();
            if (flippedCard) {
                flippedCard.classList.remove("card-flipped");
                flippedCard = null;
            }
        }, 300);
    }

    function toggleSource(select) {
        var form = select.closest(".pl-modal-form");
        var accountGroup = form.querySelector(".pl-g-cfaccount");
        var valueInput = form.querySelector('input[name="current_value"]');
        var isCashFlow = select.value === "cashflow";
        accountGroup.hidden = !isCashFlow;
        valueInput.disabled = isCashFlow;
        valueInput.style.opacity = isCashFlow ? "0.5" : "1";
    }

    function editAge(display) {
        display.hidden = true;
        var input = document.getElementById("pl-birth-date");
        input.hidden = false;
        input.focus();
    }

    function saveAge(input) {
        if (!input.value) {
            input.hidden = true;
            input.previousElementSibling.hidden = false;
            return;
        }
        input.closest("form").requestSubmit();
    }

    function deleteItem(control) {
        if (window.confirm("Delete this item?")) {
            control.closest(".pl-modal-form").querySelector(".pl-del-form").submit();
        }
    }

    function stripMoneySeparators(form) {
        form.querySelectorAll(
            'input[name="current_value"], input[name="monthly_contrib"], input[name="monthly_payment"]'
        ).forEach(function (input) {
            input.value = input.value.replace(/,/g, "");
        });
    }

    function initialize() {
        var root = controllerRoot();
        if (!root || root.dataset.initialized === "true") {
            return;
        }
        root.dataset.initialized = "true";
    }

    document.addEventListener("click", function (event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        var control = event.target.closest("[data-planning-action]");
        if (!control) {
            return;
        }
        var action = control.dataset.planningAction;
        if (action === "flip-open") {
            flipAndOpen(control);
        } else if (action === "open-add") {
            openAdd(control.dataset.entityKey, control.dataset.itemType);
        } else if (action === "close-modal") {
            closeModal();
        } else if (action === "close-on-scrim" && event.target === control) {
            closeModal();
        } else if (action === "edit-age") {
            editAge(control);
        } else if (action === "delete-item") {
            deleteItem(control);
        }
    });

    document.addEventListener("change", function (event) {
        if (event.target.matches('[data-planning-change="source"]')) {
            toggleSource(event.target);
        } else if (event.target.matches('[data-planning-change="save-age"]')) {
            saveAge(event.target);
        }
    });

    document.addEventListener("focusout", function (event) {
        if (event.target.matches('[data-planning-change="save-age"]')) {
            saveAge(event.target);
        }
    });

    document.addEventListener("submit", function (event) {
        if (event.target.matches(".pl-modal-form form")) {
            stripMoneySeparators(event.target);
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && controllerRoot()) {
            closeModal();
        }
    });

    document.addEventListener("DOMContentLoaded", initialize);
}());
