# Notebook

## 构建文档为网页

需要先安装 `python`以及文档渲染主题：

```shell
pip install sphinx myst-parser pydata-sphinx-theme
```

> 在 macOS 上的 CLion 需要先激活虚拟环境
> 编辑器打开一个 .py 文件的时候会提示安装一个虚拟解释器环境，安装之后会创建一个 `.venv`目录，然后激活环境并安装包
>
> `source .venv/bin/activate`
>
> `pip install sphinx myst-parser pydata-sphinx-theme`

如果速度慢使用国内镜像源：

```shell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ sphinx myst-parser pydata-sphinx-theme 
```

构建网页

```shell
sh build.sh
```

build.sh 会基于当前的 source 文件进行重新构建，这是封装在 build.sh 中的命令：

```text
sphinx-build -b html docs/source site
```

## 离线阅读文档

文件浏览器上双击 [site/index.html](./site/index.html) 即可离线阅读

## 项目维护
