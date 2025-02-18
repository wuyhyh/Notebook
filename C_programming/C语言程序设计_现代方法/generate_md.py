import os

# 章节列表
chapters = [
    "第1章  C语言概述",
    "第2章  C语言基本概念",
    "第3章  格式化输入/输出",
    "第4章  表达式",
    "第5章  选择语句",
    "第6章  循环语句",
    "第7章  基本类型",
    "第8章  数组",
    "第9章  函数",
    "第10章  程序组织",
    "第11章  指针",
    "第12章  指针与数组",
    "第13章  字符串",
    "第14章  预处理器",
    "第15章  编写大型程序",
    "第16章  结构、共用体和枚举",
    "第17章  指针的高级应用",
    "第18章  声明",
    "第19章  程序设计",
    "第20章  底层程序设计",
    "第21章  标准库",
    "第22章  输入/输出",
    "第23章  库对数值和字符数据的支持",
    "第24章  错误处理",
    "第25章  国际化特性",
    "第26章  其他库函数",
    "第27章  C99对数学计算的新增支持",
    "第28章  C1X新增的多线程和原子操作的支持",
]

# 当前目录
current_dir = os.getcwd()

# 生成 Markdown 文件
for chapter in chapters:
    filename = chapter.replace(" ", "_").replace("/", "").replace("：", "") + ".md"
    filepath = os.path.join(current_dir, filename)

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {chapter}\n\n")
            f.write(f"## 概述\n\n")
            f.write(f"本章节介绍了 {chapter} 的相关内容。\n\n")
            f.write("## 详细内容\n\n")

print("✅ 所有 Markdown 文件已生成！")

# 生成 README.md
readme_path = os.path.join(current_dir, "README.md")

with open(readme_path, "w", encoding="utf-8") as readme:
    readme.write("# C语言程序设计：现代方法（第二版）\n\n")
    readme.write("## 章节目录\n\n")
    readme.write("```\n")
    readme.write("C_Programming_A_Modern_Approach_2nd_Edition/\n")

    for chapter in chapters:
        md_filename = chapter.replace(" ", "_").replace("/", "").replace("：", "") + ".md"
        readme.write(f"├── [{chapter}](./{md_filename})\n")

    readme.write("```\n")

print("✅ README.md 生成完成！")
