# Notebook

## 构建文档为网页

### 1. 激活 venv python 环境

需要先安装 `python`以及文档渲染主题，相关的依赖在 [requirements.txt](./requirements.txt) 中

```bash
python -m pip install -r requirements.txt
```

如果速度慢使用国内镜像源：

```shell
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

> 在 macOS 上构建之前需要先激活虚拟环境
> 使用 CLion 的编辑器打开一个 [conf.py](./docs/source/conf.py) 文件的时候会提示安装一个虚拟解释器环境，安装之后会创建一个
`.venv`目录
>
> 激活环境并安装包:
>
> ```bash
> source .venv/bin/activate
> python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
> ```
> ```bash
> deactivate # 关闭已激活的环境，在 build 之前不要关闭
> ```

### 2. 开始构建

[build.sh](./build.sh) 会基于当前的 `doc/source` 目录下的文件进行构建

```shell
./build.sh
```

## 离线阅读文档

> 一键预览脚本
> ```text
> ./preview.sh               # 默认 8000 端口
> PORT=9000 ./preview.sh     # 自定义端口
> SITE_DIR=_build/html ./preview.sh   # 如果你把产物放在 _build/html
> ```

```bash
./preview.sh
```

或者在文件浏览器上双击 [site/index.html](./site/index.html) 即可离线阅读

## 项目维护

增加目录和 md 文档，然后新增和修改 `index.rst` 配置文件

## 版本管理

配置完成后，本机上的远程仓库默认名为 `origin`，使用 `push` `pull` 实现数据传送

```text
git push origin master
git pull origin master
```

创建带注释的标签：

```text
git tag -a stable1.0 -m "Stable version 1.0 release"
```

推送所有本地标签：

```text
git push origin --tags
```

查看标签

```text
git tag
git show stable1.0
```

## 部署网页到 Linux 服务器上

应该先修改 [re_deployment.sh](./re_deployment.sh) 中的配置信息

```text
./re_deployment.sh
```