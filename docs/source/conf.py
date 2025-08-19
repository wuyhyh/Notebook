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

# 关键：保持默认的相对路径输出，方便离线 file:// 直接打开
# 不要设置 html_baseurl（留空即可）

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    # 顶栏右侧：主题切换 + GitHub/主页等图标（按需）
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    # 右侧“本页目录”
    "secondary_sidebar_items": ["page-toc"],
    # 左侧导航展开层级
    "show_nav_level": 2,       # 初始展开到2级
    "show_toc_level": 2,       # 右侧目录显示到2级
    # 颜色（接近 openEuler 风格）
    "primary_color": "blue",
    "accent_color": "blue",
}

# 站点信息（可选）
html_logo = "_static/logo.png"            # 如果有
html_favicon = "_static/favicon.ico"      # 如果有

# 自定义样式（放在 _static/css/custom.css）
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# 打开搜索框（pydata 顶栏自带，会调用 Sphinx 内置搜索）
# 无需额外插件/JS

