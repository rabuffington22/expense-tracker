/* Short-Term Planning page behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    var goals = {};
    var currentGoalId = null;
    var flippedCard = null;
    var subcategoryCache = null;
    var needsBudgetRefresh = false;

    function controllerRoot() {
        return document.querySelector("[data-short-term-planning-controller]");
    }

    function readGoals() {
        var element = document.getElementById("stp-goals-data");
        if (!element) {
            return {};
        }
        try {
            var dataSource = element.content || element;
            var parsed = JSON.parse(dataSource.textContent);
            return parsed.reduce(function (result, goal) {
                result[goal.id] = goal;
                return result;
            }, {});
        } catch (error) {
            console.error("Failed to parse goals data:", error);
            return {};
        }
    }

    function routeWithId(route, id) {
        return route.replace("/0/", "/" + String(id) + "/");
    }

    function formatWholeDollars(cents) {
        return (cents / 100).toLocaleString("en-US", {
            style: "currency",
            currency: "USD",
            maximumFractionDigits: 0
        });
    }

    function typeChange(type) {
        document.getElementById("stp-debt-fields").hidden = type !== "debt_payoff";
        document.getElementById("stp-savings-fields").hidden = type !== "savings";
        document.getElementById("stp-spending-fields").hidden =
            type !== "spending_reduction";
    }

    function editGoal(goalId) {
        var goal = goals[goalId];
        var root = controllerRoot();
        if (!goal || !root) {
            return;
        }

        var form = document.getElementById("stp-edit-form");
        form.action = routeWithId(root.dataset.goalUpdateUrl, goal.id);
        document.getElementById("stp-edit-name").value = goal.name;
        document.getElementById("stp-edit-type").value = goal.goal_type;
        document.getElementById("stp-edit-monthly").value = goal.monthly_amount_cents
            ? (goal.monthly_amount_cents / 100).toLocaleString("en-US", {
                maximumFractionDigits: 0
            })
            : "";
        document.getElementById("stp-edit-target-date").value =
            goal.target_date || "";
        document.getElementById("stp-edit-status").value = goal.status;
        document.getElementById("stp-edit-notes").value = goal.notes || "";
        document.getElementById("stp-delete-form").action =
            routeWithId(root.dataset.goalDeleteUrl, goal.id);
        document.getElementById("stp-edit-modal").showModal();
    }

    function deleteCurrentGoal() {
        var deleteForm = document.getElementById("stp-delete-form");
        if (deleteForm && window.confirm("Delete this goal and all its progress data?")) {
            deleteForm.submit();
        }
    }

    function lockPlan(goalId) {
        var goal = goals[goalId];
        var root = controllerRoot();
        if (!goal || !root) {
            return;
        }

        var form = document.getElementById("stp-lock-form");
        form.action = routeWithId(root.dataset.goalLockUrl, goal.id);
        document.getElementById("stp-lock-strategy").value =
            goal.strategy || "avalanche";
        document.getElementById("stp-lock-monthly").value = goal.monthly_amount_cents
            ? (goal.monthly_amount_cents / 100).toLocaleString("en-US", {
                maximumFractionDigits: 0
            })
            : "";
        document.getElementById("stp-lock-date").value = goal.target_date || "";
        document.getElementById("stp-lock-narrative").value = goal.ai_plan || "";
        document.getElementById("stp-lock-strategy-group").hidden =
            goal.goal_type !== "debt_payoff";
        document.getElementById("stp-lock-modal").showModal();
    }

    function animateGoalPopup(popup, card, closing) {
        popup.getAnimations().forEach(function (animation) {
            animation.cancel();
        });
        var popupRect = popup.getBoundingClientRect();
        var cardRect = card ? card.getBoundingClientRect() : popupRect;
        var offsetX = cardRect.left + cardRect.width / 2
            - (popupRect.left + popupRect.width / 2);
        var offsetY = cardRect.top + cardRect.height / 2
            - (popupRect.top + popupRect.height / 2);
        var originFrame = {
            opacity: 0,
            transform: "translate3d(" + offsetX + "px, "
                + offsetY + "px, 0) scale(0.05)"
        };
        var settledFrame = {
            opacity: 1,
            transform: "translate3d(0, 0, 0) scale(1)"
        };
        popup.animate(
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

    function openGoalPopup(goalId) {
        var goal = goals[goalId];
        if (!goal) {
            return;
        }
        currentGoalId = goalId;

        var popup = document.getElementById("stp-goal-popup");
        popup.classList.remove(
            "stp-goal-popup--debt_payoff",
            "stp-goal-popup--savings",
            "stp-goal-popup--spending_reduction"
        );
        popup.classList.add("stp-goal-popup--" + goal.goal_type);
        document.getElementById("stp-popup-name").textContent = goal.name;
        document.getElementById("stp-popup-balance").textContent =
            formatWholeDollars(goal.current_balance_cents);

        var target = document.getElementById("stp-popup-target");
        if (goal.goal_type === "savings" && goal.target_amount_cents) {
            target.textContent = "of " + formatWholeDollars(goal.target_amount_cents);
            target.hidden = false;
        } else {
            target.hidden = true;
        }

        document.getElementById("stp-popup-pct").textContent =
            (goal.progress_pct || 0) + "%";

        var strategyRow = document.getElementById("stp-popup-strategy-row");
        if (goal.strategy) {
            document.getElementById("stp-popup-strategy").textContent =
                goal.strategy.charAt(0).toUpperCase() + goal.strategy.slice(1);
            strategyRow.hidden = false;
        } else {
            strategyRow.hidden = true;
        }

        var monthlyRow = document.getElementById("stp-popup-monthly-row");
        if (goal.monthly_amount_cents && goal.monthly_amount_cents > 0) {
            document.getElementById("stp-popup-monthly").textContent =
                formatWholeDollars(goal.monthly_amount_cents) + "/mo";
            monthlyRow.hidden = false;
        } else {
            monthlyRow.hidden = true;
        }

        var targetDateRow = document.getElementById("stp-popup-target-date-row");
        if (goal.target_date) {
            document.getElementById("stp-popup-target-date").textContent =
                goal.target_date;
            targetDateRow.hidden = false;
        } else {
            targetDateRow.hidden = true;
        }

        var planGroup = document.getElementById("stp-popup-plan-group");
        if (goal.ai_plan) {
            document.getElementById("stp-popup-plan-content").textContent =
                goal.ai_plan;
            planGroup.hidden = false;
        } else {
            planGroup.hidden = true;
        }

        document.getElementById("stp-popup-review-banner").hidden =
            !goal.needs_review;
        document.getElementById("stp-popup-plan-btn").textContent =
            goal.ai_plan ? "Update Plan" : "Lock In Plan";
        document.getElementById("stp-goal-scrim").hidden = false;
        animateGoalPopup(popup, flippedCard, false);
    }

    function flipAndOpen(card, event) {
        if (event.target.closest("button, a")) {
            return;
        }
        card.classList.add("card-flipped");
        flippedCard = card;
        window.setTimeout(function () {
            openGoalPopup(card.dataset.goalId);
        }, 250);
    }

    function closeGoalPopup() {
        var scrim = document.getElementById("stp-goal-scrim");
        var popup = document.getElementById("stp-goal-popup");
        if (!scrim || scrim.hidden) {
            return;
        }
        scrim.classList.add("stp-goal-scrim--closing");
        animateGoalPopup(popup, flippedCard, true);
        window.setTimeout(function () {
            scrim.hidden = true;
            scrim.classList.remove("stp-goal-scrim--closing");
            popup.getAnimations().forEach(function (animation) {
                animation.cancel();
            });
            if (flippedCard) {
                flippedCard.classList.remove("card-flipped");
                flippedCard = null;
            }
            currentGoalId = null;
        }, 300);
    }

    function toggleSubcategories(control) {
        var category = control.dataset.category;
        var chevron = control.querySelector(".stp-cat-chevron");
        var row = control.closest("tr");
        var isOpen = chevron.classList.contains("open");
        row.parentElement.querySelectorAll(
            'tr.stp-subcat-row[data-parent="' + CSS.escape(category) + '"]'
        ).forEach(function (existingRow) {
            existingRow.remove();
        });

        if (isOpen) {
            chevron.classList.remove("open");
            return;
        }

        chevron.classList.add("open");
        var root = controllerRoot();
        var url = root.dataset.budgetSubcategoriesUrl
            + "?category=" + encodeURIComponent(category)
            + "&month=" + encodeURIComponent(root.dataset.currentMonth);
        window.fetch(url)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Subcategory request failed");
                }
                return response.text();
            })
            .then(function (html) {
                if (!html.trim()) {
                    return;
                }
                var temp = document.createElement("tbody");
                temp.innerHTML = html;
                var after = row;
                temp.querySelectorAll("tr").forEach(function (subcategoryRow) {
                    subcategoryRow.dataset.parent = category;
                    after.parentElement.insertBefore(
                        subcategoryRow,
                        after.nextSibling
                    );
                    after = subcategoryRow;
                });
            })
            .catch(function () {
                chevron.classList.remove("open");
            });
    }

    function showTransactions(category, subcategory) {
        var root = controllerRoot();
        var modal = document.getElementById("stp-txn-modal");
        var body = document.getElementById("stp-txn-modal-body");
        document.getElementById("stp-txn-modal-title").textContent = subcategory
            ? category + " › " + subcategory
            : category;
        body.innerHTML = '<div class="stp-drill-empty">Loading…</div>';
        modal.dataset.originalCategory = category;
        modal.dataset.originalSubcategory = subcategory || "";
        modal.dataset.month = root.dataset.currentMonth;
        modal.showModal();

        var url = root.dataset.budgetTransactionsUrl
            + "?category=" + encodeURIComponent(category)
            + "&month=" + encodeURIComponent(root.dataset.currentMonth);
        if (subcategory) {
            url += "&subcategory=" + encodeURIComponent(subcategory);
        }
        window.fetch(url)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Transaction request failed");
                }
                return response.text();
            })
            .then(function (html) {
                body.innerHTML = html;
            })
            .catch(function () {
                body.innerHTML =
                    '<div class="stp-drill-empty">Error loading transactions</div>';
            });
    }

    function ensureSubcategoryCache() {
        if (subcategoryCache) {
            return Promise.resolve(subcategoryCache);
        }
        return window.fetch(controllerRoot().dataset.allSubcategoriesUrl)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Category request failed");
                }
                return response.json();
            })
            .then(function (data) {
                subcategoryCache = data;
                return data;
            })
            .catch(function (error) {
                window.alert("Could not load categories");
                throw error;
            });
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function buildOptions(items, selected) {
        return items.map(function (item) {
            var escaped = escapeHtml(item);
            return '<option value="' + escaped + '"'
                + (item === selected ? " selected" : "")
                + ">" + escaped + "</option>";
        }).join("");
    }

    function editTransaction(row) {
        if (row.classList.contains("stp-drill-edit-row")) {
            return;
        }
        ensureSubcategoryCache().then(function () {
            var transactionId = row.dataset.transactionId;
            var currentCategory = row.dataset.category;
            var currentSubcategory = row.dataset.subcategory;
            row._originalHtml = row.innerHTML;
            row.classList.add("stp-drill-edit-row");
            row.classList.remove("stp-drill-row");

            var categories = Object.keys(subcategoryCache).sort();
            if (currentCategory && categories.indexOf(currentCategory) < 0) {
                categories.push(currentCategory);
                categories.sort();
            }
            var subcategories =
                (subcategoryCache[currentCategory] || ["General"]).slice();
            if (
                currentSubcategory
                && subcategories.indexOf(currentSubcategory) < 0
            ) {
                subcategories.push(currentSubcategory);
                subcategories.sort();
            }

            var cells = row.querySelectorAll("td");
            var dateText = escapeHtml(cells[0].textContent);
            var description = escapeHtml(cells[1].textContent);
            var amountText = escapeHtml(cells[3].textContent);
            row.innerHTML =
                "<td>" + dateText + "</td>"
                + "<td>" + description + "</td>"
                + '<td colspan="2">'
                + '<div class="stp-drill-edit-wrap">'
                + '<select data-stp-change="transaction-category">'
                + buildOptions(categories, currentCategory)
                + "</select>"
                + '<select data-stp-field="transaction-subcategory">'
                + buildOptions(subcategories, currentSubcategory)
                + "</select>"
                + "</div>"
                + '<div class="stp-drill-edit-actions">'
                + '<button type="button" class="btn btn-primary btn-sm" '
                + 'data-stp-action="save-transaction">Save</button>'
                + '<button type="button" class="btn btn-secondary btn-sm" '
                + 'data-stp-action="cancel-transaction">' + amountText + "</button>"
                + "</div>"
                + "</td>";
            row.dataset.transactionId = transactionId;
        }).catch(function () {
            /* ensureSubcategoryCache already reports the controlled failure. */
        });
    }

    function changeTransactionCategory(select) {
        var row = select.closest("tr");
        var subcategorySelect = row.querySelector(
            '[data-stp-field="transaction-subcategory"]'
        );
        var subcategories = subcategoryCache[select.value] || ["General"];
        subcategorySelect.innerHTML = buildOptions(subcategories, "General");
    }

    function saveTransaction(row) {
        var root = controllerRoot();
        var modal = document.getElementById("stp-txn-modal");
        var categorySelect = row.querySelector(
            '[data-stp-change="transaction-category"]'
        );
        var subcategorySelect = row.querySelector(
            '[data-stp-field="transaction-subcategory"]'
        );
        var formData = new FormData();
        formData.append("category", categorySelect.value);
        formData.append("subcategory", subcategorySelect.value);
        formData.append("orig_category", modal.dataset.originalCategory);
        formData.append(
            "orig_subcategory",
            modal.dataset.originalSubcategory
        );
        formData.append("month", modal.dataset.month);

        var updateUrl = root.dataset.updateTransactionUrl.replace(
            "__txn_id__",
            encodeURIComponent(row.dataset.transactionId)
        );
        window.fetch(updateUrl, {
            method: "POST",
            body: formData
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Save failed");
                }
                var trigger = response.headers.get("HX-Trigger");
                if (trigger && trigger.indexOf("stpBudgetChanged") >= 0) {
                    needsBudgetRefresh = true;
                }
                return response.text();
            })
            .then(function (html) {
                document.getElementById("stp-txn-modal-body").innerHTML = html;
            })
            .catch(function () {
                window.alert("Error saving — try again");
            });
    }

    function cancelTransaction(row) {
        if (!row || !row._originalHtml) {
            return;
        }
        row.innerHTML = row._originalHtml;
        row.classList.remove("stp-drill-edit-row");
        row.classList.add("stp-drill-row");
    }

    function closeDialog(control) {
        var dialog = control.closest("dialog");
        if (dialog) {
            dialog.close();
        }
    }

    function handleClick(event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        var control = event.target.closest("[data-stp-action]");
        if (!control) {
            return;
        }
        var action = control.dataset.stpAction;
        if (action === "open-dialog") {
            document.getElementById(control.dataset.dialogId).showModal();
        } else if (action === "close-dialog") {
            closeDialog(control);
        } else if (action === "flip-open") {
            flipAndOpen(control, event);
        } else if (action === "close-goal-popup") {
            closeGoalPopup();
        } else if (action === "edit-current-goal") {
            var editGoalId = currentGoalId;
            closeGoalPopup();
            editGoal(editGoalId);
        } else if (action === "lock-current-goal") {
            var lockGoalId = currentGoalId;
            closeGoalPopup();
            lockPlan(lockGoalId);
        } else if (action === "review-current-goal") {
            var reviewGoalId = currentGoalId;
            closeGoalPopup();
            var reviewDialog = document.getElementById(
                "stp-review-" + reviewGoalId
            );
            if (reviewDialog) {
                reviewDialog.showModal();
            }
        } else if (action === "delete-current-goal") {
            deleteCurrentGoal();
        } else if (action === "toggle-subcategories") {
            toggleSubcategories(control);
        } else if (action === "show-transactions") {
            showTransactions(
                control.dataset.category,
                control.dataset.subcategory || ""
            );
        } else if (action === "edit-transaction") {
            editTransaction(control.closest("tr"));
        } else if (action === "save-transaction") {
            saveTransaction(control.closest("tr"));
        } else if (action === "cancel-transaction") {
            cancelTransaction(control.closest("tr"));
        }
    }

    function handleChange(event) {
        if (!(event.target instanceof Element)) {
            return;
        }
        if (event.target.matches('[data-stp-change="goal-type"]')) {
            typeChange(event.target.value);
        } else if (event.target.matches('[data-stp-change="budget-month"]')) {
            window.location.href = controllerRoot().dataset.indexUrl
                + "?month=" + encodeURIComponent(event.target.value)
                + "#budget";
        } else if (
            event.target.matches('[data-stp-change="transaction-category"]')
        ) {
            changeTransactionCategory(event.target);
        }
    }

    function stripMoneySeparators(form) {
        form.querySelectorAll(
            'input[name="monthly_amount"], input[name="target_amount"]'
        ).forEach(function (input) {
            input.value = input.value.replace(/,/g, "");
        });
        form.querySelectorAll(".stp-budget-input").forEach(function (input) {
            input.value = input.value.replace(/,/g, "").replace(/\$/g, "");
        });
    }

    function initialize() {
        var root = controllerRoot();
        if (!root || root.dataset.initialized === "true") {
            return;
        }
        goals = readGoals();
        root.dataset.initialized = "true";
        var transactionModal = document.getElementById("stp-txn-modal");
        transactionModal.addEventListener("close", function () {
            if (needsBudgetRefresh) {
                needsBudgetRefresh = false;
                window.location.reload();
            }
        });
    }

    document.addEventListener("click", handleClick);
    document.addEventListener("change", handleChange);
    document.addEventListener("keydown", function (event) {
        var scrim = document.getElementById("stp-goal-scrim");
        if (event.key === "Escape" && scrim && !scrim.hidden) {
            closeGoalPopup();
        }
    });
    document.addEventListener("submit", function (event) {
        if (controllerRoot() && event.target instanceof HTMLFormElement) {
            stripMoneySeparators(event.target);
        }
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
}());
