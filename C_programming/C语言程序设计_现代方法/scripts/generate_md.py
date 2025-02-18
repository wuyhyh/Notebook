import os
import sys

# 章节列表
chapters = [
    "第1章 C语言概述",
    "第2章 C语言基本概念",
    "第3章 格式化输入/输出",
    "第4章 表达式",
    "第5章 选择语句",
    "第6章 循环语句",
    "第7章 基本类型",
    "第8章 数组",
    "第9章 函数",
    "第10章 程序组织",
    "第11章 指针",
    "第12章 指针与数组",
    "第13章 字符串",
    "第14章 预处理器",
    "第15章 编写大型程序",
    "第16章 结构、共用体和枚举",
    "第17章 指针的高级应用",
    "第18章 声明",
    "第19章 程序设计",
    "第20章 底层程序设计",
    "第21章 标准库",
    "第22章 输入/输出",
    "第23章 库对数值和字符数据的支持",
    "第24章 错误处理",
    "第25章 国际化特性",
    "第26章 其他库函数",
    "第27章 C99对数学计算的新增支持",
    "第28章 C1X新增的多线程和原子操作的支持",
]

# 附录列表
appendices = [
    "附录A C语言运算符",
    "附录B C1X与C99的比较",
    "附录C C99与C89的比较",
    "附录D C89与经典C的比较",
    "附录E 标准库函数",
    "附录F ASCII字符集",
]

# 获取当前脚本的根目录（scripts 目录的上一级）
script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts 目录
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

# 生成 Markdown 文件（包括章节和附录）
all_sections = chapters + appendices  # 组合章节和附录

for section in all_sections:
    filename = section.replace(" ", "_").replace("/", "-") + ".md"
    filepath = os.path.join(chapters_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {section}\n\n")
        f.write(f"## 概述\n\n")
        f.write(f"本章节介绍了 {section} 的相关内容。\n\n")
        f.write("## 详细内容\n\n")

print("✅ 所有 Markdown 文件已生成！")

# 生成 `README.md`
readme_path = os.path.join(project_root, "README.md")

with open(readme_path, "w", encoding="utf-8") as readme:
    readme.write("# C语言程序设计：现代方法（第二版）\n\n")
    readme.write("## 章节目录\n\n")

    for chapter in chapters:
        md_filename = chapter.replace(" ", "_").replace("/", "-") + ".md"
        readme.write(f"- [{chapter}](./chapters/{md_filename})\n")

    readme.write("\n## 附录\n\n")

    for appendix in appendices:
        md_filename = appendix.replace(" ", "_").replace("/", "-") + ".md"
        readme.write(f"- [{appendix}](./chapters/{md_filename})\n")

print("✅ README.md 生成完成！")
