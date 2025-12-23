(() => {
    const KEY = "wyh_sidebar_widths_v2";

    // 你可以按手感改这四个限制
    const MIN_NAV = 200, MAX_NAV = 520;   // 左侧
    const MIN_TOC = 220, MAX_TOC = 620;   // 右侧

    const root = document.documentElement;

    function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
    function setVar(name, valuePx) { root.style.setProperty(name, valuePx + "px"); }

    function load() {
        try {
            const raw = localStorage.getItem(KEY);
            if (!raw) return;
            const obj = JSON.parse(raw);
            if (obj.nav) setVar("--wyh-nav-width", obj.nav);
            if (obj.toc) setVar("--wyh-toc-width", obj.toc);
        } catch (e) {}
    }

    function save(navW, tocW) {
        try {
            localStorage.setItem(KEY, JSON.stringify({ nav: navW, toc: tocW }));
        } catch (e) {}
    }

    let hLeft, hRight;

    function ensureHandles() {
        if (!hLeft) {
            hLeft = document.createElement("div");
            hLeft.className = "wyh-drag-handle wyh-drag-left";
            document.body.appendChild(hLeft);
            attachDrag(hLeft, "nav");
        }
        if (!hRight) {
            hRight = document.createElement("div");
            hRight.className = "wyh-drag-handle wyh-drag-right";
            document.body.appendChild(hRight);
            attachDrag(hRight, "toc");
        }
    }

    function findSidebars() {
        const nav = document.querySelector(".bd-sidebar-primary");
        const toc = document.querySelector(".bd-sidebar-secondary");
        // 有些页面/窗口宽度下右侧 TOC 可能被折叠
        return { nav, toc };
    }

    function updateHandlePositions() {
        const { nav, toc } = findSidebars();
        if (!nav) return;

        const navRect = nav.getBoundingClientRect();

        // 左手柄：贴在左侧栏右边界
        if (hLeft) {
            hLeft.style.left = (navRect.right - 5) + "px";
            hLeft.style.display = "block";
        }

        // 右手柄：贴在右侧栏左边界（如果右侧存在）
        if (hRight) {
            if (!toc || toc.offsetParent === null) {
                hRight.style.display = "none";
            } else {
                const tocRect = toc.getBoundingClientRect();
                hRight.style.left = (tocRect.left - 5) + "px";
                hRight.style.display = "block";
            }
        }
    }

    function attachDrag(handle, which) {
        handle.addEventListener("mousedown", (e) => {
            if (e.button !== 0) return;
            e.preventDefault();

            const { nav, toc } = findSidebars();
            if (!nav) return;
            if (which === "toc" && (!toc || toc.offsetParent === null)) return;

            const startX = e.clientX;
            const startNav = Math.round(nav.getBoundingClientRect().width);
            const startToc = toc ? Math.round(toc.getBoundingClientRect().width) : 0;

            document.body.classList.add("wyh-resizing");

            function onMove(ev) {
                const dx = ev.clientX - startX;

                if (which === "nav") {
                    const navW = clamp(startNav + dx, MIN_NAV, MAX_NAV);
                    setVar("--wyh-nav-width", navW);
                } else {
                    // 右边界向右拖 => TOC 变窄；向左拖 => TOC 变宽
                    const tocW = clamp(startToc - dx, MIN_TOC, MAX_TOC);
                    setVar("--wyh-toc-width", tocW);
                }

                // 位置跟着变
                updateHandlePositions();
            }

            function onUp() {
                document.removeEventListener("mousemove", onMove);
                document.removeEventListener("mouseup", onUp);
                document.body.classList.remove("wyh-resizing");

                const { nav: nav2, toc: toc2 } = findSidebars();
                const navW = nav2 ? Math.round(nav2.getBoundingClientRect().width) : startNav;
                const tocW = (toc2 && toc2.offsetParent !== null) ? Math.round(toc2.getBoundingClientRect().width) : startToc;
                save(navW, tocW);
            }

            document.addEventListener("mousemove", onMove);
            document.addEventListener("mouseup", onUp);
        });
    }

    function boot() {
        load();
        ensureHandles();
        updateHandlePositions();

        window.addEventListener("resize", () => updateHandlePositions());

        // pydata 有些元素会后插入，观察 DOM 变化后重新定位手柄
        const obs = new MutationObserver(() => updateHandlePositions());
        obs.observe(document.documentElement, { childList: true, subtree: true });
    }

    window.addEventListener("DOMContentLoaded", boot);
    window.addEventListener("load", boot);
})();
