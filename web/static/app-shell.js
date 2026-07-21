/* Shared application-shell behavior. Keep this file free of server-rendered code. */
(function () {
    "use strict";

    var drawerMedia = window.matchMedia("(max-width: 768px)");
    var drawerCloseTimer = null;
    var aiCurrentPage = "general";
    var initialized = false;

    function syncThemeUI(theme) {
        var icon = document.querySelector(".theme-toggle-icon");
        if (icon) {
            icon.textContent = theme === "dark" ? "\u263E" : "\u2600\uFE0F";
        }

        var meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
            meta.content = theme === "light" ? "#F7F9FC" : "#000000";
        }
    }

    function toggleTheme() {
        var html = document.documentElement;
        var current = html.getAttribute("data-theme") || "dark";
        var next = current === "dark" ? "light" : "dark";
        html.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
        syncThemeUI(next);
    }

    function drawerElements() {
        return {
            sidebar: document.getElementById("sidebar-nav"),
            scrim: document.getElementById("sidebar-scrim"),
            button: document.getElementById("hamburger-btn"),
        };
    }

    function drawerFocusable(sidebar) {
        return Array.prototype.filter.call(
            sidebar.querySelectorAll(
                'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
            ),
            function (element) {
                return !element.hidden && element.getAttribute("aria-hidden") !== "true";
            }
        );
    }

    function setClosedDrawerSemantics(isMobile) {
        var elements = drawerElements();
        if (!elements.sidebar || !elements.scrim || !elements.button) {
            return;
        }

        elements.sidebar.classList.remove("open");
        elements.scrim.classList.remove("visible");
        elements.scrim.hidden = true;
        elements.button.setAttribute("aria-expanded", "false");
        elements.button.setAttribute("aria-label", "Open navigation");
        document.body.classList.remove("mobile-drawer-open");

        if (isMobile) {
            elements.sidebar.setAttribute("aria-hidden", "true");
            elements.sidebar.setAttribute("inert", "");
        } else {
            elements.sidebar.removeAttribute("aria-hidden");
            elements.sidebar.removeAttribute("inert");
        }
    }

    function openSidebar() {
        if (!drawerMedia.matches) {
            return;
        }

        var elements = drawerElements();
        if (!elements.sidebar || !elements.scrim || !elements.button) {
            return;
        }

        if (drawerCloseTimer) {
            window.clearTimeout(drawerCloseTimer);
            drawerCloseTimer = null;
        }

        elements.sidebar.removeAttribute("aria-hidden");
        elements.sidebar.removeAttribute("inert");
        elements.sidebar.classList.add("open");
        elements.scrim.hidden = false;
        void elements.scrim.offsetWidth;
        elements.scrim.classList.add("visible");
        elements.button.setAttribute("aria-expanded", "true");
        elements.button.setAttribute("aria-label", "Close navigation");
        document.body.classList.add("mobile-drawer-open");

        var firstPrimaryLink = elements.sidebar.querySelector(".sb-nav a[href]");
        if (firstPrimaryLink) {
            firstPrimaryLink.focus();
        }
    }

    function closeSidebar(options) {
        options = options || {};
        if (!drawerMedia.matches) {
            setClosedDrawerSemantics(false);
            return;
        }

        var elements = drawerElements();
        if (!elements.sidebar || !elements.scrim || !elements.button) {
            return;
        }

        var wasOpen = elements.sidebar.classList.contains("open");
        elements.sidebar.classList.remove("open");
        elements.sidebar.setAttribute("aria-hidden", "true");
        elements.sidebar.setAttribute("inert", "");
        elements.button.setAttribute("aria-expanded", "false");
        elements.button.setAttribute("aria-label", "Open navigation");
        elements.scrim.classList.remove("visible");
        document.body.classList.remove("mobile-drawer-open");

        if (drawerCloseTimer) {
            window.clearTimeout(drawerCloseTimer);
        }
        drawerCloseTimer = window.setTimeout(function () {
            elements.scrim.hidden = true;
            drawerCloseTimer = null;
        }, 300);

        if (wasOpen && options.restoreFocus !== false && drawerMedia.matches) {
            elements.button.focus();
        }
    }

    function toggleSidebar() {
        var elements = drawerElements();
        if (!elements.sidebar) {
            return;
        }
        if (elements.sidebar.classList.contains("open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    function syncDrawerBreakpoint() {
        if (drawerCloseTimer) {
            window.clearTimeout(drawerCloseTimer);
            drawerCloseTimer = null;
        }
        setClosedDrawerSemantics(drawerMedia.matches);
    }

    function aiScrollThread() {
        window.requestAnimationFrame(function () {
            var body = document.querySelector(".ai-chat-body");
            if (body) {
                body.scrollTop = body.scrollHeight;
            }
        });
    }

    function aiChatOpen(page) {
        page = page || "general";
        var thread = document.getElementById("ai-chat-thread");
        var empty = document.getElementById("ai-chat-empty");
        var pageInput = document.getElementById("ai-chat-page");
        var clearButton = document.getElementById("ai-chat-clear-btn");
        var scrim = document.getElementById("ai-chat-scrim");
        var input = document.getElementById("ai-chat-input");

        if (!thread || !empty || !pageInput || !scrim || !input) {
            return;
        }
        if (page !== aiCurrentPage) {
            thread.innerHTML = "";
            empty.hidden = false;
            aiCurrentPage = page;
        }

        pageInput.value = page;
        if (clearButton) {
            clearButton.setAttribute("hx-vals", JSON.stringify({ page: page }));
            if (window.htmx) {
                window.htmx.process(clearButton);
            }
        }

        scrim.hidden = false;
        document.body.style.overflow = "hidden";
        input.focus();
        aiScrollThread();
    }

    function aiChatClose(event) {
        var scrim = document.getElementById("ai-chat-scrim");
        if (!scrim || (event && event.target !== scrim)) {
            return;
        }
        scrim.hidden = true;
        document.body.style.overflow = "";
    }

    function aiChatBeforeRequest() {
        var thinking = document.getElementById("ai-chat-thinking");
        var empty = document.getElementById("ai-chat-empty");
        if (thinking) {
            thinking.hidden = false;
        }
        if (empty) {
            empty.hidden = true;
        }
        aiScrollThread();
    }

    function aiChatAfterRequest(event) {
        var thinking = document.getElementById("ai-chat-thinking");
        var form = document.getElementById("ai-chat-form");
        var pageInput = document.getElementById("ai-chat-page");
        var input = document.getElementById("ai-chat-input");
        if (thinking) {
            thinking.hidden = true;
        }
        if (!form || !event.detail.successful) {
            return;
        }

        form.reset();
        if (pageInput) {
            pageInput.value = aiCurrentPage;
        }
        aiScrollThread();
        if (input) {
            input.focus();
        }
    }

    function keyboardShortcuts(event) {
        var targetTag = event.target.tagName;
        if (
            targetTag === "INPUT" ||
            targetTag === "TEXTAREA" ||
            targetTag === "SELECT" ||
            event.target.isContentEditable
        ) {
            return;
        }

        var key = event.key;
        if (keyboardShortcuts.pendingNavigation) {
            keyboardShortcuts.pendingNavigation = false;
            window.clearTimeout(keyboardShortcuts.navigationTimer);
            if (key === "t") {
                window.location.href = "/transactions/";
            } else if (key === "d") {
                window.location.href = "/";
            }
            return;
        }
        if (key === "g") {
            keyboardShortcuts.pendingNavigation = true;
            keyboardShortcuts.navigationTimer = window.setTimeout(function () {
                keyboardShortcuts.pendingNavigation = false;
            }, 1000);
            return;
        }

        if (key === "/") {
            var search = document.getElementById("q");
            var start = document.getElementById("start");
            if (search) {
                event.preventDefault();
                search.focus();
            } else if (start) {
                event.preventDefault();
                start.focus();
            }
            return;
        }

        var container = document.getElementById("txn-results");
        var rows = container ? Array.from(container.querySelectorAll("tbody tr")) : [];
        if (rows.length && (key === "j" || key === "k")) {
            var current = rows.findIndex(function (row) {
                return row.classList.contains("is-selected");
            });
            current = key === "j" ? Math.min(current + 1, rows.length - 1) : Math.max(current - 1, 0);
            rows.forEach(function (row) {
                row.classList.remove("is-selected");
            });
            if (current >= 0 && current < rows.length) {
                rows[current].classList.add("is-selected");
                rows[current].scrollIntoView({ block: "nearest" });
            }
            return;
        }

        if (key === "Enter" && rows.length) {
            var selectedRow = document.querySelector("#txn-results tr.is-selected");
            if (!selectedRow) {
                return;
            }
            var action = selectedRow.classList.contains("txn-editing")
                ? selectedRow.querySelector('button[type="submit"]')
                : selectedRow.querySelector(".btn-icon");
            if (action) {
                action.click();
            }
            return;
        }

        if (key === "Escape") {
            var editing = document.querySelector("#txn-results tr.txn-editing");
            if (editing) {
                var cancel = editing.querySelector('.btn-icon[title="Cancel"]');
                if (cancel) {
                    cancel.click();
                }
                return;
            }
            var selected = document.querySelector("#txn-results tr.is-selected");
            if (selected) {
                selected.classList.remove("is-selected");
            }
        }
    }
    keyboardShortcuts.pendingNavigation = false;
    keyboardShortcuts.navigationTimer = null;

    function injectCsrfInputs(root, token) {
        root.querySelectorAll('form[method="post"], form[method="POST"]').forEach(function (form) {
            if (!form.querySelector('input[name="_csrf_token"]')) {
                var input = document.createElement("input");
                input.type = "hidden";
                input.name = "_csrf_token";
                input.value = token;
                form.appendChild(input);
            }
        });
    }

    function configureCsrf() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        if (!meta) {
            return;
        }
        var token = meta.content;
        injectCsrfInputs(document, token);

        document.body.addEventListener("htmx:afterSettle", function () {
            injectCsrfInputs(document, token);
        });
        document.body.addEventListener("htmx:configRequest", function (event) {
            event.detail.headers["X-CSRF-Token"] = token;
        });

        var originalFetch = window.fetch;
        window.fetch = function (url, options) {
            options = options || {};
            var method = (options.method || "GET").toUpperCase();
            if (method !== "GET" && method !== "HEAD") {
                options.headers = options.headers || {};
                if (options.headers instanceof Headers) {
                    if (!options.headers.has("X-CSRF-Token")) {
                        options.headers.set("X-CSRF-Token", token);
                    }
                } else if (!options.headers["X-CSRF-Token"]) {
                    options.headers["X-CSRF-Token"] = token;
                }
            }
            return originalFetch.call(this, url, options);
        };
    }

    function registerServiceWorker() {
        if (!("serviceWorker" in navigator)) {
            return;
        }
        window.addEventListener("load", function () {
            navigator.serviceWorker.register("/sw.js").then(function (registration) {
                registration.addEventListener("updatefound", function () {
                    var newWorker = registration.installing;
                    if (newWorker) {
                        newWorker.addEventListener("statechange", function () {
                            if (newWorker.state === "activated") {
                                console.log("[SW] New version activated");
                            }
                        });
                    }
                });
            }).catch(function (error) {
                console.log("[SW] Registration failed:", error);
            });
        });
    }

    function initialize() {
        if (initialized) {
            return;
        }
        initialized = true;

        syncThemeUI(document.documentElement.getAttribute("data-theme") || "dark");
        syncDrawerBreakpoint();
        if (drawerMedia.addEventListener) {
            drawerMedia.addEventListener("change", syncDrawerBreakpoint);
        } else {
            drawerMedia.addListener(syncDrawerBreakpoint);
        }

        var hamburger = document.getElementById("hamburger-btn");
        var sidebarScrim = document.getElementById("sidebar-scrim");
        var aiScrim = document.getElementById("ai-chat-scrim");
        var aiClose = document.querySelector("[data-ai-chat-close]");
        var aiForm = document.getElementById("ai-chat-form");

        if (hamburger) {
            hamburger.addEventListener("click", toggleSidebar);
        }
        if (sidebarScrim) {
            sidebarScrim.addEventListener("click", function () {
                closeSidebar();
            });
        }
        if (aiScrim) {
            aiScrim.addEventListener("click", aiChatClose);
        }
        if (aiClose) {
            aiClose.addEventListener("click", function () {
                aiChatClose();
            });
        }
        if (aiForm) {
            document.body.addEventListener("htmx:beforeRequest", function (event) {
                if (event.target === aiForm) {
                    aiChatBeforeRequest();
                }
            });
            document.body.addEventListener("htmx:afterRequest", function (event) {
                if (event.target === aiForm) {
                    aiChatAfterRequest(event);
                }
            });
        }

        document.addEventListener("keydown", function (event) {
            var elements = drawerElements();
            if (!elements.sidebar || !drawerMedia.matches || !elements.sidebar.classList.contains("open")) {
                return;
            }
            if (event.key === "Escape") {
                event.preventDefault();
                closeSidebar();
                return;
            }
            if (event.key !== "Tab") {
                return;
            }

            var focusable = drawerFocusable(elements.sidebar);
            if (!focusable.length) {
                event.preventDefault();
                return;
            }
            var first = focusable[0];
            var last = focusable[focusable.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        });
        document.addEventListener("keydown", function (event) {
            var scrim = document.getElementById("ai-chat-scrim");
            if (event.key === "Escape" && scrim && !scrim.hidden) {
                aiChatClose();
                event.stopImmediatePropagation();
            }
        });
        document.addEventListener("keydown", keyboardShortcuts);

        document.querySelectorAll('.sidebar a, .sidebar button[type="submit"]').forEach(function (element) {
            element.addEventListener("click", function () {
                if (drawerMedia.matches) {
                    closeSidebar({ restoreFocus: false });
                }
            });
        });

        configureCsrf();
        registerServiceWorker();
    }

    window.toggleTheme = toggleTheme;
    window.openSidebar = openSidebar;
    window.closeSidebar = closeSidebar;
    window.toggleSidebar = toggleSidebar;
    window.aiChatOpen = aiChatOpen;
    window.aiChatClose = aiChatClose;
    window.aiChatBeforeReq = aiChatBeforeRequest;
    window.aiChatAfterReq = aiChatAfterRequest;

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();
