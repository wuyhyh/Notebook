# -- 基本项 -----------------------------------------------------------------
project = "蓝夜的notebook"

extensions = [
    "myst_parser",  # 允许使用 Markdown（MyST）
    "sphinx_copybutton",
]

# 复制按钮应用到哪些代码块（默认就能覆盖大多数情况）
# 加了 :not(.no-copybutton) 方便你对个别块禁用按钮
copybutton_selector = "div.highlight pre:not(.no-copybutton)"

# 复制时去掉“提示符”（正则表达式）
# 覆盖常见的：$、#、>>>、...、PowerShell 的 PS>、以及带虚拟环境/箭头的 zsh 提示
# 复制时去掉“提示符”（不再把 # 当提示符）
copybutton_prompt_is_regexp = True
copybutton_prompt_text = (
    r'^\s*('
    r'\$\s'                # 普通用户的 $ 提示符
    r'|>>> '               # Python 交互式
    r'|\.\.\. '            # Python 续行
    r'|PS> '               # PowerShell
    r'|\(.+\)\s*➜ '        # 某些 zsh/oh-my-zsh 主题
    r'|\(.+\)\s*[\w@.-]+:[^$>]+[$] '  # 仅去掉以 $ 结尾的路径提示符（不再匹配 #）
    r')'
)

# 可选：如果你示例里用到反斜杠续行，复制时自动合并成一行
# copybutton_line_continuation_character = "\\"

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
    # 顶栏最多显示多少个链接，超过的才进 “More”
    "header_links_before_dropdown": 10,
}

# 站点信息（可选）
html_logo = "_static/logo.jpg"
html_favicon = "_static/logo.jpg"

# 自定义样式（放在 _static/css/custom.css）
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/resize.js"]

# 打开搜索框（pydata 顶栏自带，会调用 Sphinx 内置搜索）
