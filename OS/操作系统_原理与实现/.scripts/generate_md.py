import os
import sys

# 《操作系统：原理与实现》的14章目录
chapters = [
    "第1章 操作系统概述",
    "第2章 操作系统结构",
    "第3章 硬件环境与软件抽象",
    "第4章 虚拟内存管理",
    "第5章 物理内存管理",
    "第6章 进程与线程",
    "第7章 处理器调度",
    "第8章 进程间通信",
    "第9章 并发与同步",
    "第10章 同步原语的实现",
    "第11章 文件系统",
    "第12章 文件系统崩溃一致性",
    "第13章 设备管理",
    "第14章 系统虚拟化",
]

# 获取当前脚本的根目录（.scripts 目录的上一级）
script_dir = os.path.dirname(os.path.abspath(__file__))  # .scripts 目录
project_root = os.path.abspath(os.path.join(script_dir, ".."))  # 项目根目录

# 目标 `chapters/` 目录路径
chapters_dir = os.path.join(project_root, "chapters")

# 如果 `chapters/` 目录已存在，阻止运行脚本
if os.path.exists(chapters_dir):
    print("🚫 `chapters/` 目录已存在，脚本终止运行以避免覆盖已修改的文件！")
    print("❌ 如果需要重新生成，请手动删除 `chapters/` 目录后再运行此脚本。")
    sys.exit(1)  # 终止脚本执行

# 创建 `chapters/` 目录
os.makedirs(chapters_dir)

# 生成 Markdown 文件
for chapter in chapters:
    filename = chapter.replace(" ", "_").replace("/", "-") + ".md"
    filepath = os.path.join(chapters_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {chapter}\n\n")
        f.write(f"## 概述\n\n")
        f.write(f"本章节介绍了 {chapter} 的相关内容。\n\n")
        f.write("## 详细内容\n\n")

print("✅ 所有 Markdown 文件已生成！")

# 生成 `README.md`
readme_path = os.path.join(project_root, "README.md")

with open(readme_path, "w", encoding="utf-8") as readme:
    readme.write("# 操作系统：原理与实现\n\n")
    readme.write("## 章节目录\n\n")

    for chapter in chapters:
        md_filename = chapter.replace(" ", "_").replace("/", "-") + ".md"
        readme.write(f"- [{chapter}](./chapters/{md_filename})\n")

print("✅ README.md 生成完成！")
