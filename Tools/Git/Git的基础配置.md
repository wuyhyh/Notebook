# 使用 Git 足够的特性

简单的设计可能就是最好的设计，就像铲子被发明和使用了几千年。

但是 Git 这个工具有些功能强大且复杂没用。

---

## Git 安装与初始化

- 在 Fedora 上安装 Git

```shell
sudo dnf install git -y
```

- 在 Ubuntu 上安装 Git

```shell
sudo apt install git -y
```

- 配置用户名和邮箱

```shell
git config --global user.name <name>
git config --global user.email <email_address>
```

比如：

```shell
git config --global user.name "wuyhyh"
git config --global user.email wuyhyh@gmail.com
```

- 查询配置信息

```shell
git config --list
```

配置信息是可以在子目录下多次新建的，配置信息保存在文件`.gitconfig下`。子目录的配置会覆盖顶层目录的配置。

- 在服务器的`~/.ssh`目录下生成公钥和私钥

```shell
cd ~/.ssh;ssh-keygen
```

- 复制公钥到 github 端

## Git 的基本用法

### 1. 创建 Git 仓库

- 在现有的项目根目录下进行初始化

```shell
git init
```

- Clone 远程仓库

```shell
git clone <URL>
```

你还可以修改 clone 下来的仓库的默认名称，但是没有什么卵用。

### 2. Git 的基本模型

Git 本质上是一个按内容寻址的文件系统。所有 Git 中的对象都是通过20个字节，160个`ASCII`字符的`sha-1`的序列来索引的。
不用担心这个索引会出现冲突，这个地址空间非常的大。

#### Git 中有三个区域:

- 已经 commit 的文件，被压缩后放置在`.git`目录下。`HEAD`是一个指针，指向最后定型的提交的`sha-1`值.
- 已经 index 的文件，也就是已经暂存的文件，这些文件可以理解为登记造册的文件，下一次提交会把他们放入commit区。
- 工作区，这个区域的文件可以是刚刚新增的，亦可以是以前就在的，以前就有的文件可能是被修改了的，也可以是没有没修改过的。
  所以就有了tracked untracked modified unmodified 的概念。

查看当前文件的状态

```shell
git status
```

把文件从工作区域移动到暂存区

```shell
git add <file_name or dir_name>
git add . # 当前 tracked 的所有文件
```

相反的，可以将文件从暂存区移动回工作区

```shell
git reset HEAD~
```

放弃对某个文件或者所有文件的修改，还原到上次`commit`的状态

```shell
git checkout -- <filename>
```

还可以查看一下现在暂存区的文件和已经持久化的文件有什么区别，也就是下一次提交会产生什么后果：

```shell
git diff
```

提交代码，进行持久化

```shell
git commit -m <message>
```

不在跟踪某个文件

```shell
git rm --cached <file_name>
```

删除文件还是交给sh中的 rm 去做吧。

查看历史提交

```shell
git log
git log --pretty=oneline # 有用但是那么长，傻逼
```

如果刚刚提交的内容不满意，可以修改`commit message`，还可以追加文件

```shell
git commit --amend
```

如果你已经把`commit`推送到了远端仓库，那么再次推送，要加上`force`

```shell
git push <remote_rep_name> <remote_branch_name> -f
```

比如

```shell
git push origin master -f
```

### 远程仓库的使用

使用`git clone`得到的仓库默认其远程仓库是`origin`

显示远程仓库

```shell
git remote
git remote -v # 还会显示 URL
```

远程仓库的添加、删除、查看、重命名

```shell
git remote add <rep_name> <url>
git remote rm <rep_name>
git remote show <rep_name>
git remote rename <old_name> <new_name>
```

从远程仓库拉去数据，`fetch`只会取回本地没有的数据，不会修改本地工作目录下的数据。

```shell
git fetch <remote_rep_name>
```

把数据推送到远端

```shell
git push <remote_rep_name> <remote_branch_name>
```

比如

```shell
git push origin master
```

## Git 的分支特性

## 重要的 Git 命令



