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
> 使用 CLion 的编辑器打开一个 .py 文件的时候会提示安装一个虚拟解释器环境，安装之后会创建一个 `.venv`目录
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
sh build.sh
```

## 离线阅读文档

文件浏览器上双击 [site/index.html](./site/index.html) 即可离线阅读

## 项目维护

增加目录和 md 文档，然后新增和修改 `index.rst` 配置文件

## 版本管理和本地备份

如果要将项目部署在一个不连外网的机器上时，我们需要进行本地备份。

### 1. 创建本地备份仓库

在安装了 Git 的 windows 电脑上，
执行备份命令会在 C 盘用户目录下创建一个 `git-backup` 的备份目录并写入当前项目的所有数据，
之后这个目录将作为一个本地的远程仓库，支持备份和版本管理功能。

> 通用本地备份脚本（Git Bash / Linux / macOS 皆可用）
> 功能：
> 1) 在当前项目的使用者的用户目录(~)下创建 `~/git-backups/<project>.git` 裸仓库
> 2) 将该裸仓库添加为远程 `"backup"`（已存在则更新 URL）
> 3) 首次推送所有分支与标签到该本地远程
> 4) 输出发生的操作与结果说明
>
> 用法：在项目根目录执行 `./backup.sh`
> 先决条件：当前目录必须是一个已有提交的 Git 仓库

### 2. 版本管理

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

