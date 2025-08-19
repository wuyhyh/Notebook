# -- 基本项 -----------------------------------------------------------------
project = "HPC 项目文档"
extensions = [
    "myst_parser",          # 允许使用 Markdown（MyST）
]
myst_enable_extensions = [
    "linkify", "attrs", "deflist", "tasklist", "colon_fence", "dollarmath"
]

# 主题：Read the Docs 风格（离线搜索友好）
html_theme = "sphinx_rtd_theme"

# 静态资源目录（可选）
html_static_path = ["_static"]

# 关键：保持默认的相对路径输出，方便离线 file:// 直接打开
# 不要设置 html_baseurl（留空即可）
