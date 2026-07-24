/* Cash Flow page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var flippedCard = null;

    function controllerRoot() {
        return document.querySelector("[data-cashflow-controller]");
    }

    function formatDate(isoString) {
        if (!isoString) {
            return "";
        }
        var parts = isoString.split("-");
        if (parts.length !== 3) {
            return isoString;
        }
        var month = parseInt(parts[1], 10) - 1;
        var day = parseInt(parts[2], 10);
        return months[month] + " " + day;
    }

    function sizeInput(input) {
        input.size = Math.max(2, input.value.length + 1);
    }

    function parseDueDay(input) {
        var value = input.value.replace(/[^0-9]/g, "");
        var day = parseInt(value, 10);
        document.getElementById("cf-modal-due-day-hidden").value =
            day >= 1 && day <= 31 ? day : "";
        sizeInput(input);
    }

    function animateModal(modal, card, closing) {
        modal.getAnimations().forEach(function (animation) {
            animation.cancel();
        });
        var modalRect = modal.getBoundingClientRect();
        var cardRect = card ? card.getBoundingClientRect() : modalRect;
        var offsetX = cardRect.left + cardRect.width / 2
            - (modalRect.left + modalRect.width / 2);
        var offsetY = cardRect.top + cardRect.height / 2
            - (modalRect.top + modalRect.height / 2);
        var originFrame = {
            opacity: 0,
            transform: "translate3d(" + offsetX + "px, "
                + offsetY + "px, 0) scale(0.05)"
        };
        var settledFrame = {
            opacity: 1,
            transform: "translate3d(0, 0, 0) scale(1)"
        };
        modal.animate(
            closing ? [settledFrame, originFrame] : [originFrame, settledFrame],
            {
                duration: closing ? 300 : 400,
                easing: closing
                    ? "cubic-bezier(0.55, 0, 1, 0.45)"
                    : "cubic-bezier(0.22, 1, 0.36, 1)",
                fill: closing ? "forwards" : "none"
            }
        );
    }

    function openModal(control, event) {
        if (event && event.target.closest("button, form, a") && !control.matches("button")) {
            return;
        }

        var data = control.dataset;
        var isCard = data.acctType === "credit_card";
        var modal = document.querySelector(".cfm");
        modal.classList.remove("cfm--bank", "cfm--card");
        modal.classList.add(isCard ? "cfm--card" : "cfm--bank");

        document.getElementById("cf-modal-title").textContent = data.acctName;
        document.getElementById("cf-modal-form").action = isCard
            ? "/cashflow/accounts/update-card/" + data.acctId
            : "/cashflow/accounts/update/" + data.acctId;
        document.getElementById("cf-modal-entity").value = data.entityKey;

        var balanceInput = document.getElementById("cf-modal-balance");
        balanceInput.value = data.balance;
        sizeInput(balanceInput);

        var cardGroup = document.getElementById("cf-modal-card-group");
        if (isCard) {
            cardGroup.hidden = false;
            var limitInput = document.getElementById("cf-modal-limit");
            limitInput.value = data.limit;
            sizeInput(limitInput);

            var aprInput = document.getElementById("cf-modal-apr");
            aprInput.value = data.apr || "";
            sizeInput(aprInput);

            document.getElementById("cf-modal-due-day-hidden").value = data.dueDay;
            var dueDisplay = document.getElementById("cf-modal-due-display");
            dueDisplay.value = data.dueDate ? formatDate(data.dueDate) : (data.dueDay || "");
            sizeInput(dueDisplay);

            var paymentInput = document.getElementById("cf-modal-payment");
            paymentInput.value = data.payment;
            sizeInput(paymentInput);
        } else {
            cardGroup.hidden = true;
        }

        document.getElementById("cf-modal-upcoming-label").hidden = true;
        document.getElementById("cf-modal-upcoming-list").innerHTML =
            '<span class="cfm-empty">No upcoming charges</span>';
        document.getElementById("cf-add-entity").value = data.entityKey;
        document.getElementById("cf-add-acct-id").value = data.acctId;
        document.getElementById("cf-add-recurring-section").hidden = false;
        document.getElementById("cf-modal-scrim").hidden = false;
        animateModal(modal, flippedCard, false);
    }

    function flipAndOpen(card, event) {
        if (event && event.target.closest("button, form, a")) {
            return;
        }
        card.classList.add("card-flipped");
        flippedCard = card;
        window.setTimeout(function () {
            openModal(card, null);
        }, 250);
    }

    function closeModal() {
        var scrim = document.getElementById("cf-modal-scrim");
        if (!scrim || scrim.hidden) {
            return;
        }
        var modal = document.querySelector(".cfm");
        scrim.classList.add("cf-modal-scrim--closing");
        animateModal(modal, flippedCard, true);
        window.setTimeout(function () {
            scrim.hidden = true;
            scrim.classList.remove("cf-modal-scrim--closing");
            modal.getAnimations().forEach(function (animation) {
                animation.cancel();
            });
            document.getElementById("cf-add-recurring-section").hidden = true;
            if (flippedCard) {
                flippedCard.classList.remove("card-flipped");
                flippedCard = null;
            }
        }, 300);
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
        var control = event.target.closest("[data-cashflow-action]");
        if (!control) {
            return;
        }

        var action = control.dataset.cashflowAction;
        if (action === "flip-open") {
            flipAndOpen(control, event);
        } else if (action === "open-modal") {
            openModal(control, event);
        } else if (action === "close-modal") {
            closeModal();
        } else if (action === "close-on-scrim" && event.target === control) {
            closeModal();
        }
    });

    document.addEventListener("focusin", function (event) {
        if (event.target.matches("[data-cashflow-select-on-focus]")) {
            event.target.select();
        }
    });

    document.addEventListener("input", function (event) {
        if (event.target.matches('[data-cashflow-input="size"]')) {
            sizeInput(event.target);
        } else if (event.target.matches('[data-cashflow-input="due-day"]')) {
            parseDueDay(event.target);
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && controllerRoot()) {
            closeModal();
        }
    });

    document.addEventListener("DOMContentLoaded", initialize);
}());
