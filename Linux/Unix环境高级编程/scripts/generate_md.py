import os
import sys

# 《UNIX 环境高级编程（第3版）》的完整目录（共 21 章）
chapters = [
    "第1章 UNIX基础知识",
    "第2章 UNIX标准及实现",
    "第3章 文件I/O",
    "第4章 文件和目录",
    "第5章 标准I/O库",
    "第6章 系统数据文件和信息",
    "第7章 进程环境",
    "第8章 进程控制",
    "第9章 进程关系",
    "第10章 信号",
    "第11章 线程",
    "第12章 线程控制",
    "第13章 守护进程",
    "第14章 高级I/O",
    "第15章 进程间通信",
    "第16章 网络IPC：套接字",
    "第17章 高级进程间通信",
    "第18章 终端I/O",
    "第19章 伪终端",
    "第20章 数据库函数",
    "第21章 与网络打印机通信",
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
    readme.write("# UNIX 环境高级编程（第3版）\n\n")
    readme.write("## 章节目录\n\n")

    for chapter in chapters:
        md_filename = chapter.replace(" ", "_").replace("/", "-") + ".md"
        readme.write(f"- [{chapter}](./chapters/{md_filename})\n")

print("✅ README.md 生成完成！")
