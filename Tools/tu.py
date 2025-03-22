import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 创建画布和轴
fig, ax = plt.subplots(figsize=(10, 8))
ax.axis('off')

# 节点内容
nodes = {
    "A": "start_kernel",
    "B": "setup_arch",
    "C": "e820__memblock_setup\n(memblock 添加物理内存段)",
    "D": "mm_core_init",
    "E": "build_all_zonelists\n(建立 zone 链表)",
    "F": "mem_init",
    "G": "memmap_init_zone\n(初始化每个 struct page)",
    "H": "__init_single_page\n(初始化页框结构)",
    "I": "__free_pages\n将空闲页加入伙伴系统",
    "J": "__free_pages_ok",
    "K": "__free_one_page\n(加入 free_area[order])"
}

# 节点位置 (x, y)
positions = {
    "A": (5, 10),
    "B": (5, 9),
    "C": (5, 8),
    "D": (5, 7),
    "E": (5, 6),
    "F": (5, 5),
    "G": (5, 4),
    "H": (3.5, 3),
    "I": (6.5, 3),
    "J": (6.5, 2),
    "K": (6.5, 1)
}

# 绘制节点
for key, text in nodes.items():
    x, y = positions[key]
    ax.text(x, y, text, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightblue'))

# 绘制箭头
arrows = [
    ("A", "B"), ("B", "C"), ("A", "D"), ("D", "E"),
    ("A", "F"), ("F", "G"), ("G", "H"), ("G", "I"),
    ("I", "J"), ("J", "K")
]

for start, end in arrows:
    x1, y1 = positions[start]
    x2, y2 = positions[end]
    ax.annotate("",
                xy=(x2, y2), xycoords='data',
                xytext=(x1, y1), textcoords='data',
                arrowprops=dict(arrowstyle="->", lw=1.5))

plt.title("Linux 启动时物理内存加入伙伴系统流程图", fontsize=14)
plt.tight_layout()
plt.show()

