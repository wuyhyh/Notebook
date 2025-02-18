import os
import sys

# 《Linux 设备驱动程序（第三版）》的目录
chapters = [
    "第1章 设备驱动程序简介",
    "第2章 构造和运行模块",
    "第3章 字符设备驱动程序",
    "第4章 调试技术",
    "第5章 并发和竞态",
    "第6章 高级字符驱动程序操作",
    "第7章 时间、延迟和延缓操作",
    "第8章 分配内存",
    "第9章 与硬件通信",
    "第10章 中断处理",
    "第11章 内核的数据类型",
    "第12章 PCI 驱动程序",
    "第13章 USB 驱动程序",
    "第14章 Linux 设备模型",
    "第15章 内存映射和 DMA",
    "第16章 块设备驱动程序",
    "第17章 网络设备驱动程序",
    "第18章 TTY 驱动程序",
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
    readme.write("# Linux 设备驱动程序（第三版）\n\n")
    readme.write("## 章节目录\n\n")

    for chapter in chapters:
        md_filename = chapter.replace(" ", "_").replace("/", "-") + ".md"
        readme.write(f"- [{chapter}](./chapters/{md_filename})\n")

print("✅ README.md 生成完成！")
