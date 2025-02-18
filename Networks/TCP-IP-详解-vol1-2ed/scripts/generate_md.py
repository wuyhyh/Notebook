import os
import sys

# 《TCP/IP 详解 第一卷（第二版）》的目录
chapters = [
    "第1章 概述",
    "第2章 Internet 地址结构",
    "第3章 链路层",
    "第4章 地址解析协议",
    "第5章 Internet 协议",
    "第6章 系统配置：DHCP 和自动配置",
    "第7章 防火墙和网络地址转换",
    "第8章 ICMPv4 和 ICMPv6: Internet 控制报文协议",
    "第9章 广播和本地组播（IGMP 和 MLD）",
    "第10章 用户数据报协议和 IP 分片",
    "第11章 名字解析和域名系统",
    "第12章 TCP：传输控制协议（初步）",
    "第13章 TCP 连接管理",
    "第14章 TCP 超时与重传",
    "第15章 TCP 数据流与窗口管理",
    "第16章 TCP 拥塞控制",
    "第17章 TCP 保活机制",
    "第18章 安全：可扩展身份认证协议、IP 安全协议、传输层安全、DNS 安全、域名密钥识别邮件",
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
    readme.write("# TCP/IP 详解 第一卷（第二版）\n\n")
    readme.write("## 章节目录\n\n")

    for chapter in chapters:
        md_filename = chapter.replace(" ", "_").replace("/", "-") + ".md"
        readme.write(f"- [{chapter}](./chapters/{md_filename})\n")

print("✅ README.md 生成完成！")
