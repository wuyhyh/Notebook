# -- 基本项 -----------------------------------------------------------------
project = "蓝焰的 Notebook"
extensions = [
    "myst_parser",  # 允许使用 Markdown（MyST）
]
myst_enable_extensions = [
    "linkify", "attrs", "deflist", "tasklist", "colon_fence", "dollarmath"
]

# 主题：Read the Docs 风格（离线搜索友好）
# html_theme = "sphinx_rtd_theme"

# 静态资源目录（可选）
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/inpage-search.js"]

# 关键：保持默认的相对路径输出，方便离线 file:// 直接打开
# 不要设置 html_baseurl（留空即可）

html_theme = "furo"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#5aa7e0",
        "color-brand-content": "#2b6cb0",
        # 可继续调：
        # "color-background-primary": "#ffffff",
        # "color-background-secondary": "#f6fbff",
        # "color-foreground-primary": "#0b2540",
    },
    # "dark_css_variables": { ... }  # 如需暗色方案
}
