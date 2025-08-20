# -- 基本项 -----------------------------------------------------------------
from importlib.util import source_hash

project = "蓝焰的notebook"

extensions = [
    "myst_parser",  # 允许使用 Markdown（MyST）
]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

myst_enable_extensions = [
    "linkify",  # 自动把 URL 变链接
    "deflist",
    "tasklist",
    "substitution",
    "colon_fence",  # ::: 提示框/指令围栏
    "dollarmath",  # $ 数学公式
    # 需要“属性”功能时，改用下面两个二选一（或都开）
    # "attrs_block",
    # "attrs_inline",
]

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    # 顶栏右侧：主题切换 + GitHub/主页等图标（按需）
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    # 右侧“本页目录”
    "secondary_sidebar_items": ["page-toc"],
    # 左侧导航展开层级
    "show_nav_level": 2,  # 初始展开到2级
    "show_toc_level": 2,  # 右侧目录显示到2级
}

# 站点信息（可选）
html_logo = "_static/logo.jpg"
html_favicon = "_static/logo.jpg"

# 自定义样式（放在 _static/css/custom.css）
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# 打开搜索框（pydata 顶栏自带，会调用 Sphinx 内置搜索）
