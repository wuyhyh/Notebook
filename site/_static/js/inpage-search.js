(function () {
    /* ---- 将“页面内搜索框”插到右侧 toc 区域顶部 ---- */
    function insertBox() {
        // Furo 右侧目录容器常见类名：.toc-sticky 或 .toc-tree-container
        const tocSticky =
            document.querySelector(".toc-sticky") ||
            document.querySelector(".toc-tree-container");

        if (!tocSticky || document.getElementById("inpage-search-box")) return;

        const box = document.createElement("div");
        box.id = "inpage-search-box";
        box.innerHTML = `
      <input id="inpage-search-input" type="search" placeholder="页面内搜索…（回车/上下键跳转）" />
      <div id="inpage-search-status" style="font-size:.85rem;margin-top:.35rem;opacity:.75"></div>
    `;
        tocSticky.prepend(box);

        wireSearch(
            document.getElementById("inpage-search-input"),
            document.getElementById("inpage-search-status")
        );
    }

    /* ---- 为当前文档内容做“页面内查找 + 高亮 + 定位” ---- */
    function wireSearch(input, status) {
        const article = document.querySelector("article");
        if (!article) return;

        let currentIndex = -1;
        let hits = [];

        function clearMarks() {
            article.querySelectorAll("mark.__inpage_hit").forEach((m) => {
                const parent = m.parentNode;
                parent.replaceChild(document.createTextNode(m.textContent), m);
                parent.normalize();
            });
        }

        function highlightAll(q) {
            clearMarks();
            hits = [];
            currentIndex = -1;
            if (!q) {
                status.textContent = "";
                return;
            }
            const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT, {
                acceptNode: (node) => {
                    const s = node.nodeValue.trim();
                    return s ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
                },
            });

            const regex = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");

            while (walker.nextNode()) {
                const node = walker.currentNode;
                const m = node.nodeValue.match(regex);
                if (!m) continue;

                // 分片替换为 <mark>
                const frag = document.createDocumentFragment();
                let lastIndex = 0;
                node.nodeValue.replace(regex, (match, offset) => {
                    const before = node.nodeValue.slice(lastIndex, offset);
                    if (before) frag.appendChild(document.createTextNode(before));
                    const mark = document.createElement("mark");
                    mark.className = "__inpage_hit";
                    mark.textContent = match;
                    frag.appendChild(mark);
                    hits.push(mark);
                    lastIndex = offset + match.length;
                });
                const after = node.nodeValue.slice(lastIndex);
                if (after) frag.appendChild(document.createTextNode(after));
                node.parentNode.replaceChild(frag, node);
            }

            status.textContent = hits.length ? `命中 ${hits.length} 项` : "无结果";
            if (hits.length) jumpTo(0);
        }

        function jumpTo(idx) {
            if (!hits.length) return;
            // 取消上一个 focus 效果
            article.querySelectorAll("mark.__inpage_hit.__focus").forEach((m) =>
                m.classList.remove("__focus")
            );

            currentIndex = (idx + hits.length) % hits.length;
            const el = hits[currentIndex];
            el.classList.add("__focus");
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            status.textContent = `第 ${currentIndex + 1} / ${hits.length} 项（↑/↓ 切换）`;
        }

        input.addEventListener("input", (e) => {
            highlightAll(e.target.value.trim());
        });

        input.addEventListener("keydown", (e) => {
            if (!hits.length) return;
            if (e.key === "Enter" || e.key === "ArrowDown") {
                e.preventDefault();
                jumpTo(currentIndex + 1);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                jumpTo(currentIndex - 1);
            } else if (e.key === "Escape") {
                input.value = "";
                highlightAll("");
            }
        });

        // 当切换页面时（单页应用式导航），重新挂载
        document.addEventListener("DOMContentLoaded", () => highlightAll(input.value.trim()));
    }

    // 初次挂载
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", insertBox);
    } else {
        insertBox();
    }
})();
